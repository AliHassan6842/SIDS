"""Materialize a reviewed batch into a new, never-promoted YOLO dataset version."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from collections import Counter
from pathlib import Path

from review_schema import load_config, resolve_bounded_image, sha256_file, validate_safe_token


def link_or_copy(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--base-dataset", type=Path, required=True)
    parser.add_argument("--sealed-batch", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--output-version", required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    validate_safe_token(args.output_version, "output_version")
    config = load_config(args.config)
    sealed = json.loads(args.sealed_batch.read_text(encoding="utf-8"))
    if sealed.get("status") != "SEALED_HUMAN_REVIEWED_NOT_MATERIALIZED":
        raise ValueError("Batch is not a sealed human-reviewed batch")
    validate_safe_token(str(sealed["batch_id"]), "batch_id")
    output = workspace / "ml/data/prepared" / args.output_version
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    shutil.copytree(args.base_dataset, output, copy_function=link_or_copy)
    source_index_path = output / "source-index.json"
    source_index = json.loads(source_index_path.read_text(encoding="utf-8"))
    existing_sha = {record["sha256"] for record in source_index}
    existing_dhash = {int(record["dhash"], 16) for record in source_index}
    class_index = {
        pest_id: index
        for index, pest_id in enumerate(
            pest
            for crop in config["allowed_crop_classes"].values()
            for pest in crop
        )
    }
    added = []
    for record in sealed["records"]:
        if record["review_status"] != "approved":
            continue
        validate_safe_token(str(record["sample_id"]), "sample_id")
        if record["image_sha256"] in existing_sha:
            raise ValueError(f"Reviewed image already exists in base dataset: {record['sample_id']}")
        reviewed_dhash = int(record["image_dhash"], 16)
        if any((reviewed_dhash ^ known).bit_count() <= 2 for known in existing_dhash):
            raise ValueError(
                f"Reviewed image is a near duplicate of the base public dataset: {record['sample_id']}"
            )
        image_path = resolve_bounded_image(args.image_root, record["image_path"])
        split = record["assigned_split"]
        file_name = f"AL_{sealed['batch_id']}_{record['sample_id']}_{record['image_sha256'][:12]}{image_path.suffix.lower()}"
        link_or_copy(image_path, output / "images" / split / file_name)
        lines = []
        for annotation in record["annotations"]:
            bbox = annotation["bbox"]
            lines.append(
                f"{class_index[annotation['pest_id']]} "
                f"{bbox['x'] + bbox['width'] / 2:.8f} "
                f"{bbox['y'] + bbox['height'] / 2:.8f} "
                f"{bbox['width']:.8f} {bbox['height']:.8f}"
            )
        (output / "labels" / split / f"{Path(file_name).stem}.txt").write_text(
            "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
        )
        item = {
            "prepared_split": split,
            "source_dataset": "human-reviewed-active-learning",
            "review_batch_id": sealed["batch_id"],
            "sample_id": record["sample_id"],
            "capture_group": record["capture_group"],
            "file_name": file_name,
            "crop_slug": record["crop_slug"],
            "class_slugs": [annotation["pest_id"] for annotation in record["annotations"]],
            "sha256": record["image_sha256"],
            "dhash": record["image_dhash"],
            "boxes": len(record["annotations"]),
            "reviewer_id": record["reviewer_id"],
            "reviewed_at": record["reviewed_at"],
        }
        source_index.append(item)
        added.append(item)
        existing_sha.add(record["image_sha256"])
        existing_dhash.add(reviewed_dhash)
    # copytree hard-links large prepared assets for efficiency. Replace metadata
    # rather than truncating the hard link, which would mutate the base index.
    source_index_path.unlink()
    source_index_path.write_text(json.dumps(source_index, indent=2) + "\n", encoding="utf-8")

    registry = {
        "schema_version": 1,
        "dataset_id": args.output_version,
        "task": "pest-detection",
        "status": "RETRAIN_CANDIDATE_NOT_TRAINED_NOT_PROMOTED",
        "base_dataset": config["base_dataset_version"],
        "sealed_review_batch": str(args.sealed_batch),
        "sealed_review_batch_sha256": sha256_file(args.sealed_batch),
        "prepared_relative_path": f"ml/data/prepared/{args.output_version}",
        "approved_images_added": len(added),
        "added_split_counts": dict(Counter(record["prepared_split"] for record in added)),
        "promotion": {
            "allowed": False,
            "reason": "Retrain and every configured evaluation gate require separate execution and approval",
        },
    }
    registry_path = workspace / "ml/dataset-registry/versions" / f"{args.output_version}.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "approved_images_added": len(added)}))


if __name__ == "__main__":
    main()
