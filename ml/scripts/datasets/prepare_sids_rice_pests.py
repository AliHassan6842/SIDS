"""Audit IP102/BAU-Insectv2 and prepare the bounded SIDS rice-pest dataset.

Large fetched and prepared assets stay under ``ml/data`` and are ignored by Git.
This script writes compact, reviewable evidence to ``ml/reports`` and
``ml/dataset-registry``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, UnidentifiedImageError


DATASET_VERSION = "sids-rice-pest-detection-v1.1"
SEED = 20260822
SELECTED_CLASSES = {
    1: "rice-leaf-roller",
    4: "asiatic-rice-borer",
    11: "rice-water-weevil",
}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def deterministic_key(value: str) -> str:
    return hashlib.sha256(f"{SEED}:{value}".encode("utf-8")).hexdigest()


def difference_hash(path: Path, size: int = 8) -> int:
    with Image.open(path) as image:
        gray = image.convert("L").resize((size + 1, size))
        getter = getattr(gray, "get_flattened_data", gray.getdata)
        pixels = list(getter())
    bits = 0
    for row in range(size):
        offset = row * (size + 1)
        for column in range(size):
            bits = (bits << 1) | int(pixels[offset + column] > pixels[offset + column + 1])
    return bits


def validate_image(path: Path) -> tuple[bool, str | None, tuple[int, int] | None]:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
        if width <= 0 or height <= 0:
            return False, "NON_POSITIVE_DIMENSION", None
        return True, None, (width, height)
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        return False, type(exc).__name__, None


def load_coco(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_coco_split(root: Path, split: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    coco = load_coco(root / "annotations" / f"instances_{split}.json")
    image_dir = root / split
    categories = {int(item["id"]): item["name"] for item in coco["categories"]}
    images = {int(item["id"]): item for item in coco["images"]}
    by_image: dict[int, list[dict[str, Any]]] = defaultdict(list)
    category_boxes: Counter[int] = Counter()
    category_images: dict[int, set[int]] = defaultdict(set)
    bbox_issues: Counter[str] = Counter()

    for annotation in coco["annotations"]:
        image_id = int(annotation["image_id"])
        category_id = int(annotation["category_id"])
        by_image[image_id].append(annotation)
        category_boxes[category_id] += 1
        category_images[category_id].add(image_id)
        image = images.get(image_id)
        if image is None:
            bbox_issues["UNKNOWN_IMAGE_ID"] += 1
            continue
        x, y, width, height = [float(value) for value in annotation["bbox"]]
        if width <= 0 or height <= 0:
            bbox_issues["NON_POSITIVE_AREA"] += 1
        if x < 0 or y < 0 or x + width > float(image["width"]) + 1e-6 or y + height > float(image["height"]) + 1e-6:
            bbox_issues["OUT_OF_BOUNDS"] += 1

    missing_files = 0
    invalid_files: Counter[str] = Counter()
    dimension_mismatches = 0
    selected_records: list[dict[str, Any]] = []
    for image_id, image in sorted(images.items()):
        image_path = image_dir / image["file_name"]
        if not image_path.is_file():
            missing_files += 1
            continue
        valid, reason, dimensions = validate_image(image_path)
        if not valid:
            invalid_files[reason or "UNKNOWN"] += 1
            continue
        if dimensions != (int(image["width"]), int(image["height"])):
            dimension_mismatches += 1
        annotations = by_image.get(image_id, [])
        category_ids = {int(item["category_id"]) for item in annotations}
        if len(category_ids) == 1 and next(iter(category_ids), None) in SELECTED_CLASSES:
            category_id = next(iter(category_ids))
            selected_records.append(
                {
                    "source_split": split,
                    "image_id": image_id,
                    "file_name": image["file_name"],
                    "path": image_path,
                    "width": int(image["width"]),
                    "height": int(image["height"]),
                    "source_category_id": category_id,
                    "class_slug": SELECTED_CLASSES[category_id],
                    "annotations": annotations,
                }
            )

    report = {
        "images_declared": len(images),
        "annotations_declared": len(coco["annotations"]),
        "categories_declared": len(categories),
        "missing_image_files": missing_files,
        "invalid_image_files": dict(sorted(invalid_files.items())),
        "dimension_mismatches": dimension_mismatches,
        "bbox_issues": dict(sorted(bbox_issues.items())),
        "category_counts": [
            {
                "source_category_id": category_id,
                "source_name": categories[category_id],
                "images": len(category_images[category_id]),
                "boxes": category_boxes[category_id],
            }
            for category_id in sorted(categories)
        ],
        "selected_single_class_images": Counter(record["class_slug"] for record in selected_records),
    }
    report["selected_single_class_images"] = dict(sorted(report["selected_single_class_images"].items()))
    return report, selected_records


def audit_bau(root: Path) -> dict[str, Any]:
    split_records: dict[str, list[Path]] = {}
    invalid: Counter[str] = Counter()
    class_counts: dict[str, dict[str, int]] = {}
    hashes: dict[str, list[str]] = defaultdict(list)
    dhashes: dict[int, list[str]] = defaultdict(list)

    for split in ("train", "test"):
        records: list[Path] = []
        split_counts: Counter[str] = Counter()
        for path in sorted((root / split).rglob("*")):
            if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            valid, reason, _ = validate_image(path)
            if not valid:
                invalid[reason or "UNKNOWN"] += 1
                continue
            records.append(path)
            split_counts[path.parent.name] += 1
            relative = path.relative_to(root).as_posix()
            hashes[sha256_file(path)].append(relative)
            dhashes[difference_hash(path)].append(relative)
        split_records[split] = records
        class_counts[split] = dict(sorted(split_counts.items()))

    exact_cross_split = []
    for paths in hashes.values():
        splits = {path.split("/", 1)[0] for path in paths}
        if len(splits) > 1:
            exact_cross_split.append(sorted(paths))
    dhash_cross_split = []
    for paths in dhashes.values():
        splits = {path.split("/", 1)[0] for path in paths}
        if len(splits) > 1:
            dhash_cross_split.append(sorted(paths))

    return {
        "annotation_type": "folder-level coarse class labels; no bounding boxes found",
        "class_counts": class_counts,
        "valid_images": {split: len(records) for split, records in split_records.items()},
        "invalid_images": dict(sorted(invalid.items())),
        "exact_duplicate_clusters_cross_split": len(exact_cross_split),
        "exact_duplicate_files_cross_split": sum(len(cluster) for cluster in exact_cross_split),
        "exact_duplicate_cluster_samples": exact_cross_split[:20],
        "identical_dhash_clusters_cross_split_review_required": len(dhash_cross_split),
        "identical_dhash_cluster_samples": dhash_cross_split[:20],
        "taxonomy_use": "supplementary rejection probe only; no BAU label is mapped to a supported species",
    }


def hamming_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def enrich_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched = []
    for record in records:
        item = dict(record)
        item["sha256"] = sha256_file(item["path"])
        item["dhash"] = difference_hash(item["path"])
        enriched.append(item)
    return enriched


def remove_test_leakage(
    train_records: list[dict[str, Any]], test_records: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    test_sha = {record["sha256"] for record in test_records}
    exact = [record for record in train_records if record["sha256"] in test_sha]
    exact_ids = {record["image_id"] for record in exact}
    candidates = [record for record in train_records if record["image_id"] not in exact_ids]
    near_ids: set[int] = set()
    near_pairs: list[dict[str, Any]] = []
    for train in candidates:
        for test in test_records:
            distance = hamming_distance(train["dhash"], test["dhash"])
            if distance <= 2:
                near_ids.add(train["image_id"])
                near_pairs.append(
                    {
                        "train": train["file_name"],
                        "test": test["file_name"],
                        "dhash_distance": distance,
                    }
                )
                break
    kept = [record for record in candidates if record["image_id"] not in near_ids]
    return kept, {
        "removed_exact_train_images": sorted(record["file_name"] for record in exact),
        "removed_near_duplicate_train_images": sorted(
            record["file_name"] for record in candidates if record["image_id"] in near_ids
        ),
        "near_duplicate_pairs": near_pairs,
        "dhash_distance_threshold": 2,
    }


def split_train_val(
    records: list[dict[str, Any]], val_ratio: float = 0.2
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
            if hamming_distance(records[left]["dhash"], records[right]["dhash"]) <= 2:
                union(left, right)

    components: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for index, record in enumerate(records):
        components[find(index)].append(record)
    ambiguous = [
        component
        for component in components.values()
        if len({record["class_slug"] for record in component}) > 1
    ]
    ambiguous_ids = {record["image_id"] for component in ambiguous for record in component}
    clean_components = [
        component
        for component in components.values()
        if not any(record["image_id"] in ambiguous_ids for record in component)
    ]

    train: list[dict[str, Any]] = []
    val: list[dict[str, Any]] = []
    by_class: dict[str, list[list[dict[str, Any]]]] = defaultdict(list)
    for component in clean_components:
        by_class[component[0]["class_slug"]].append(component)
    for class_slug, class_components in sorted(by_class.items()):
        ordered = sorted(
            class_components,
            key=lambda component: deterministic_key(min(record["sha256"] for record in component)),
        )
        total_images = sum(len(component) for component in ordered)
        val_target = max(1, round(total_images * val_ratio))
        val_images = 0
        for component in ordered:
            if val_images < val_target:
                val.extend(component)
                val_images += len(component)
            else:
                train.extend(component)
    split_evidence = {
        "dhash_distance_threshold": 2,
        "perceptual_components": len(components),
        "multi_image_components": sum(len(component) > 1 for component in components.values()),
        "removed_cross_class_ambiguous_images": sorted(
            record["file_name"] for component in ambiguous for record in component
        ),
        "split_unit": "perceptual component; no dHash-distance<=2 component crosses train/validation",
    }
    return (
        sorted(train, key=lambda item: item["file_name"]),
        sorted(val, key=lambda item: item["file_name"]),
        split_evidence,
    )


def link_or_copy(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def write_yolo_dataset(output_root: Path, splits: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError(f"Prepared output already exists: {output_root}")
    for split in splits:
        (output_root / "images" / split).mkdir(parents=True, exist_ok=False)
        (output_root / "labels" / split).mkdir(parents=True, exist_ok=False)

    class_index = {source_id: index for index, source_id in enumerate(SELECTED_CLASSES)}
    source_index: list[dict[str, Any]] = []
    for split, records in splits.items():
        for record in records:
            destination_image = output_root / "images" / split / record["file_name"]
            link_or_copy(record["path"], destination_image)
            label_path = output_root / "labels" / split / f"{Path(record['file_name']).stem}.txt"
            lines = []
            for annotation in record["annotations"]:
                x, y, width, height = [float(value) for value in annotation["bbox"]]
                x_center = (x + width / 2) / record["width"]
                y_center = (y + height / 2) / record["height"]
                normalized_width = width / record["width"]
                normalized_height = height / record["height"]
                lines.append(
                    f"{class_index[int(annotation['category_id'])]} {x_center:.8f} {y_center:.8f} "
                    f"{normalized_width:.8f} {normalized_height:.8f}"
                )
            label_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            source_index.append(
                {
                    "prepared_split": split,
                    "source_split": record["source_split"],
                    "source_image_id": record["image_id"],
                    "file_name": record["file_name"],
                    "source_category_id": record["source_category_id"],
                    "class_slug": record["class_slug"],
                    "sha256": record["sha256"],
                    "dhash": f"{record['dhash']:016x}",
                    "boxes": len(record["annotations"]),
                }
            )

    yaml_lines = [
        f"path: {output_root.resolve().as_posix()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "names:",
    ]
    for source_id, index in class_index.items():
        yaml_lines.append(f"  {index}: {SELECTED_CLASSES[source_id]}")
    (output_root / "data.yaml").write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")
    (output_root / "source-index.json").write_text(json.dumps(source_index, indent=2), encoding="utf-8")

    return {
        "split_images": {split: len(records) for split, records in splits.items()},
        "split_boxes": {
            split: sum(len(record["annotations"]) for record in records) for split, records in splits.items()
        },
        "class_split_images": {
            class_slug: {
                split: sum(record["class_slug"] == class_slug for record in records)
                for split, records in splits.items()
            }
            for class_slug in SELECTED_CLASSES.values()
        },
        "class_split_boxes": {
            class_slug: {
                split: sum(
                    len(record["annotations"])
                    for record in records
                    if record["class_slug"] == class_slug
                )
                for split, records in splits.items()
            }
            for class_slug in SELECTED_CLASSES.values()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    ip102_root = workspace / "ml/data/fetched/ip102/extracted/ip102"
    bau_root = workspace / "ml/data/fetched/bau-insectv2/extracted/extracted_folder/pest"
    output_root = workspace / "ml/data/prepared" / DATASET_VERSION
    reports_dir = workspace / "ml/reports"
    registry_dir = workspace / "ml/dataset-registry/versions"
    reports_dir.mkdir(parents=True, exist_ok=True)
    registry_dir.mkdir(parents=True, exist_ok=True)

    train_audit, source_train = audit_coco_split(ip102_root, "train")
    test_audit, source_test = audit_coco_split(ip102_root, "test")
    source_train = enrich_records(source_train)
    source_test = enrich_records(source_test)
    source_train, leakage = remove_test_leakage(source_train, source_test)
    prepared_train, prepared_val, train_val_leakage = split_train_val(source_train)
    splits = {"train": prepared_train, "val": prepared_val, "test": source_test}
    prepared = write_yolo_dataset(output_root, splits)
    bau_audit = audit_bau(bau_root)

    audit = {
        "schema_version": 1,
        "generated_at": "2026-08-22",
        "dataset_version": DATASET_VERSION,
        "ip102": {"train": train_audit, "test": test_audit},
        "bau_insectv2": bau_audit,
        "leakage_control": {
            "official_train_vs_test": leakage,
            "prepared_train_vs_validation": train_val_leakage,
        },
        "prepared": prepared,
        "scope_rule": (
            "Rice-only; source-native IP102 classes with at least 120 official-train images and "
            "30 official-test images. Only images whose annotations contain one selected class are used."
        ),
    }
    report_path = reports_dir / f"{DATASET_VERSION}-audit.json"
    report_path.write_text(json.dumps(audit, indent=2, default=list), encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "dataset_id": DATASET_VERSION,
        "task": "pest-detection",
        "status": "PREPARED_NOT_PROMOTED",
        "crop_scope": ["rice"],
        "classes": [
            {
                "model_index": index,
                "pest_id": SELECTED_CLASSES[source_id],
                "source_dataset": "IP102 v1.1 COCO derivative",
                "source_category_id": source_id,
                "source_label": next(
                    row["source_name"] for row in train_audit["category_counts"] if row["source_category_id"] == source_id
                ),
                "scientific_name_mapping": None,
            }
            for index, source_id in enumerate(SELECTED_CLASSES)
        ],
        "sources": ["ip102-coco-v1", "bau-insectv2-v2"],
        "training_source": "ip102-coco-v1",
        "supplementary_evaluation_source": "bau-insectv2-v2",
        "supplementary_use": "rejection probe only; no coarse BAU label is a supported class",
        "split_seed": SEED,
        "prepared_relative_path": f"ml/data/prepared/{DATASET_VERSION}",
        "prepared_counts": prepared,
        "leakage_policy": "Exact and dHash-distance<=2 train/test matches removed from training candidates",
        "audit_report": f"ml/reports/{report_path.name}",
        "audit_report_sha256": sha256_file(report_path),
        "license": {
            "ip102": "Academic use only; contact original author for other purposes",
            "bau_insectv2": "CC BY 4.0",
            "redistribution": "Raw images and prepared image material are not committed",
        },
    }
    manifest_path = registry_dir / f"{DATASET_VERSION}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(report_path), "manifest": str(manifest_path), **prepared}, indent=2))


if __name__ == "__main__":
    main()
