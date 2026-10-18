"""Calibrate an image-level acceptance threshold and run rejection probes.

This evaluator deliberately keeps training evidence (IP102) separate from rejection
evidence (BAU-Insectv2 and local COCO8 fixtures). It does not reinterpret BAU's
coarse folder names as species labels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from collections import defaultdict
from pathlib import Path

from PIL import Image
from ultralytics import YOLO


def sha256(path: Path) -> str:
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
    return sum(
        (1 << (row * 8 + col))
        for row in range(8)
        for col in range(8)
        if pixels[row * 9 + col] > pixels[row * 9 + col + 1]
    )


def iou_xyxy(left: list[float], right: list[float]) -> float:
    x1, y1 = max(left[0], right[0]), max(left[1], right[1])
    x2, y2 = min(left[2], right[2]), min(left[3], right[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    left_area = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    right_area = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union else 0.0


def load_truth(dataset_root: Path, source_index: Path, split: str) -> list[dict]:
    records = json.loads(source_index.read_text(encoding="utf-8"))
    selected = []
    for record in records:
        if record["prepared_split"] != split:
            continue
        image_path = dataset_root / "images" / split / record["file_name"]
        label_path = dataset_root / "labels" / split / f"{image_path.stem}.txt"
        with Image.open(image_path) as image:
            width, height = image.size
        boxes = []
        for line in label_path.read_text(encoding="utf-8").splitlines():
            class_id, cx, cy, bw, bh = map(float, line.split())
            boxes.append(
                {
                    "class_id": int(class_id),
                    "xyxy": [
                        (cx - bw / 2) * width,
                        (cy - bh / 2) * height,
                        (cx + bw / 2) * width,
                        (cy + bh / 2) * height,
                    ],
                }
            )
        selected.append({"path": image_path, "truth": boxes})
    return selected


def predict(model: YOLO, paths: list[Path], image_size: int) -> tuple[list[dict], float]:
    started = time.perf_counter()
    results = model.predict(
        source=[str(path) for path in paths],
        imgsz=image_size,
        conf=0.001,
        iou=0.7,
        device="cpu",
        verbose=False,
        stream=False,
    )
    elapsed = time.perf_counter() - started
    parsed = []
    for path, result in zip(paths, results, strict=True):
        detections = []
        if result.boxes is not None:
            for box in result.boxes:
                detections.append(
                    {
                        "class_id": int(box.cls.item()),
                        "confidence": float(box.conf.item()),
                        "xyxy": [float(value) for value in box.xyxy[0].tolist()],
                    }
                )
        parsed.append({"path": str(path), "detections": detections})
    return parsed, elapsed


def known_metrics(predictions: list[dict], truth: list[dict], threshold: float) -> dict:
    correct = accepted = 0
    for prediction, target in zip(predictions, truth, strict=True):
        qualifying = [
            detection
            for detection in prediction["detections"]
            if detection["confidence"] >= threshold
        ]
        accepted += bool(qualifying)
        matched = any(
            detection["class_id"] == gt["class_id"]
            and iou_xyxy(detection["xyxy"], gt["xyxy"]) >= 0.5
            for detection in qualifying
            for gt in target["truth"]
        )
        correct += matched
    total = len(truth)
    return {
        "images": total,
        "accepted_images": accepted,
        "correctly_localized_images": correct,
        "unknown_images": total - accepted,
        "accepted_but_not_correctly_localized": accepted - correct,
        "coverage": accepted / total if total else 0.0,
        "correct_detection_rate": correct / total if total else 0.0,
        "accepted_precision": correct / accepted if accepted else 0.0,
    }


def rejection_metrics(predictions: list[dict], threshold: float) -> dict:
    accepted = sum(
        any(detection["confidence"] >= threshold for detection in prediction["detections"])
        for prediction in predictions
    )
    total = len(predictions)
    return {
        "images": total,
        "false_accepts": accepted,
        "rejected": total - accepted,
        "false_accept_rate": accepted / total if total else 0.0,
    }


def bau_probe_split(root: Path, seed: int, per_class: int) -> tuple[list[Path], list[Path], dict]:
    candidates = sorted(
        path
        for path in root.rglob("*")
        if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    valid = []
    invalid = 0
    for path in candidates:
        try:
            with Image.open(path) as image:
                image.verify()
            valid.append((path, sha256(path), dhash(path)))
        except Exception:
            invalid += 1

    # Assign global perceptual components so a near duplicate cannot cross probes.
    parent = list(range(len(valid)))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    sha_first: dict[str, int] = {}
    for index, (_, digest, _) in enumerate(valid):
        if digest in sha_first:
            union(index, sha_first[digest])
        else:
            sha_first[digest] = index
    for left in range(len(valid)):
        for right in range(left + 1, len(valid)):
            if (valid[left][2] ^ valid[right][2]).bit_count() <= 2:
                union(left, right)

    by_class: dict[str, list[tuple[int, Path]]] = defaultdict(list)
    for index, (path, _, _) in enumerate(valid):
        relative = path.relative_to(root)
        # layout is split/class/file
        class_name = relative.parts[-2]
        by_class[class_name].append((find(index), path))

    calibration: list[Path] = []
    holdout: list[Path] = []
    used_groups: set[int] = set()
    rng = random.Random(seed)
    per_class_counts = {}
    for class_name in sorted(by_class):
        representatives: dict[int, Path] = {}
        for group, path in by_class[class_name]:
            representatives.setdefault(group, path)
        items = sorted(representatives.items(), key=lambda item: str(item[1]))
        rng.shuffle(items)
        available = [(group, path) for group, path in items if group not in used_groups]
        calibration_items = available[:per_class]
        holdout_items = available[per_class : per_class * 2]
        calibration.extend(path for _, path in calibration_items)
        holdout.extend(path for _, path in holdout_items)
        used_groups.update(group for group, _ in calibration_items + holdout_items)
        per_class_counts[class_name] = {
            "calibration": len(calibration_items),
            "holdout": len(holdout_items),
        }
    return calibration, holdout, {
        "candidate_files": len(candidates),
        "valid_files": len(valid),
        "invalid_files": invalid,
        "perceptual_components": len({find(index) for index in range(len(valid))}),
        "per_class": per_class_counts,
        "selection_seed": seed,
        "max_per_class_per_partition": per_class,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--source-index", type=Path, required=True)
    parser.add_argument("--bau-root", type=Path, required=True)
    parser.add_argument("--non-insect", type=Path, action="append", default=[])
    parser.add_argument("--bad-image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260822)
    parser.add_argument("--image-size", type=int, default=320)
    parser.add_argument("--bau-per-class", type=int, default=5)
    args = parser.parse_args()

    model = YOLO(str(args.model))
    validation_truth = load_truth(args.dataset_root, args.source_index, "val")
    test_truth = load_truth(args.dataset_root, args.source_index, "test")
    bau_calibration, bau_holdout, bau_audit = bau_probe_split(
        args.bau_root, args.seed, args.bau_per_class
    )

    val_predictions, val_seconds = predict(
        model, [item["path"] for item in validation_truth], args.image_size
    )
    test_predictions, test_seconds = predict(
        model, [item["path"] for item in test_truth], args.image_size
    )
    bau_cal_predictions, bau_cal_seconds = predict(model, bau_calibration, args.image_size)
    bau_hold_predictions, bau_hold_seconds = predict(model, bau_holdout, args.image_size)
    object_midpoint = len(args.non_insect) // 2
    object_calibration_paths = args.non_insect[:object_midpoint]
    object_holdout_paths = args.non_insect[object_midpoint:]
    object_cal_predictions, object_cal_seconds = predict(
        model, object_calibration_paths, args.image_size
    )
    object_hold_predictions, object_hold_seconds = predict(
        model, object_holdout_paths, args.image_size
    )

    candidates = []
    for step in range(5, 96):
        threshold = step / 100
        known = known_metrics(val_predictions, validation_truth, threshold)
        ood = rejection_metrics(bau_cal_predictions, threshold)
        objects = rejection_metrics(object_cal_predictions, threshold)
        if (
            known["accepted_precision"] >= 0.80
            and ood["false_accept_rate"] <= 0.05
            and objects["false_accept_rate"] == 0.0
        ):
            f1 = (
                2
                * known["accepted_precision"]
                * known["correct_detection_rate"]
                / (known["accepted_precision"] + known["correct_detection_rate"])
            )
            candidates.append((f1, -threshold, threshold, known, ood, objects))

    selected = max(candidates) if candidates else None
    threshold = selected[2] if selected else None
    held_known = known_metrics(test_predictions, test_truth, threshold) if selected else None
    held_bau = rejection_metrics(bau_hold_predictions, threshold) if selected else None
    held_objects = rejection_metrics(object_hold_predictions, threshold) if selected else None
    held_out_gate = bool(
        selected
        and held_known["accepted_precision"] >= 0.80
        and held_known["correct_detection_rate"] >= 0.30
        and held_bau["false_accept_rate"] <= 0.10
        and held_objects["false_accept_rate"] <= 0.10
    )
    bad_image_result = {"status": "NOT_EXECUTED"}
    if args.bad_image:
        started = time.perf_counter()
        try:
            invalid_results = model.predict(
                source=str(args.bad_image),
                imgsz=args.image_size,
                conf=threshold or 0.25,
                device="cpu",
                verbose=False,
            )
            returned_detections = sum(
                len(result.boxes) if result.boxes is not None else 0
                for result in invalid_results
            )
            bad_image_result = {
                "status": "EXECUTED_BACKEND_DID_NOT_RAISE",
                "elapsed_ms": 1000 * (time.perf_counter() - started),
                "returned_results": len(invalid_results),
                "returned_detections": returned_detections,
                "note": "HTTP/runtime validation must reject malformed bytes before this backend",
            }
        except Exception as error:
            bad_image_result = {
                "status": "PASS_REJECTED_INVALID_PAYLOAD",
                "elapsed_ms": 1000 * (time.perf_counter() - started),
                "exception_type": type(error).__name__,
                "message": str(error),
                "payload_path": str(args.bad_image),
                "payload_bytes": args.bad_image.stat().st_size,
            }

    report = {
        "schema_version": 1,
        "model_path": str(args.model),
        "model_sha256": sha256(args.model),
        "dataset_version": args.dataset_version,
        "threshold_selection_rule": (
            "Highest validation image-level F1 among thresholds 0.05..0.95 with "
            "accepted precision >=0.80, BAU calibration false-accept rate <=0.05, "
            "and zero false accepts on four COCO8 calibration fixtures; "
            "ties prefer the lower threshold"
        ),
        "selected_threshold": threshold,
        "promotion_gate": "PASS" if held_out_gate else "BLOCKED_EXTERNAL",
        "held_out_gate_rule": (
            "IP102 test accepted precision >=0.80 and correct-detection rate >=0.30; "
            "BAU holdout false-accept rate <=0.10; COCO8 holdout false-accept rate <=0.10"
        ),
        "calibration": {
            "known_ip102_validation": selected[3] if selected else None,
            "unsupported_insect_bau": selected[4] if selected else None,
            "non_insect_random_object_coco8": selected[5] if selected else None,
        },
        "held_out": {
            "known_ip102_test": held_known,
            "unsupported_insect_bau": held_bau,
            "non_insect_random_object_coco8": held_objects,
        },
        "latency": {
            "device": "cpu",
            "image_size": args.image_size,
            "ip102_validation_ms_per_image": 1000 * val_seconds / len(validation_truth),
            "ip102_test_ms_per_image": 1000 * test_seconds / len(test_truth),
            "bau_calibration_ms_per_image": 1000 * bau_cal_seconds / len(bau_calibration),
            "bau_holdout_ms_per_image": 1000 * bau_hold_seconds / len(bau_holdout),
            "coco8_calibration_ms_per_image": (
                1000 * object_cal_seconds / len(object_calibration_paths)
                if object_calibration_paths
                else None
            ),
            "coco8_holdout_ms_per_image": (
                1000 * object_hold_seconds / len(object_holdout_paths)
                if object_holdout_paths
                else None
            ),
        },
        "bau_probe_audit": bau_audit,
        "fixtures": {
            "known_validation": [str(item["path"]) for item in validation_truth],
            "known_test": [str(item["path"]) for item in test_truth],
            "bau_calibration": [str(path) for path in bau_calibration],
            "bau_holdout": [str(path) for path in bau_holdout],
            "non_insect_random_object_calibration": [
                str(path) for path in object_calibration_paths
            ],
            "non_insect_random_object_holdout": [str(path) for path in object_holdout_paths],
            "bad_image": bad_image_result,
        },
        "limitations": [
            "BAU is rejection-only evidence; its coarse labels are not mapped to IP102 classes.",
            "COCO8 is rejection-only evidence and is not product or pest-training evidence.",
            "This is a bounded CPU short-run, not a production-scale training claim.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected_threshold": threshold, "promotion_gate": report["promotion_gate"]}))


if __name__ == "__main__":
    main()
