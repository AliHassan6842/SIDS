"""Bounded CPU linear-probe training for the BAU coarse general-insect candidate."""

from __future__ import annotations

import argparse
import copy
import json
import platform
import random
import time
from pathlib import Path

import numpy as np
import torch
import torchvision
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def classification_metrics(labels: list[int], predictions: list[int], classes: list[str]) -> dict:
    matrix = [[0 for _ in classes] for _ in classes]
    for expected, predicted in zip(labels, predictions):
        matrix[expected][predicted] += 1
    per_class = {}
    f1_values = []
    for index, class_name in enumerate(classes):
        true_positive = matrix[index][index]
        false_positive = sum(matrix[row][index] for row in range(len(classes)) if row != index)
        false_negative = sum(matrix[index][column] for column in range(len(classes)) if column != index)
        support = sum(matrix[index])
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        f1_values.append(f1)
        per_class[class_name] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
    return {
        "accuracy": sum(matrix[index][index] for index in range(len(classes))) / len(labels),
        "macro_f1": sum(f1_values) / len(f1_values),
        "per_class": per_class,
        "confusion_matrix": matrix,
    }


def loader(root: Path, image_size: int, batch_size: int, train: bool, seed: int) -> DataLoader:
    weights = MobileNet_V3_Small_Weights.DEFAULT
    preprocessing = weights.transforms()
    normalization = transforms.Normalize(mean=preprocessing.mean, std=preprocessing.std)
    if train:
        transform = transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
                transforms.ToTensor(),
                normalization,
            ]
        )
    else:
        transform = transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                normalization,
            ]
        )
    dataset = datasets.ImageFolder(root, transform=transform)
    generator = torch.Generator().manual_seed(seed)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=train,
        num_workers=0,
        generator=generator,
    )


def evaluate(model: nn.Module, data: DataLoader, criterion: nn.Module) -> dict:
    model.eval()
    labels, predictions = [], []
    loss_total = 0.0
    started = time.perf_counter()
    with torch.inference_mode():
        for images, target in data:
            logits = model(images)
            loss_total += float(criterion(logits, target).item()) * len(target)
            labels.extend(target.tolist())
            predictions.extend(logits.argmax(dim=1).tolist())
    elapsed = time.perf_counter() - started
    metrics = classification_metrics(labels, predictions, data.dataset.classes)
    return {
        "loss": loss_total / len(labels),
        **metrics,
        "elapsed_seconds": elapsed,
        "latency_ms_per_image": 1000 * elapsed / len(labels),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--image-size", type=int, default=160)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=20260823)
    args = parser.parse_args()
    if args.run_dir.exists():
        raise FileExistsError(f"Refusing to overwrite run directory: {args.run_dir}")
    set_seed(args.seed)
    args.run_dir.mkdir(parents=True)
    train_loader = loader(args.data / "train", args.image_size, args.batch_size, True, args.seed)
    val_loader = loader(args.data / "val", args.image_size, args.batch_size, False, args.seed)
    test_loader = loader(args.data / "test", args.image_size, args.batch_size, False, args.seed)
    if not (
        train_loader.dataset.classes == val_loader.dataset.classes == test_loader.dataset.classes
    ):
        raise ValueError("Class directory mappings differ across splits")

    weights = MobileNet_V3_Small_Weights.DEFAULT
    model = mobilenet_v3_small(weights=weights)
    for parameter in model.features.parameters():
        parameter.requires_grad = False
    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, len(train_loader.dataset.classes))
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        (parameter for parameter in model.parameters() if parameter.requires_grad),
        lr=args.learning_rate,
        weight_decay=1e-4,
    )

    history = []
    best_f1 = -1.0
    best_state = None
    started = time.perf_counter()
    for epoch in range(1, args.epochs + 1):
        model.train()
        model.features.eval()
        train_loss = 0.0
        labels, predictions = [], []
        for images, target in train_loader:
            optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, target)
            loss.backward()
            optimizer.step()
            train_loss += float(loss.item()) * len(target)
            labels.extend(target.tolist())
            predictions.extend(logits.argmax(dim=1).tolist())
        training_metrics = classification_metrics(labels, predictions, train_loader.dataset.classes)
        validation = evaluate(model, val_loader, criterion)
        epoch_record = {
            "epoch": epoch,
            "train_loss": train_loss / len(labels),
            "train_accuracy": training_metrics["accuracy"],
            "train_macro_f1": training_metrics["macro_f1"],
            "validation_loss": validation["loss"],
            "validation_accuracy": validation["accuracy"],
            "validation_macro_f1": validation["macro_f1"],
        }
        history.append(epoch_record)
        print(json.dumps(epoch_record))
        if validation["macro_f1"] > best_f1:
            best_f1 = validation["macro_f1"]
            best_state = copy.deepcopy(model.state_dict())

    if best_state is None:
        raise RuntimeError("Training produced no checkpoint")
    model.load_state_dict(best_state)
    checkpoint_path = args.run_dir / "best.pt"
    torch.save(
        {
            "model": "mobilenet_v3_small",
            "weights": "MobileNet_V3_Small_Weights.DEFAULT",
            "classes": train_loader.dataset.classes,
            "image_size": args.image_size,
            "state_dict": best_state,
        },
        checkpoint_path,
    )
    test = evaluate(model, test_loader, criterion)
    elapsed = time.perf_counter() - started
    report = {
        "schema_version": 1,
        "status": "RESEARCH_CANDIDATE_NOT_PROMOTED",
        "dataset_version": "sids-general-insect-classification-v1.0",
        "task": "coarse-general-insect-classification",
        "classes": train_loader.dataset.classes,
        "architecture": "torchvision mobilenet_v3_small frozen feature extractor",
        "pretrained_weights": "MobileNet_V3_Small_Weights.DEFAULT",
        "seed": args.seed,
        "epochs": args.epochs,
        "image_size": args.image_size,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "device": "cpu",
        "elapsed_seconds": elapsed,
        "history": history,
        "best_validation_macro_f1": best_f1,
        "test": test,
        "checkpoint": str(checkpoint_path),
        "checkpoint_bytes": checkpoint_path.stat().st_size,
        "checkpoint_sha256": __import__("hashlib").sha256(checkpoint_path.read_bytes()).hexdigest(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "torchvision": torchvision.__version__,
        },
        "promotion": {
            "allowed": False,
            "reason": (
                "Closed-set agricultural classification has no household-scene or unknown/OOD gate; "
                "the Python production runtime also has no approved classifier contract"
            ),
        },
        "limitations": [
            "BAU labels are coarse folders, not verified species.",
            "The deduplicated test has only 9-10 images per class.",
            "No household scenes, random objects, or unknown insects are included in this classifier test.",
        ],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (args.run_dir / "history.json").write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"test_macro_f1": test["macro_f1"], "test_accuracy": test["accuracy"]}))


if __name__ == "__main__":
    main()
