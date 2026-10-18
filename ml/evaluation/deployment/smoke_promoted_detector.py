"""Exercise the checksum-verified promoted manifest through runtime components."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from sids_ai.core.config import Settings
from sids_ai.core.errors import ImageRejected
from sids_ai.image.decoder import decode_and_sanitize
from sids_ai.insect.model import PestDetector
from sids_ai.registry.manifest import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--threshold-report", type=Path, required=True)
    parser.add_argument("--bad-image", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    detector = PestDetector(manifest)
    settings = Settings(service_token="local-runtime-smoke-only")
    threshold_report = json.loads(args.threshold_report.read_text(encoding="utf-8"))
    fixtures = threshold_report["fixtures"]

    groups = {
        "known_pests": [Path(path) for path in fixtures["known_test"]],
        "unsupported_insects": [Path(path) for path in fixtures["bau_holdout"]],
        "non_insect_random_objects": [
            Path(path) for path in fixtures["non_insect_random_object_holdout"]
        ],
    }
    results = {}
    for group_name, paths in groups.items():
        accepted = image_rejected = 0
        elapsed = 0.0
        samples = []
        rejection_reasons: dict[str, int] = {}
        for path in paths:
            started = time.perf_counter()
            try:
                decoded = decode_and_sanitize(
                    path.read_bytes(),
                    f"image/{'png' if path.suffix.lower() == '.png' else 'jpeg'}",
                    settings,
                )
                detection = detector.identify(decoded.rgb, "rice")
            except ImageRejected as error:
                image_rejected += 1
                rejection_reasons[error.reason] = rejection_reasons.get(error.reason, 0) + 1
                detection = None
            finally:
                elapsed += time.perf_counter() - started
            accepted += detection is not None
            if detection is not None and len(samples) < 4:
                samples.append(
                    {
                        "path": str(path),
                        "pest_id": detection.prediction.pestId,
                        "confidence": detection.prediction.confidence,
                        "bbox": detection.prediction.bbox.model_dump(),
                    }
                )
        results[group_name] = {
            "status": "EXECUTED",
            "images": len(paths),
            "identified": accepted,
            "unknown": len(paths) - accepted,
            "rejected_before_inference": image_rejected,
            "rejection_reasons": rejection_reasons,
            "latency_ms_per_image": 1000 * elapsed / len(paths),
            "identified_samples": samples,
        }

    started = time.perf_counter()
    try:
        decode_and_sanitize(args.bad_image.read_bytes(), "image/jpeg", settings)
        bad_image = {"status": "FAIL_ACCEPTED_INVALID_PAYLOAD"}
    except ImageRejected as error:
        bad_image = {
            "status": "PASS_REJECTED_INVALID_PAYLOAD",
            "reason": error.reason,
            "message": str(error),
            "payload_bytes": args.bad_image.stat().st_size,
            "latency_ms": 1000 * (time.perf_counter() - started),
        }

    report = {
        "schema_version": 1,
        "manifest": str(args.manifest),
        "model_id": manifest.model_id,
        "model_version": manifest.version,
        "dataset_version": manifest.dataset_version,
        "artifact_path": str(manifest.artifact_path),
        "artifact_sha256": manifest.sha256,
        "acceptance_threshold": manifest.acceptance_threshold,
        "groups": results,
        "bad_image": bad_image,
        "note": "This smoke run checks runtime loading and response behavior; AP and leakage-safe threshold metrics live in the evaluation reports.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"groups": results, "bad_image": bad_image}))


if __name__ == "__main__":
    main()
