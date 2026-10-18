"""Select general-insect confidence/margin thresholds without reading test data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch import nn
from torchvision import datasets, transforms
from torchvision.models import mobilenet_v3_small


def load_candidate(checkpoint: Path) -> tuple[nn.Module, list[str], int]:
    payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
    classes = payload["classes"]
    image_size = int(payload["image_size"])
    model = mobilenet_v3_small(weights=None)
    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, len(classes))
    model.load_state_dict(payload["state_dict"])
    model.eval()
    return model, classes, image_size


def preprocessing(image_size: int) -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def score_known(model: nn.Module, root: Path, image_size: int) -> list[dict]:
    dataset = datasets.ImageFolder(root, transform=preprocessing(image_size))
    rows = []
    with torch.inference_mode():
        for index in range(len(dataset)):
            image, expected = dataset[index]
            probabilities = torch.softmax(model(image.unsqueeze(0))[0], dim=0)
            top = torch.topk(probabilities, 2)
            rows.append(
                {
                    "expected": expected,
                    "predicted": int(top.indices[0]),
                    "confidence": float(top.values[0]),
                    "margin": float(top.values[0] - top.values[1]),
                }
            )
    return rows


def score_ood(model: nn.Module, root: Path, image_size: int) -> list[dict]:
    paths = sorted(path for path in root.rglob("*") if path.suffix.lower() in {".jpg", ".jpeg", ".png"})
    transform = preprocessing(image_size)
    rows = []
    from PIL import Image

    with torch.inference_mode():
        for path in paths:
            with Image.open(path) as source:
                image = transform(source.convert("RGB"))
            probabilities = torch.softmax(model(image.unsqueeze(0))[0], dim=0)
            top = torch.topk(probabilities, 2)
            rows.append(
                {
                    "source_label": path.parent.name,
                    "predicted": int(top.indices[0]),
                    "confidence": float(top.values[0]),
                    "margin": float(top.values[0] - top.values[1]),
                }
            )
    return rows


def metrics(
    known: list[dict],
    ood: list[dict],
    confidence: float,
    margin: float,
    classes: list[str],
    internal_unknown_index: int | None,
) -> dict:
    def accepted(row: dict) -> bool:
        return (
            row["predicted"] != internal_unknown_index
            and row["confidence"] >= confidence
            and row["margin"] >= margin
        )

    accepted_known = [row for row in known if accepted(row)]
    false_accepts = [row for row in ood if accepted(row)]
    per_class = {}
    for class_index, class_name in enumerate(classes):
        class_rows = [row for row in known if row["expected"] == class_index]
        class_accepted = [row for row in accepted_known if row["expected"] == class_index]
        per_class[class_name] = {
            "support": len(class_rows),
            "accepted": len(class_accepted),
            "coverage": len(class_accepted) / len(class_rows),
            "accepted_correct": sum(row["predicted"] == row["expected"] for row in class_accepted),
        }
    return {
        "known_support": len(known),
        "known_accepted": len(accepted_known),
        "known_coverage": len(accepted_known) / len(known),
        "known_accepted_precision": (
            sum(row["predicted"] == row["expected"] for row in accepted_known) / len(accepted_known)
            if accepted_known
            else 0.0
        ),
        "per_class": per_class,
        "ood_support": len(ood),
        "ood_false_accepts": len(false_accepts),
        "ood_false_accept_rate": len(false_accepts) / len(ood),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--ood-calibration", type=Path)
    parser.add_argument("--gates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite calibration report: {args.output}")
    gate_document = json.loads(args.gates.read_text(encoding="utf-8"))
    gates = gate_document["threshold_selection"]
    model, classes, image_size = load_candidate(args.checkpoint)
    internal_unknown_index = classes.index("unknown-insect") if "unknown-insect" in classes else None
    supported_classes = [name for index, name in enumerate(classes) if index != internal_unknown_index]
    known = score_known(model, args.dataset / "val", image_size)
    ood_root = args.ood_calibration or args.dataset / "ood/calibration"
    ood = score_ood(model, ood_root, image_size)
    candidates = []
    for confidence_step in range(34, 100):
        confidence = confidence_step / 100
        for margin_step in range(0, 91, 2):
            margin = margin_step / 100
            result = metrics(known, ood, confidence, margin, supported_classes, internal_unknown_index)
            min_class_coverage = min(row["coverage"] for row in result["per_class"].values())
            if (
                result["known_accepted_precision"] >= gates["minimum_known_accepted_precision"]
                and result["known_coverage"] >= gates["minimum_known_coverage"]
                and min_class_coverage >= gates["minimum_per_class_known_coverage"]
                and result["ood_false_accept_rate"] <= gates["maximum_ood_false_accept_rate"]
            ):
                candidates.append((confidence, margin, result))
    if candidates:
        confidence, margin, selected = max(
            candidates,
            key=lambda row: (
                row[2]["known_coverage"],
                -row[2]["ood_false_accept_rate"],
                row[2]["known_accepted_precision"],
                row[0] + row[1],
            ),
        )
        status = "PASS"
    else:
        confidence = margin = None
        selected = None
        status = "FAIL_NO_THRESHOLD_MEETS_PREDECLARED_GATES"
    report = {
        "schema_version": 1,
        "status": status,
        "checkpoint": str(args.checkpoint),
        "dataset_version": gate_document["dataset_version"],
        "classes": classes,
        "supported_classes": supported_classes,
        "internal_unknown_index": internal_unknown_index,
        "known_validation_support": len(known),
        "ood_calibration_support": len(ood),
        "confidence_threshold": confidence,
        "margin_threshold": margin,
        "selected_metrics": selected,
        "test_data_read": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
