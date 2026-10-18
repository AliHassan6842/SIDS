"""Prepare a leakage-safe, unpromoted five-crop IP102 detection candidate.

The crop grouping follows the eight IP102 super-classes published by Wu et al.
Only COCO images containing one unique source category are retained, preventing
unselected pests from becoming unlabeled background. Raw/fetched data is read-only;
prepared images remain under the ignored ``ml/data/prepared`` tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError


DATASET_VERSION = "sids-multicrop-pest-detection-v2.0"
SEED = 20260823
DHASH_DISTANCE = 2
VAL_RATIO = 0.20
SOURCE = "ip102-coco-v1"
TAXONOMY_AUTHORITY = "https://openaccess.thecvf.com/content_CVPR_2019/papers/Wu_IP102_A_Large-Scale_Benchmark_Dataset_for_Insect_Pest_Recognition_CVPR_2019_paper.pdf"

# IP102 source category IDs and label strings are preserved in every manifest.
# Crop prefixes disambiguate generic labels such as "aphids" and "army worm".
CLASSES: dict[int, dict[str, str]] = {
    1: {"crop": "rice", "slug": "rice-leaf-roller", "source_label": "rice leaf roller"},
    11: {"crop": "rice", "slug": "rice-water-weevil", "source_label": "rice water weevil"},
    23: {"crop": "corn", "slug": "corn-borer", "source_label": "corn borer"},
    24: {"crop": "corn", "slug": "corn-army-worm", "source_label": "army worm"},
    25: {"crop": "corn", "slug": "corn-aphids", "source_label": "aphids"},
    28: {"crop": "wheat", "slug": "english-grain-aphid", "source_label": "english grain aphid"},
    35: {"crop": "wheat", "slug": "wheat-sawfly", "source_label": "wheat sawfly"},
    38: {"crop": "beet", "slug": "flea-beetle", "source_label": "flea beetle"},
    39: {"crop": "beet", "slug": "cabbage-army-worm", "source_label": "cabbage army worm"},
    40: {"crop": "beet", "slug": "beet-army-worm", "source_label": "beet army worm"},
    77: {"crop": "citrus", "slug": "icerya-purchasi", "source_label": "Icerya purchasi Maskell"},
    87: {"crop": "citrus", "slug": "prodenia-litura", "source_label": "Prodenia litura"},
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dhash(path: Path) -> int:
    with Image.open(path) as image:
        gray = image.convert("L").resize((9, 8))
        getter = getattr(gray, "get_flattened_data", gray.getdata)
        pixels = list(getter())
    value = 0
    for row in range(8):
        for column in range(8):
            offset = row * 9 + column
            value = (value << 1) | int(pixels[offset] > pixels[offset + 1])
    return value


def valid_image(path: Path) -> tuple[bool, tuple[int, int] | None, str | None]:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            dimensions = image.size
        if min(dimensions) <= 0:
            return False, None, "NON_POSITIVE_DIMENSION"
        return True, dimensions, None
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as error:
        return False, None, type(error).__name__


def load_split(root: Path, split: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    coco = json.loads(
        (root / "annotations" / f"instances_{split}.json").read_text(encoding="utf-8")
    )
    category_names = {int(row["id"]): str(row["name"]) for row in coco["categories"]}
    for source_id, definition in CLASSES.items():
        if category_names[source_id] != definition["source_label"]:
            raise ValueError(
                f"IP102 taxonomy drift for {source_id}: {category_names[source_id]!r}"
            )

    images = {int(row["id"]): row for row in coco["images"]}
    annotations_by_image: dict[int, list[dict[str, Any]]] = defaultdict(list)
    source_boxes: Counter[int] = Counter()
    source_images: dict[int, set[int]] = defaultdict(set)
    for annotation in coco["annotations"]:
        image_id = int(annotation["image_id"])
        category_id = int(annotation["category_id"])
        annotations_by_image[image_id].append(annotation)
        if category_id in CLASSES:
            source_boxes[category_id] += 1
            source_images[category_id].add(image_id)

    invalid_files: Counter[str] = Counter()
    skipped_dimension_mismatch = 0
    skipped_invalid_bbox = 0
    skipped_mixed_category = 0
    records = []
    for image_id, image in sorted(images.items()):
        annotations = annotations_by_image.get(image_id, [])
        category_ids = {int(annotation["category_id"]) for annotation in annotations}
        if not category_ids.intersection(CLASSES):
            continue
        if len(category_ids) != 1 or next(iter(category_ids)) not in CLASSES:
            skipped_mixed_category += 1
            continue
        source_id = next(iter(category_ids))
        path = root / split / image["file_name"]
        valid, dimensions, reason = valid_image(path)
        if not valid:
            invalid_files[reason or "UNKNOWN"] += 1
            continue
        declared_dimensions = (int(image["width"]), int(image["height"]))
        if dimensions != declared_dimensions:
            skipped_dimension_mismatch += 1
            continue
        invalid_bbox = False
        for annotation in annotations:
            x, y, width, height = map(float, annotation["bbox"])
            if (
                width <= 0
                or height <= 0
                or x < 0
                or y < 0
                or x + width > declared_dimensions[0] + 1e-6
                or y + height > declared_dimensions[1] + 1e-6
            ):
                invalid_bbox = True
                break
        if invalid_bbox:
            skipped_invalid_bbox += 1
            continue
        definition = CLASSES[source_id]
        records.append(
            {
                "source_split": split,
                "source_image_id": image_id,
                "file_name": image["file_name"],
                "path": path,
                "width": declared_dimensions[0],
                "height": declared_dimensions[1],
                "source_category_id": source_id,
                "source_label": definition["source_label"],
                "crop_slug": definition["crop"],
                "class_slug": definition["slug"],
                "annotations": annotations,
                "sha256": sha256_file(path),
                "dhash": dhash(path),
            }
        )

    return records, {
        "declared_images": len(images),
        "declared_annotations": len(coco["annotations"]),
        "selected_source_counts": {
            CLASSES[source_id]["slug"]: {
                "source_category_id": source_id,
                "annotated_images": len(source_images[source_id]),
                "boxes": source_boxes[source_id],
            }
            for source_id in CLASSES
        },
        "eligible_single_category_images": dict(
            sorted(Counter(record["class_slug"] for record in records).items())
        ),
        "skipped_mixed_or_unselected_category_images": skipped_mixed_category,
        "skipped_dimension_mismatch": skipped_dimension_mismatch,
        "skipped_invalid_bbox": skipped_invalid_bbox,
        "invalid_files": dict(sorted(invalid_files.items())),
    }


def remove_official_test_leakage(
    train: list[dict[str, Any]], test: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    test_sha = {record["sha256"] for record in test}
    test_dhashes = [(record["dhash"], record["file_name"]) for record in test]
    kept = []
    exact = []
    near = []
    for record in train:
        if record["sha256"] in test_sha:
            exact.append(record["file_name"])
            continue
        match = next(
            (
                (test_name, (record["dhash"] ^ test_hash).bit_count())
                for test_hash, test_name in test_dhashes
                if (record["dhash"] ^ test_hash).bit_count() <= DHASH_DISTANCE
            ),
            None,
        )
        if match:
            near.append(
                {
                    "train": record["file_name"],
                    "test": match[0],
                    "dhash_distance": match[1],
                }
            )
            continue
        kept.append(record)
    return kept, {
        "dhash_distance_threshold": DHASH_DISTANCE,
        "removed_exact_train_images": sorted(exact),
        "removed_near_duplicate_train_pairs": near,
    }


def component_split(
    records: list[dict[str, Any]], val_ratio: float
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    parents = list(range(len(records)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    for left in range(len(records)):
        for right in range(left + 1, len(records)):
            if (records[left]["dhash"] ^ records[right]["dhash"]).bit_count() <= DHASH_DISTANCE:
                union(left, right)

    components: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for index, record in enumerate(records):
        components[find(index)].append(record)
    ambiguous_components = [
        component
        for component in components.values()
        if len({record["class_slug"] for record in component}) != 1
    ]
    ambiguous_ids = {
        record["source_image_id"]
        for component in ambiguous_components
        for record in component
    }
    class_components: dict[str, list[list[dict[str, Any]]]] = defaultdict(list)
    for component in components.values():
        if any(record["source_image_id"] in ambiguous_ids for record in component):
            continue
        class_components[component[0]["class_slug"]].append(component)

    train, validation = [], []
    for class_slug, groups in sorted(class_components.items()):
        ordered = sorted(
            groups,
            key=lambda group: hashlib.sha256(
                f"{SEED}:{min(record['sha256'] for record in group)}".encode()
            ).hexdigest(),
        )
        target = max(1, round(sum(len(group) for group in ordered) * val_ratio))
        assigned = 0
        for group in ordered:
            if assigned < target:
                validation.extend(group)
                assigned += len(group)
            else:
                train.extend(group)
    evidence = {
        "dhash_distance_threshold": DHASH_DISTANCE,
        "perceptual_components": len(components),
        "multi_image_components": sum(len(group) > 1 for group in components.values()),
        "removed_cross_class_ambiguous_images": sorted(
            record["file_name"]
            for component in ambiguous_components
            for record in component
        ),
        "split_seed": SEED,
        "validation_ratio_target": val_ratio,
        "split_unit": "dHash-distance<=2 perceptual component",
    }
    return (
        sorted(train, key=lambda record: record["file_name"]),
        sorted(validation, key=lambda record: record["file_name"]),
        evidence,
    )


def link_or_copy(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def write_dataset(output: Path, splits: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    for split in splits:
        (output / "images" / split).mkdir(parents=True)
        (output / "labels" / split).mkdir(parents=True)
    model_index = {source_id: index for index, source_id in enumerate(CLASSES)}
    source_index = []
    for split, records in splits.items():
        for record in records:
            image_destination = output / "images" / split / record["file_name"]
            link_or_copy(record["path"], image_destination)
            label_lines = []
            for annotation in record["annotations"]:
                x, y, width, height = map(float, annotation["bbox"])
                label_lines.append(
                    f"{model_index[record['source_category_id']]} "
                    f"{(x + width / 2) / record['width']:.8f} "
                    f"{(y + height / 2) / record['height']:.8f} "
                    f"{width / record['width']:.8f} {height / record['height']:.8f}"
                )
            (output / "labels" / split / f"{Path(record['file_name']).stem}.txt").write_text(
                "\n".join(label_lines) + "\n", encoding="utf-8"
            )
            source_index.append(
                {
                    "prepared_split": split,
                    "source_split": record["source_split"],
                    "source_image_id": record["source_image_id"],
                    "file_name": record["file_name"],
                    "crop_slug": record["crop_slug"],
                    "source_category_id": record["source_category_id"],
                    "source_label": record["source_label"],
                    "class_slug": record["class_slug"],
                    "model_index": model_index[record["source_category_id"]],
                    "sha256": record["sha256"],
                    "dhash": f"{record['dhash']:016x}",
                    "boxes": len(record["annotations"]),
                }
            )

    yaml = [
        f"path: {output.resolve().as_posix()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "names:",
    ]
    for source_id, index in model_index.items():
        yaml.append(f"  {index}: {CLASSES[source_id]['slug']}")
    (output / "data.yaml").write_text("\n".join(yaml) + "\n", encoding="utf-8")
    (output / "source-index.json").write_text(
        json.dumps(source_index, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "split_images": {split: len(records) for split, records in splits.items()},
        "split_boxes": {
            split: sum(len(record["annotations"]) for record in records)
            for split, records in splits.items()
        },
        "class_split_images": {
            definition["slug"]: {
                split: sum(record["source_category_id"] == source_id for record in records)
                for split, records in splits.items()
            }
            for source_id, definition in CLASSES.items()
        },
        "class_split_boxes": {
            definition["slug"]: {
                split: sum(
                    len(record["annotations"])
                    for record in records
                    if record["source_category_id"] == source_id
                )
                for split, records in splits.items()
            }
            for source_id, definition in CLASSES.items()
        },
    }


def verify_no_split_leakage(output: Path) -> dict[str, Any]:
    index = json.loads((output / "source-index.json").read_text(encoding="utf-8"))
    by_split: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in index:
        by_split[record["prepared_split"]].append(record)
    comparisons = {}
    for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
        exact = sorted(
            {record["sha256"] for record in by_split[left]}
            & {record["sha256"] for record in by_split[right]}
        )
        near = []
        for left_record in by_split[left]:
            left_hash = int(left_record["dhash"], 16)
            for right_record in by_split[right]:
                distance = (left_hash ^ int(right_record["dhash"], 16)).bit_count()
                if distance <= DHASH_DISTANCE:
                    near.append(
                        {
                            "left": left_record["file_name"],
                            "right": right_record["file_name"],
                            "distance": distance,
                        }
                    )
        comparisons[f"{left}_vs_{right}"] = {
            "exact_sha_overlap": exact,
            "dhash_distance_lte_2_pairs": near,
        }
    if any(
        evidence["exact_sha_overlap"] or evidence["dhash_distance_lte_2_pairs"]
        for evidence in comparisons.values()
    ):
        raise RuntimeError("Prepared split leakage verification failed")
    return comparisons


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    source_root = workspace / "ml/data/fetched/ip102/extracted/ip102"
    output = workspace / "ml/data/prepared" / DATASET_VERSION
    report_path = workspace / "ml/reports" / f"{DATASET_VERSION}-preparation.json"
    registry_path = (
        workspace / "ml/dataset-registry/versions" / f"{DATASET_VERSION}.json"
    )

    source_train, train_audit = load_split(source_root, "train")
    source_test, test_audit = load_split(source_root, "test")
    leakage_safe_train, official_leakage = remove_official_test_leakage(
        source_train, source_test
    )
    train, validation, component_evidence = component_split(
        leakage_safe_train, VAL_RATIO
    )
    splits = {"train": train, "val": validation, "test": source_test}
    counts = write_dataset(output, splits)
    final_leakage = verify_no_split_leakage(output)

    report = {
        "schema_version": 1,
        "generated_at": "2026-08-23",
        "dataset_version": DATASET_VERSION,
        "status": "PREPARED_CANDIDATE_NOT_TRAINED_NOT_PROMOTED",
        "taxonomy_authority": TAXONOMY_AUTHORITY,
        "scope_rule": (
            "Five IP102 crop super-classes; 2-3 source-native labels per crop; every "
            "selected class has at least 100 official-train and 25 official-test images"
        ),
        "source_audit": {"train": train_audit, "test": test_audit},
        "leakage_control": {
            "official_train_vs_test": official_leakage,
            "train_validation_components": component_evidence,
            "final_verification": final_leakage,
        },
        "prepared_counts": counts,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "dataset_id": DATASET_VERSION,
        "task": "pest-detection",
        "status": "PREPARED_CANDIDATE_NOT_TRAINED_NOT_PROMOTED",
        "source": SOURCE,
        "taxonomy_authority": TAXONOMY_AUTHORITY,
        "crop_scope": sorted({definition["crop"] for definition in CLASSES.values()}),
        "classes": [
            {
                "model_index": index,
                "crop_slug": definition["crop"],
                "pest_id": definition["slug"],
                "source_category_id": source_id,
                "source_label": definition["source_label"],
                "scientific_name_mapping": None,
            }
            for index, (source_id, definition) in enumerate(CLASSES.items())
        ],
        "prepared_relative_path": f"ml/data/prepared/{DATASET_VERSION}",
        "prepared_counts": counts,
        "split_seed": SEED,
        "leakage_policy": "No SHA or dHash-distance<=2 component may cross a split",
        "preparation_report": f"ml/reports/{report_path.name}",
        "preparation_report_sha256": sha256_file(report_path),
        "license": {
            "ip102": "Academic use only; contact original author for other purposes",
            "redistribution": "Raw and prepared image material is not committed",
        },
        "promotion": {
            "allowed": False,
            "reason": "No v2 model has been trained or evaluated",
        },
    }
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"dataset": str(output), **counts}, indent=2))


if __name__ == "__main__":
    main()
