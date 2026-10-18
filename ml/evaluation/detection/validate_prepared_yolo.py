"""Independently validate a prepared YOLO tree and its source index."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--classes", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    index = json.loads((args.dataset / "source-index.json").read_text(encoding="utf-8"))
    indexed = {(record["prepared_split"], record["file_name"]): record for record in index}
    errors = []
    counts = {}
    hashes_by_split = {}
    dhashes_by_split = {}
    for split in ("train", "val", "test"):
        images = sorted((args.dataset / "images" / split).glob("*"))
        labels = sorted((args.dataset / "labels" / split).glob("*.txt"))
        image_stems = {path.stem for path in images}
        label_stems = {path.stem for path in labels}
        if image_stems != label_stems:
            errors.append(
                {
                    "split": split,
                    "missing_labels": sorted(image_stems - label_stems),
                    "orphan_labels": sorted(label_stems - image_stems),
                }
            )
        class_boxes: Counter[int] = Counter()
        for image_path in images:
            try:
                with Image.open(image_path) as image:
                    image.verify()
            except Exception as error:
                errors.append({"split": split, "image": image_path.name, "error": str(error)})
            record = indexed.get((split, image_path.name))
            if record is None:
                errors.append({"split": split, "image": image_path.name, "error": "NOT_INDEXED"})
                continue
            for line_number, line in enumerate(
                (args.dataset / "labels" / split / f"{image_path.stem}.txt")
                .read_text(encoding="utf-8")
                .splitlines(),
                start=1,
            ):
                fields = line.split()
                if len(fields) != 5:
                    errors.append(
                        {"split": split, "image": image_path.name, "line": line_number, "error": "FIELDS"}
                    )
                    continue
                class_id = int(fields[0])
                x, y, width, height = map(float, fields[1:])
                if not 0 <= class_id < args.classes:
                    errors.append({"split": split, "image": image_path.name, "error": "CLASS_RANGE"})
                if not (
                    0 <= x <= 1
                    and 0 <= y <= 1
                    and 0 < width <= 1
                    and 0 < height <= 1
                    and x - width / 2 >= -1e-6
                    and y - height / 2 >= -1e-6
                    and x + width / 2 <= 1 + 1e-6
                    and y + height / 2 <= 1 + 1e-6
                ):
                    errors.append({"split": split, "image": image_path.name, "error": "BBOX_RANGE"})
                class_boxes[class_id] += 1
        split_records = [record for record in index if record["prepared_split"] == split]
        hashes_by_split[split] = {record["sha256"] for record in split_records}
        dhashes_by_split[split] = [
            (record["file_name"], int(record["dhash"], 16)) for record in split_records
        ]
        counts[split] = {
            "images": len(images),
            "labels": len(labels),
            "boxes": sum(class_boxes.values()),
            "boxes_by_model_index": dict(sorted(class_boxes.items())),
        }

    leakage = {}
    for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
        exact = hashes_by_split[left] & hashes_by_split[right]
        near = []
        for left_name, left_hash in dhashes_by_split[left]:
            for right_name, right_hash in dhashes_by_split[right]:
                distance = (left_hash ^ right_hash).bit_count()
                if distance <= 2:
                    near.append({"left": left_name, "right": right_name, "distance": distance})
        leakage[f"{left}_vs_{right}"] = {
            "exact_sha_overlap": len(exact),
            "dhash_distance_lte_2_pairs": len(near),
        }
        if exact or near:
            errors.append({"split_pair": f"{left}_vs_{right}", "error": "LEAKAGE"})
    report = {
        "schema_version": 1,
        "dataset": str(args.dataset),
        "status": "PASS" if not errors else "FAIL",
        "counts": counts,
        "source_index_records": len(index),
        "leakage": leakage,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors), "counts": counts}))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
