"""Select uncertain/unknown inference records into a deterministic review queue."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from review_schema import (
    difference_hash,
    load_config,
    resolve_bounded_image,
    sha256_file,
    validate_safe_token,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--inference-jsonl", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    config = load_config(args.config)
    selection = config["selection"]
    limit = args.limit or int(selection["maximum_batch_size"])
    allowed = config["allowed_crop_classes"]
    selected = []
    seen_samples = set()

    for line_number, line in enumerate(
        args.inference_jsonl.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        record = json.loads(line)
        sample_id = validate_safe_token(str(record["sample_id"]), "sample_id")
        if sample_id in seen_samples:
            raise ValueError(f"Duplicate sample_id at line {line_number}: {sample_id}")
        seen_samples.add(sample_id)
        crop_slug = str(record["crop_slug"])
        if crop_slug not in allowed:
            continue
        predictions = sorted(
            record.get("predictions", []),
            key=lambda prediction: float(prediction["confidence"]),
            reverse=True,
        )
        for prediction in predictions:
            if prediction["pest_id"] not in allowed[crop_slug]:
                raise ValueError(
                    f"Inference record contains a class outside {crop_slug}: {prediction['pest_id']}"
                )
        top = float(predictions[0]["confidence"]) if predictions else 0.0
        second = float(predictions[1]["confidence"]) if len(predictions) > 1 else 0.0
        reasons = []
        if record.get("status") == "UNKNOWN" and selection["include_unknown"]:
            reasons.append("UNKNOWN")
        if selection["uncertain_confidence_min"] <= top <= selection["uncertain_confidence_max"]:
            reasons.append("UNCERTAIN_CONFIDENCE")
        if len(predictions) > 1 and top - second <= selection["maximum_top_two_margin"]:
            reasons.append("SMALL_TOP_TWO_MARGIN")
        if not reasons:
            continue
        image_path = resolve_bounded_image(args.image_root, str(record["image_path"]))
        selected.append(
            {
                "schema_version": 1,
                "sample_id": sample_id,
                "image_path": str(Path(record["image_path"]).as_posix()),
                "image_sha256": sha256_file(image_path),
                "image_dhash": difference_hash(image_path),
                "capture_group": validate_safe_token(
                    str(record["capture_group"]), "capture_group"
                ),
                "crop_slug": crop_slug,
                "source_model": record.get("model"),
                "source_status": record.get("status"),
                "predictions": predictions,
                "selection_reasons": sorted(set(reasons)),
                "review_status": "pending",
                "reviewer_id": None,
                "reviewed_at": None,
                "annotations": None,
            }
        )

    seed = int(selection["seed"])
    selected.sort(
        key=lambda record: hashlib.sha256(
            f"{seed}:{record['sample_id']}".encode()
        ).hexdigest()
    )
    selected = selected[:limit]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(record) + "\n" for record in selected), encoding="utf-8"
    )
    print(json.dumps({"selected": len(selected), "output": str(args.output)}))


if __name__ == "__main__":
    main()
