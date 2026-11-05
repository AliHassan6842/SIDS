"""
Module 4: Knowledge Distillation & Weight Generation Pipeline
==============================================================
Author: SIDS AI Research & Engineering Tutor Team
Target: Learn how to transfer knowledge from a heavy Teacher model
        to a compact Student model using Temperature Scaling, KL-Divergence,
        and generate deployable .pt weight files with SHA-256 verification.

Run:
    python ml/tutorials/04_knowledge_distillation_pipeline.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F


# =====================================================================
# 1. Models: Heavy Teacher vs Compact Student
# =====================================================================

class TeacherPestModel(nn.Module):
    """
    Simulates a heavy foundation model (e.g. ResNet-101 / Qwen-VL Backbone)
    with deep capacity and large channel widths.
    """

    def __init__(self, num_classes: int = 4) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.features(x).flatten(1)
        return self.classifier(feat)


class StudentEdgeModel(nn.Module):
    """
    Compact edge model designed for budget smartphones (< 10 MB, low RAM).
    Much smaller channel widths (16 -> 32 -> 64).
    """

    def __init__(self, num_classes: int = 4) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(16),
            nn.SiLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.SiLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.SiLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Linear(64, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.features(x).flatten(1)
        return self.classifier(feat)


# =====================================================================
# 2. Knowledge Distillation Loss Function (Hinton Loss)
# =====================================================================

class DistillationLoss(nn.Module):
    """
    Computes total distillation loss combining:
      1. Student Hard Loss (Standard Cross-Entropy with true labels)
      2. Soft Knowledge Loss (Kullback-Leibler Divergence with Teacher softened by Temperature tau)
    """

    def __init__(self, temperature: float = 4.0, alpha: float = 0.3) -> None:
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.kl_div = nn.KLDivLoss(reduction="batchmean")
        self.ce_loss = nn.CrossEntropyLoss()

    def forward(
        self, student_logits: torch.Tensor, teacher_logits: torch.Tensor, labels: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # 1. Hard Cross-Entropy Loss
        loss_hard = self.ce_loss(student_logits, labels)

        # 2. Soft Knowledge Loss with Temperature Scaling
        # Log-Softmax on Student, Softmax on Teacher
        soft_student = F.log_softmax(student_logits / self.temperature, dim=1)
        soft_teacher = F.softmax(teacher_logits / self.temperature, dim=1)

        # Scale by tau^2 to match gradient magnitudes
        loss_soft = self.kl_div(soft_student, soft_teacher) * (self.temperature ** 2)

        # Combined Weighted Loss
        total_loss = (self.alpha * loss_hard) + ((1.0 - self.alpha) * loss_soft)
        return total_loss, loss_hard, loss_soft


# =====================================================================
# 3. Training & Weight Generation Pipeline
# =====================================================================

def compute_file_sha256(filepath: Path) -> str:
    """Computes SHA-256 checksum to verify model weight artifact integrity."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> None:
    print("============================================================")
    print("  SIDS MACHINE LEARNING MASTERCLASS - MODULE 4 EXECUTION    ")
    print("============================================================")

    # 1. Instantiate Teacher and Student
    print("\n--- 1. Model Parameter Comparison ---")
    teacher = TeacherPestModel(num_classes=4)
    student = StudentEdgeModel(num_classes=4)

    teacher_params = sum(p.numel() for p in teacher.parameters())
    student_params = sum(p.numel() for p in student.parameters())

    print(f"-> Teacher Parameters: {teacher_params:,} (~{teacher_params * 4 / 1024:.1f} KB)")
    print(f"-> Student Parameters: {student_params:,} (~{student_params * 4 / 1024:.1f} KB)")
    print(f"-> Size Reduction:     {teacher_params / student_params:.1f}x smaller for edge devices!")

    # 2. Demonstrate Temperature Scaling Effect
    print("\n--- 2. Temperature Scaling & 'Dark Knowledge' Demo ---")
    raw_teacher_logits = torch.tensor([[8.5, 2.1, 0.4, -1.2]])
    sharp_probs = F.softmax(raw_teacher_logits / 1.0, dim=1)
    soft_probs = F.softmax(raw_teacher_logits / 4.0, dim=1)

    print(f"-> Raw Teacher Logits: {raw_teacher_logits.tolist()[0]}")
    print(f"-> Sharp Softmax (T=1.0): {[round(p, 4) for p in sharp_probs.tolist()[0]]} (Secondary classes nearly zero!)")
    print(f"-> Softened Softmax (T=4.0): {[round(p, 4) for p in soft_probs.tolist()[0]]} (Reveals inter-class similarity!)")

    # 3. Simulate Knowledge Distillation Training Loop
    print("\n--- 3. Running Knowledge Distillation Training Loop ---")
    teacher.eval()  # Teacher weights are frozen
    student.train()

    optimizer = torch.optim.Adam(student.parameters(), lr=1e-3)
    criterion = DistillationLoss(temperature=4.0, alpha=0.3)

    # Create synthetic batch: 4 images [4, 3, 128, 128] and targets
    dummy_x = torch.randn(4, 3, 128, 128)
    dummy_y = torch.tensor([0, 1, 1, 2], dtype=torch.long)

    for epoch in range(1, 4):
        optimizer.zero_grad()

        # Step A: Get Teacher prediction (no gradients needed for teacher)
        with torch.no_grad():
            teacher_logits = teacher(dummy_x)

        # Step B: Get Student prediction
        student_logits = student(dummy_x)

        # Step C: Compute distillation loss
        loss_total, loss_hard, loss_soft = criterion(student_logits, teacher_logits, dummy_y)

        # Step D: Backpropagate and update student weights
        loss_total.backward()
        optimizer.step()

        print(f"   Epoch {epoch}/3 | Total Loss: {loss_total.item():.4f} (Hard: {loss_hard.item():.4f}, Soft KD: {loss_soft.item():.4f})")

    # 4. Save and Craft the Distilled Weight Checkpoint (.pt)
    print("\n--- 4. Crafting & Saving Deployable Weights (.pt) ---")
    output_dir = Path("d:/vs code/uniSIDS/FinalYearProject/scratch/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    weights_path = output_dir / "sids-distilled-student-v1.0.pt"

    checkpoint = {
        "model_id": "sids-student-distilled",
        "version": "1.0.0",
        "architecture": "StudentEdgeModel",
        "num_classes": 4,
        "classes": ["rice-leaf-roller", "rice-water-weevil", "ladybird-beetle", "healthy-leaf"],
        "state_dict": student.state_dict(),
        "temperature": 4.0,
        "alpha": 0.3,
    }

    torch.save(checkpoint, weights_path)
    sha256 = compute_file_sha256(weights_path)
    file_size_kb = weights_path.stat().st_size / 1024

    print(f"-> Successfully Saved Weights File: {weights_path.name}")
    print(f"-> File Size on Disk:               {file_size_kb:.2f} KB")
    print(f"-> Cryptographic SHA-256 Checksum:  {sha256}")

    # 5. Reload and Verify Weights for Inference
    print("\n--- 5. Reloading & Verifying Weights for Edge Inference ---")
    reloaded_student = StudentEdgeModel(num_classes=4)
    loaded_ckpt = torch.load(weights_path, weights_only=True)
    reloaded_student.load_state_dict(loaded_ckpt["state_dict"])
    reloaded_student.eval()

    test_input = torch.randn(1, 3, 128, 128)
    with torch.no_grad():
        test_pred = F.softmax(reloaded_student(test_input), dim=1)

    predicted_class_idx = test_pred.argmax(dim=1).item()
    predicted_class_name = loaded_ckpt["classes"][predicted_class_idx]
    confidence = test_pred[0, predicted_class_idx].item()

    print(f"-> Edge Inference Test Prediction: '{predicted_class_name}' with Confidence: {confidence*100:.2f}%")
    print("-> Verification: Distilled weights loaded and inference executed with zero errors!")

    print("\n" + "=" * 60)
    print("SUCCESS: Module 4 Knowledge Distillation Executed 100%!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
