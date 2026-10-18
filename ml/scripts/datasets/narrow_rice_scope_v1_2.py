"""Derive the final two-class dataset from the audited leakage-safe v1.1 split."""

from __future__ import annotations

import json
import os
import shutil
from collections import Counter
from pathlib import Path


SOURCE_VERSION = "sids-rice-pest-detection-v1.1"
TARGET_VERSION = "sids-rice-pest-detection-v1.2"
ALLOWED = {"rice-leaf-roller": 0, "rice-water-weevil": 1}
OLD_TO_NEW = {0: 0, 2: 1}


def link_or_copy(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def main() -> None:
    workspace = Path(__file__).resolve().parents[3]
    source = workspace / "ml/data/prepared" / SOURCE_VERSION
    target = workspace / "ml/data/prepared" / TARGET_VERSION
    if target.exists():
        raise FileExistsError(target)

    source_index = json.loads((source / "source-index.json").read_text(encoding="utf-8"))
    selected = [record for record in source_index if record["class_slug"] in ALLOWED]
    for split in ("train", "val", "test"):
        (target / "images" / split).mkdir(parents=True)
        (target / "labels" / split).mkdir(parents=True)

    for record in selected:
        split = record["prepared_split"]
        filename = record["file_name"]
        link_or_copy(source / "images" / split / filename, target / "images" / split / filename)
        old_lines = (source / "labels" / split / f"{Path(filename).stem}.txt").read_text(encoding="utf-8").splitlines()
        new_lines = []
        for line in old_lines:
            parts = line.split()
            old_index = int(parts[0])
            if old_index not in OLD_TO_NEW:
                raise ValueError(f"Unexpected mixed label {old_index} in {filename}")
            parts[0] = str(OLD_TO_NEW[old_index])
            new_lines.append(" ".join(parts))
        (target / "labels" / split / f"{Path(filename).stem}.txt").write_text(
            "\n".join(new_lines) + "\n", encoding="utf-8"
        )
        record["model_index"] = ALLOWED[record["class_slug"]]

    (target / "source-index.json").write_text(json.dumps(selected, indent=2), encoding="utf-8")
    (target / "data.yaml").write_text(
        "\n".join(
            [
                f"path: {target.resolve().as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                "  0: rice-leaf-roller",
                "  1: rice-water-weevil",
                "",
            ]
        ),
        encoding="utf-8",
    )

    image_counts = Counter((record["class_slug"], record["prepared_split"]) for record in selected)
    box_counts = Counter()
    for record in selected:
        box_counts[(record["class_slug"], record["prepared_split"])] += int(record["boxes"])
    counts = {
        "images": {
            pest: {split: image_counts[(pest, split)] for split in ("train", "val", "test")}
            for pest in ALLOWED
        },
        "boxes": {
            pest: {split: box_counts[(pest, split)] for split in ("train", "val", "test")}
            for pest in ALLOWED
        },
        "split_images": {
            split: sum(image_counts[(pest, split)] for pest in ALLOWED)
            for split in ("train", "val", "test")
        },
        "split_boxes": {
            split: sum(box_counts[(pest, split)] for pest in ALLOWED)
            for split in ("train", "val", "test")
        },
    }
    manifest = {
        "schema_version": 1,
        "dataset_id": TARGET_VERSION,
        "task": "pest-detection",
        "status": "PREPARED_NOT_PROMOTED",
        "derived_from": SOURCE_VERSION,
        "derivation": "Removed asiatic-rice-borer after weak independent short-run test evidence; retained existing leakage-safe split membership",
        "crop_scope": ["rice"],
        "classes": [
            {
                "model_index": index,
                "pest_id": pest,
                "source_dataset": "IP102 v1.1 COCO derivative",
                "source_category_id": 1 if pest == "rice-leaf-roller" else 11,
                "scientific_name_mapping": None,
            }
            for pest, index in ALLOWED.items()
        ],
        "prepared_relative_path": f"ml/data/prepared/{TARGET_VERSION}",
        "prepared_counts": counts,
        "split_seed": 20260822,
        "leakage_evidence": "Inherited v1.1 split; re-verification must show no SHA or dHash-distance<=2 overlap",
        "license": {
            "ip102": "Academic use only; contact original author for other purposes",
            "redistribution": "Raw and prepared images are not committed",
        },
    }
    registry = workspace / "ml/dataset-registry/versions"
    registry.mkdir(parents=True, exist_ok=True)
    (registry / f"{TARGET_VERSION}.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
