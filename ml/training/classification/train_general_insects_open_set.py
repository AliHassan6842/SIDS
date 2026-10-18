"""Train a bounded four-way model with an internal, never-emitted unknown class."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import random
import time
from pathlib import Path

import numpy as np
import torch
import torchvision
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from torchvision import datasets, transforms
from torchvision.models import mobilenet_v3_small


CLASSES = ["beetle", "grasshopper", "mosquito", "unknown-insect"]


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def transform(image_size: int, train: bool) -> transforms.Compose:
    operations: list = [transforms.Resize((image_size, image_size))]
    if train:
        operations.extend(
            [
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(8),
                transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
            ]
        )
    operations.extend(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    return transforms.Compose(operations)


class OpenSetDataset(Dataset):
    def __init__(self, known_root: Path, unknown_root: Path, image_size: int, train: bool):
        known = datasets.ImageFolder(known_root)
        if known.classes != CLASSES[:3]:
            raise ValueError(f"Unexpected known classes: {known.classes}")
        self.samples = [(Path(path), label) for path, label in known.samples]
        self.samples.extend(
            (path, 3)
            for path in sorted(unknown_root.rglob("*"))
            if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
        )
        self.transform = transform(image_size, train)
        self.targets = [label for _, label in self.samples]

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        path, label = self.samples[index]
        with Image.open(path) as source:
            image = self.transform(source.convert("RGB"))
        return image, label


def metrics(expected: list[int], predicted: list[int]) -> dict:
    matrix = [[0 for _ in CLASSES] for _ in CLASSES]
    for target, output in zip(expected, predicted):
        matrix[target][output] += 1
    per_class, f1s = {}, []
    for index, class_name in enumerate(CLASSES):
        tp = matrix[index][index]
        fp = sum(matrix[row][index] for row in range(len(CLASSES)) if row != index)
        fn = sum(matrix[index][column] for column in range(len(CLASSES)) if column != index)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        f1s.append(f1)
        per_class[class_name] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(matrix[index])}
    return {
        "accuracy": sum(matrix[index][index] for index in range(len(CLASSES))) / len(expected),
        "macro_f1": sum(f1s) / len(f1s),
        "per_class": per_class,
        "confusion_matrix": matrix,
    }


def evaluate(model: nn.Module, loader: DataLoader, criterion: nn.Module) -> dict:
    model.eval()
    expected, predicted, loss_total = [], [], 0.0
    with torch.inference_mode():
        for images, targets in loader:
            logits = model(images)
            loss_total += float(criterion(logits, targets).item()) * len(targets)
            expected.extend(targets.tolist())
            predicted.extend(logits.argmax(dim=1).tolist())
    return {"loss": loss_total / len(expected), **metrics(expected, predicted)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--initial-checkpoint", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--image-size", type=int, default=160)
    parser.add_argument("--learning-rate", type=float, default=5e-4)
    parser.add_argument("--seed", type=int, default=20260826)
    args = parser.parse_args()
    if args.run_dir.exists() or args.report.exists():
        raise FileExistsError("Refusing to overwrite an existing run or report")
    set_seed(args.seed)
    args.run_dir.mkdir(parents=True)
    train_data = OpenSetDataset(args.data / "train", args.data / "unknown/train", args.image_size, True)
    validation_data = OpenSetDataset(args.data / "val", args.data / "unknown/calibration", args.image_size, False)
    class_counts = np.bincount(train_data.targets, minlength=len(CLASSES))
    sample_weights = [1.0 / class_counts[target] for target in train_data.targets]
    generator = torch.Generator().manual_seed(args.seed)
    sampler = WeightedRandomSampler(sample_weights, len(train_data), replacement=True, generator=generator)
    train_loader = DataLoader(train_data, batch_size=args.batch_size, sampler=sampler, num_workers=0)
    validation_loader = DataLoader(validation_data, batch_size=args.batch_size, shuffle=False, num_workers=0)

    prior = torch.load(args.initial_checkpoint, map_location="cpu", weights_only=True)
    model = mobilenet_v3_small(weights=None)
    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, len(CLASSES))
    prior_state = prior["state_dict"]
    compatible = {key: value for key, value in prior_state.items() if not key.startswith("classifier.3")}
    model.load_state_dict(compatible, strict=False)
    with torch.no_grad():
        model.classifier[-1].weight[:3].copy_(prior_state["classifier.3.weight"])
        model.classifier[-1].bias[:3].copy_(prior_state["classifier.3.bias"])
    for parameter in model.features.parameters():
        parameter.requires_grad = False
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        (parameter for parameter in model.parameters() if parameter.requires_grad),
        lr=args.learning_rate,
        weight_decay=1e-4,
    )
    best_f1, best_state, history = -1.0, None, []
    started = time.perf_counter()
    for epoch in range(1, args.epochs + 1):
        model.train()
        model.features.eval()
        expected, predicted, loss_total = [], [], 0.0
        for images, targets in train_loader:
            optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()
            loss_total += float(loss.item()) * len(targets)
            expected.extend(targets.tolist())
            predicted.extend(logits.argmax(dim=1).tolist())
        validation = evaluate(model, validation_loader, criterion)
        row = {
            "epoch": epoch,
            "train_loss": loss_total / len(expected),
            "train_macro_f1": metrics(expected, predicted)["macro_f1"],
            "validation_loss": validation["loss"],
            "validation_macro_f1": validation["macro_f1"],
        }
        history.append(row)
        print(json.dumps(row), flush=True)
        if validation["macro_f1"] > best_f1:
            best_f1 = validation["macro_f1"]
            best_state = copy.deepcopy(model.state_dict())
    if best_state is None:
        raise RuntimeError("Training produced no checkpoint")
    checkpoint = args.run_dir / "best.pt"
    torch.save(
        {
            "model": "mobilenet_v3_small",
            "classes": CLASSES,
            "image_size": args.image_size,
            "state_dict": best_state,
            "internal_unknown_index": 3,
        },
        checkpoint,
    )
    report = {
        "schema_version": 1,
        "status": "OPEN_SET_CANDIDATE_NOT_TESTED_NOT_PROMOTED",
        "dataset_version": "sids-general-insect-classification-v1.2",
        "classes": CLASSES,
        "internal_unknown_index": 3,
        "seed": args.seed,
        "epochs": args.epochs,
        "image_size": args.image_size,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "elapsed_seconds": time.perf_counter() - started,
        "history": history,
        "best_validation_macro_f1": best_f1,
        "checkpoint": str(checkpoint),
        "checkpoint_bytes": checkpoint.stat().st_size,
        "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        "test_data_read": False,
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "torchvision": torchvision.__version__,
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"best_validation_macro_f1": best_f1, "test_data_read": False}), flush=True)


if __name__ == "__main__":
    main()
