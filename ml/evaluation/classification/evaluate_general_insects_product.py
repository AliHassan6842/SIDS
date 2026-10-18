"""One-shot product-gate evaluation and TorchScript export for general insects."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torchvision import datasets, transforms
from torchvision.models import mobilenet_v3_small


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def preprocessing(image_size: int) -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def load_model(checkpoint: Path) -> tuple[nn.Module, list[str], int, int]:
    payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
    classes = list(payload["classes"])
    image_size = int(payload["image_size"])
    unknown_index = int(payload["internal_unknown_index"])
    model = mobilenet_v3_small(weights=None)
    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, len(classes))
    model.load_state_dict(payload["state_dict"])
    model.eval()
    return model, classes, image_size, unknown_index


def score(model: nn.Module, tensor: torch.Tensor) -> tuple[int, float, float, float]:
    started = time.perf_counter()
    probabilities = torch.softmax(model(tensor.unsqueeze(0))[0], dim=0)
    elapsed_ms = (time.perf_counter() - started) * 1000
    top = torch.topk(probabilities, 2)
    return int(top.indices[0]), float(top.values[0]), float(top.values[0] - top.values[1]), elapsed_ms


def accepted(predicted: int, confidence: float, margin: float, unknown_index: int, thresholds: dict) -> bool:
    return (
        predicted != unknown_index
        and confidence >= thresholds["confidence_threshold"]
        and margin >= thresholds["margin_threshold"]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--gates", type=Path, required=True)
    parser.add_argument("--coco8", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists() or args.artifact.exists():
        raise FileExistsError("Refusing to overwrite one-shot test output")
    calibration = json.loads(args.calibration.read_text(encoding="utf-8"))
    if calibration["status"] != "PASS" or not calibration["test_data_read"] is False:
        raise ValueError("Calibration evidence is not eligible")
    gate_document = json.loads(args.gates.read_text(encoding="utf-8"))
    gates = gate_document["promotion_gates"]
    thresholds = {
        "confidence_threshold": calibration["confidence_threshold"],
        "margin_threshold": calibration["margin_threshold"],
    }
    model, classes, image_size, unknown_index = load_model(args.checkpoint)
    transform = preprocessing(image_size)
    known_dataset = datasets.ImageFolder(args.dataset / "test", transform=transform)
    known_rows, latencies = [], []
    with torch.inference_mode():
        for index in range(len(known_dataset)):
            tensor, expected = known_dataset[index]
            predicted, confidence, margin, latency = score(model, tensor)
            latencies.append(latency)
            known_rows.append(
                {
                    "path": known_dataset.samples[index][0],
                    "expected": expected,
                    "predicted": predicted,
                    "confidence": confidence,
                    "margin": margin,
                    "accepted": accepted(predicted, confidence, margin, unknown_index, thresholds),
                }
            )
    supported_classes = classes[:unknown_index]
    accepted_known = [row for row in known_rows if row["accepted"]]
    known_metrics = {
        "support": len(known_rows),
        "accepted": len(accepted_known),
        "coverage": len(accepted_known) / len(known_rows),
        "accepted_precision": (
            sum(row["expected"] == row["predicted"] for row in accepted_known) / len(accepted_known)
            if accepted_known
            else 0.0
        ),
        "per_class": {},
    }
    for class_index, class_name in enumerate(supported_classes):
        rows = [row for row in known_rows if row["expected"] == class_index]
        accepted_rows = [row for row in rows if row["accepted"]]
        known_metrics["per_class"][class_name] = {
            "support": len(rows),
            "accepted": len(accepted_rows),
            "coverage": len(accepted_rows) / len(rows),
            "accepted_correct": sum(row["expected"] == row["predicted"] for row in accepted_rows),
        }

    def evaluate_ood(root: Path) -> tuple[dict, list[dict]]:
        paths = sorted(path for path in root.rglob("*") if path.suffix.lower() in {".jpg", ".jpeg", ".png"})
        rows = []
        with torch.inference_mode():
            for path in paths:
                with Image.open(path) as source:
                    tensor = transform(source.convert("RGB"))
                predicted, confidence, margin, latency = score(model, tensor)
                latencies.append(latency)
                rows.append(
                    {
                        "path": str(path),
                        "predicted": predicted,
                        "confidence": confidence,
                        "margin": margin,
                        "accepted": accepted(predicted, confidence, margin, unknown_index, thresholds),
                    }
                )
        false_accepts = sum(row["accepted"] for row in rows)
        return {
            "support": len(rows),
            "false_accepts": false_accepts,
            "false_accept_rate": false_accepts / len(rows),
        }, rows

    bau_ood, bau_rows = evaluate_ood(args.dataset / "unknown/test")
    coco8, coco_rows = evaluate_ood(args.coco8)
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    example = torch.zeros((1, 3, image_size, image_size), dtype=torch.float32)
    scripted = torch.jit.trace(model, example)
    torch.jit.save(scripted, str(args.artifact))
    artifact_bytes = args.artifact.stat().st_size
    artifact_sha256 = sha256_file(args.artifact)
    with torch.inference_mode():
        original = model(example)
        reloaded = torch.jit.load(str(args.artifact), map_location="cpu")(example)
    export_max_abs_difference = float(torch.max(torch.abs(original - reloaded)))
    latency_p95 = sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)]
    checks = {
        "known_accepted_precision": known_metrics["accepted_precision"] >= gates["minimum_known_accepted_precision"],
        "known_coverage": known_metrics["coverage"] >= gates["minimum_known_coverage"],
        "per_class_known_coverage": all(
            row["coverage"] >= gates["minimum_per_class_known_coverage"]
            for row in known_metrics["per_class"].values()
        ),
        "bau_class_disjoint_ood_fpr": (
            bau_ood["false_accept_rate"] <= gates["maximum_bau_class_disjoint_ood_false_accept_rate"]
        ),
        "coco8_non_insect_fpr": coco8["false_accept_rate"] <= gates["maximum_coco8_non_insect_false_accept_rate"],
        "cpu_p95_latency": latency_p95 <= gates["maximum_cpu_p95_latency_ms"],
        "artifact_size": artifact_bytes <= gates["maximum_artifact_bytes"],
        "export_equivalence": export_max_abs_difference <= 1e-6,
    }
    report = {
        "schema_version": 1,
        "status": "PASS_MODEL_GATES_PENDING_RUNTIME" if all(checks.values()) else "FAIL_NOT_PROMOTED",
        "model_id": gate_document["candidate_model_id"],
        "model_version": gate_document["candidate_model_version"],
        "dataset_version": gate_document["dataset_version"],
        "classes": classes,
        "supported_classes": supported_classes,
        "internal_unknown_index": unknown_index,
        "thresholds": thresholds,
        "known_test_disclosure": gate_document["known_test_disclosure"],
        "known_test": known_metrics,
        "bau_class_disjoint_ood_test": bau_ood,
        "coco8_external_non_insect_probe": coco8,
        "latency": {
            "samples": len(latencies),
            "mean_ms": statistics.mean(latencies),
            "p95_ms": latency_p95,
            "scope": "preprocessed single-image model forward on local CPU",
        },
        "artifact": str(args.artifact),
        "artifact_bytes": artifact_bytes,
        "artifact_sha256": artifact_sha256,
        "export_max_abs_difference": export_max_abs_difference,
        "checks": checks,
        "positive_fixture_candidates": {
            class_name: [row for row in known_rows if row["expected"] == index and row["accepted"] and row["predicted"] == index][:2]
            for index, class_name in enumerate(supported_classes)
        },
        "ood_false_accept_rows": [row for row in bau_rows if row["accepted"]],
        "coco8_rows": coco_rows,
        "test_executed_once": True,
        "promotion": "NOT_PERFORMED_BY_EVALUATOR",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "known_test", "bau_class_disjoint_ood_test", "coco8_external_non_insect_probe", "latency", "artifact_bytes", "artifact_sha256", "checks")}, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
