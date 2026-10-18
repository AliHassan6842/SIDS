"""Validate human decisions and seal an immutable reviewed batch manifest."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from review_schema import (
    assigned_split,
    difference_hash,
    load_config,
    resolve_bounded_image,
    sha256_file,
    validate_bbox,
    validate_safe_token,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--reviewed-jsonl", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    validate_safe_token(args.batch_id, "batch_id")
    allowed = config["allowed_crop_classes"]
    review_config = config["review"]
    sealed = []
    seen_samples = set()
    for line_number, line in enumerate(
        args.reviewed_jsonl.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        record = json.loads(line)
        sample_id = validate_safe_token(str(record["sample_id"]), "sample_id")
        if sample_id in seen_samples:
            raise ValueError(f"Duplicate sample_id at line {line_number}: {sample_id}")
        seen_samples.add(sample_id)
        status = record.get("review_status")
        if status not in review_config["required_statuses"]:
            raise ValueError(f"Unreviewed sample {sample_id}: {status}")
        reviewer = str(record.get("reviewer_id") or "")
        if len(reviewer) < int(review_config["minimum_reviewer_id_length"]):
            raise ValueError(f"Missing reviewer identity for {sample_id}")
        if not record.get("reviewed_at"):
            raise ValueError(f"Missing reviewed_at for {sample_id}")
        image_path = resolve_bounded_image(args.image_root, str(record["image_path"]))
        actual_sha = sha256_file(image_path)
        if actual_sha != record.get("image_sha256"):
            raise ValueError(f"Image checksum changed after selection: {sample_id}")
        if difference_hash(image_path) != record.get("image_dhash"):
            raise ValueError(f"Image perceptual hash changed after selection: {sample_id}")
        annotations = record.get("annotations")
        if status == "approved":
            if not isinstance(annotations, list):
                raise ValueError(f"Approved sample needs an annotations list: {sample_id}")
            crop_slug = record["crop_slug"]
            for annotation in annotations:
                if annotation["pest_id"] not in allowed[crop_slug]:
                    raise ValueError(
                        f"Annotation outside crop taxonomy for {sample_id}: {annotation['pest_id']}"
                    )
                validate_bbox(annotation["bbox"])
        elif annotations not in (None, []):
            raise ValueError(f"Rejected sample must not carry annotations: {sample_id}")
        validate_safe_token(str(record["capture_group"]), "capture_group")
        item = dict(record)
        item["assigned_split"] = assigned_split(
            str(record["capture_group"]),
            int(review_config["split_seed"]),
            review_config["split_ratios"],
        )
        sealed.append(item)

    group_splits = {}
    for record in sealed:
        previous = group_splits.setdefault(record["capture_group"], record["assigned_split"])
        if previous != record["assigned_split"]:
            raise RuntimeError("Capture group crossed splits")
    payload = {
        "schema_version": 1,
        "batch_id": args.batch_id,
        "status": "SEALED_HUMAN_REVIEWED_NOT_MATERIALIZED",
        "config": str(args.config),
        "config_sha256": sha256_file(args.config),
        "source_review_file": str(args.reviewed_jsonl),
        "source_review_sha256": sha256_file(args.reviewed_jsonl),
        "counts": {
            "review_status": dict(Counter(record["review_status"] for record in sealed)),
            "assigned_split": dict(Counter(record["assigned_split"] for record in sealed)),
            "approved_annotations": sum(
                len(record["annotations"] or []) for record in sealed
            ),
        },
        "records": sealed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sealed": len(sealed), "output": str(args.output)}))


if __name__ == "__main__":
    main()
