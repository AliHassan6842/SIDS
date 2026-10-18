"""Prepare a deduplicated BAU coarse general-insect classification candidate.

This is not a species taxonomy and not evidence for insects photographed in homes.
The published BAU train/test folders are pooled because the audit found severe
cross-split duplication, then globally repartitioned by perceptual component.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, UnidentifiedImageError


DATASET_VERSION = "sids-general-insect-classification-v1.0"
SEED = 20260823
SELECTED_LABELS = ("beetle", "grasshopper", "mosquito")
DHASH_DISTANCE = 2
SPLIT_RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def difference_hash(path: Path) -> int:
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


def link_or_copy(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    source_root = workspace / "ml/data/fetched/bau-insectv2/extracted/extracted_folder/pest"
    output = workspace / "ml/data/prepared" / DATASET_VERSION
    report_path = workspace / "ml/reports" / f"{DATASET_VERSION}-preparation.json"
    registry_path = workspace / "ml/dataset-registry/versions" / f"{DATASET_VERSION}.json"
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")

    records = []
    invalid: Counter[str] = Counter()
    published_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for published_split in ("train", "test"):
        for label in SELECTED_LABELS:
            for path in sorted((source_root / published_split / label).rglob("*")):
                if not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                    continue
                try:
                    with Image.open(path) as image:
                        image.verify()
                    image_hash = difference_hash(path)
                except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as error:
                    invalid[type(error).__name__] += 1
                    continue
                published_counts[published_split][label] += 1
                records.append(
                    {
                        "path": path,
                        "published_split": published_split,
                        "source_label": label,
                        "sha256": sha256_file(path),
                        "dhash": image_hash,
                    }
                )

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
    components: dict[int, list[dict]] = defaultdict(list)
    for index, record in enumerate(records):
        components[find(index)].append(record)

    ambiguous = [
        component
        for component in components.values()
        if len({record["source_label"] for record in component}) != 1
    ]
    clean = [
        component
        for component in components.values()
        if len({record["source_label"] for record in component}) == 1
    ]
    representatives: dict[str, list[dict]] = defaultdict(list)
    for component in clean:
        representative = min(
            component,
            key=lambda record: hashlib.sha256(
                f"{SEED}:{record['path'].as_posix()}".encode()
            ).hexdigest(),
        )
        representative = dict(representative)
        representative["component_size"] = len(component)
        representative["component_published_splits"] = sorted(
            {record["published_split"] for record in component}
        )
        representatives[representative["source_label"]].append(representative)

    splits: dict[str, list[dict]] = {split: [] for split in SPLIT_RATIOS}
    for label, label_records in sorted(representatives.items()):
        ordered = sorted(
            label_records,
            key=lambda record: hashlib.sha256(
                f"{SEED}:{record['sha256']}".encode()
            ).hexdigest(),
        )
        count = len(ordered)
        test_count = max(1, round(count * SPLIT_RATIOS["test"]))
        val_count = max(1, round(count * SPLIT_RATIOS["val"]))
        if test_count + val_count >= count:
            raise RuntimeError(f"Not enough deduplicated components for {label}: {count}")
        splits["test"].extend(ordered[:test_count])
        splits["val"].extend(ordered[test_count : test_count + val_count])
        splits["train"].extend(ordered[test_count + val_count :])

    source_index = []
    for split, split_records in splits.items():
        for label in SELECTED_LABELS:
            (output / split / label).mkdir(parents=True, exist_ok=True)
        for record in split_records:
            suffix = record["path"].suffix.lower()
            file_name = f"BAU_{record['source_label']}_{record['sha256'][:20]}{suffix}"
            link_or_copy(record["path"], output / split / record["source_label"] / file_name)
            source_index.append(
                {
                    "prepared_split": split,
                    "file_name": file_name,
                    "class_slug": record["source_label"],
                    "source_dataset": "bau-insectv2-v2",
                    "source_coarse_label": record["source_label"],
                    "source_published_split": record["published_split"],
                    "source_path": str(record["path"]),
                    "sha256": record["sha256"],
                    "dhash": f"{record['dhash']:016x}",
                    "perceptual_component_size": record["component_size"],
                    "component_published_splits": record["component_published_splits"],
                }
            )
    (output / "source-index.json").write_text(
        json.dumps(source_index, indent=2) + "\n", encoding="utf-8"
    )

    split_counts = {
        label: {
            split: sum(record["source_label"] == label for record in split_records)
            for split, split_records in splits.items()
        }
        for label in SELECTED_LABELS
    }
    report = {
        "schema_version": 1,
        "generated_at": "2026-08-23",
        "dataset_version": DATASET_VERSION,
        "status": "PREPARED_RESEARCH_CANDIDATE_NOT_TRAINED_NOT_PROMOTED",
        "task": "coarse-general-insect-classification",
        "published_split_counts": {
            split: dict(sorted(counts.items())) for split, counts in published_counts.items()
        },
        "pooled_valid_images": len(records),
        "invalid_images": dict(sorted(invalid.items())),
        "perceptual_components": len(components),
        "cross_label_ambiguous_components_removed": len(ambiguous),
        "cross_label_ambiguous_images_removed": sum(len(component) for component in ambiguous),
        "deduplicated_representatives": sum(len(rows) for rows in representatives.values()),
        "prepared_counts": split_counts,
        "split_seed": SEED,
        "split_unit": "one representative per global dHash-distance<=2 component",
        "limitations": [
            "BAU folder names are coarse labels, not verified species.",
            "Images are agricultural insect examples, not a household-scene benchmark.",
            "The original published split is discarded because of duplicate leakage.",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "dataset_id": DATASET_VERSION,
        "task": "coarse-general-insect-classification",
        "status": "PREPARED_RESEARCH_CANDIDATE_NOT_TRAINED_NOT_PROMOTED",
        "source": "bau-insectv2-v2",
        "classes": [
            {
                "model_index": index,
                "class_slug": label,
                "source_coarse_label": label,
                "scientific_name_mapping": None,
            }
            for index, label in enumerate(SELECTED_LABELS)
        ],
        "prepared_relative_path": f"ml/data/prepared/{DATASET_VERSION}",
        "prepared_counts": split_counts,
        "split_seed": SEED,
        "leakage_policy": "No perceptual component crosses a prepared split",
        "preparation_report": f"ml/reports/{report_path.name}",
        "preparation_report_sha256": sha256_file(report_path),
        "license": "CC BY 4.0",
        "product_support": False,
        "promotion": {
            "allowed": False,
            "reason": "No general-insect model has been trained or evaluated",
        },
    }
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
