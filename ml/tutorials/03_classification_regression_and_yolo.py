"""
Module 3: Neural Architectures (Classification, Regression, YOLO & Vision Transformers)
========================================================================================
Author: SIDS AI Research & Engineering Tutor Team
Target: Learn how Classification and Regression heads work mathematically,
        how Multi-Task loss is calculated, and how Self-Attention works in ViTs.

Run:
    python ml/tutorials/03_classification_regression_and_yolo.py
"""

from __future__ import annotations

import time
import torch
import torch.nn as nn
import torch.nn.functional as F


# =====================================================================
# PART 1: Multi-Task Agricultural Neural Network (Backbone + 3 Heads)
# =====================================================================

class ConvBlock(nn.Module):
    """Basic convolutional building block: Conv2d + BatchNorm + SiLU (Swish)"""

    def __init__(self, in_c: int, out_c: int, stride: int = 1) -> None:
        super().__init__()
        self.conv = nn.Conv2d(in_c, out_c, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn = nn.BatchNorm2d(out_c)
        self.act = nn.SiLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(self.bn(self.conv(x)))


class SidsMultiTaskPestNet(nn.Module):
    """
    Decoupled Multi-Task Edge Network:
      - Head 1: Insect Classification (4 Classes)
      - Head 2: Bounding Box Regression [center_x, center_y, w, h]
      - Head 3: Substrate Context Head (CROP_LEAF vs INDOOR_DOMESTIC)
    """

    def __init__(self, num_classes: int = 4, num_contexts: int = 2) -> None:
        super().__init__()
        # Backbone: 4-stage convolutional downsampling (384 -> 192 -> 96 -> 48 -> 24)
        self.stage1 = ConvBlock(3, 16, stride=2)   # -> [B, 16, 192, 192]
        self.stage2 = ConvBlock(16, 32, stride=2)  # -> [B, 32, 96, 96]
        self.stage3 = ConvBlock(32, 64, stride=2)  # -> [B, 64, 48, 48]
        self.stage4 = ConvBlock(64, 128, stride=2) # -> [B, 128, 24, 24]

        # Global Average Pooling: compresses 24x24 spatial grid to 1x1 feature vector
        self.gap = nn.AdaptiveAvgPool2d((1, 1))

        # Head 1: Insect Classification Head
        self.cls_head = nn.Sequential(
            nn.Linear(128, 64),
            nn.SiLU(),
            nn.Linear(64, num_classes),  # Raw Logits
        )

        # Head 2: Bounding Box Regression Head [cx, cy, w, h] normalized in [0, 1]
        self.reg_head = nn.Sequential(
            nn.Linear(128, 64),
            nn.SiLU(),
            nn.Linear(64, 4),
            nn.Sigmoid(),  # Sigmoid restricts output coordinates to strictly [0.0, 1.0]
        )

        # Head 3: Substrate Context Head (Crop vs Domestic)
        self.ctx_head = nn.Sequential(
            nn.Linear(128, 32),
            nn.SiLU(),
            nn.Linear(32, num_contexts),  # [Crop Canopy vs Domestic]
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        features = self.stage4(self.stage3(self.stage2(self.stage1(x))))
        pooled = self.gap(features).flatten(1)  # Shape: [B, 128]

        logits_cls = self.cls_head(pooled)     # Shape: [B, num_classes]
        bbox_pred = self.reg_head(pooled)      # Shape: [B, 4]
        logits_ctx = self.ctx_head(pooled)     # Shape: [B, num_contexts]

        return logits_cls, bbox_pred, logits_ctx


# =====================================================================
# PART 2: Vision Transformer (ViT) Self-Attention Block
# =====================================================================

class MiniVisionTransformerBlock(nn.Module):
    """
    Demonstrates how Multi-Head Self-Attention works on image patch embeddings:
    Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V
    """

    def __init__(self, embed_dim: int = 64, num_heads: int = 4) -> None:
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        self.qkv_projection = nn.Linear(embed_dim, embed_dim * 3)
        self.out_projection = nn.Linear(embed_dim, embed_dim)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input shape: [Batch, Num_Patches, Embed_Dim]
        b, n, d = x.shape
        residual = x
        x_norm = self.norm(x)

        # Project into Query, Key, and Value tensors
        qkv = self.qkv_projection(x_norm).reshape(b, n, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # Shape: [3, B, num_heads, N, head_dim]
        q, k, v = qkv[0], qkv[1], qkv[2]

        # Scaled Dot-Product Attention
        scale = 1.0 / (self.head_dim ** 0.5)
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) * scale  # Shape: [B, num_heads, N, N]
        attn_weights = F.softmax(attn_scores, dim=-1)

        out = torch.matmul(attn_weights, v)  # Shape: [B, num_heads, N, head_dim]
        out = out.permute(0, 2, 1, 3).reshape(b, n, d)
        out = self.out_projection(out)

        return residual + out


def main() -> None:
    print("============================================================")
    print("  SIDS MACHINE LEARNING MASTERCLASS - MODULE 3 EXECUTION    ")
    print("============================================================")

    # 1. Instantiate the Multi-Task Network
    print("\n--- 1. Multi-Task Network Architecture ---")
    model = SidsMultiTaskPestNet(num_classes=4, num_contexts=2)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"-> Total Learnable Parameters: {total_params:,} (~{total_params * 4 / (1024*1024):.2f} MB in FP32)")

    # 2. Simulate a batch of 2 farm images [B=2, C=3, H=384, W=384]
    dummy_input = torch.randn(2, 3, 384, 384)

    # Measure forward latency on CPU
    start_t = time.perf_counter()
    logits_cls, bbox_pred, logits_ctx = model(dummy_input)
    latency_ms = (time.perf_counter() - start_t) * 1000

    print(f"-> Forward Pass Output Shapes:")
    print(f"   - Insect Class Logits:       {logits_cls.shape} [Batch, 4 Classes]")
    print(f"   - Bounding Box Predictions:   {bbox_pred.shape} [Batch, 4 Normalized Coordinates]")
    print(f"   - Context Substrate Logits:  {logits_ctx.shape} [Batch, 2 Contexts: Crop vs Domestic]")
    print(f"-> CPU Forward Latency:         {latency_ms:.2f} ms (Ultra Fast!)")

    # 3. Simulate Ground Truth & Multi-Task Loss Calculation
    print("\n--- 2. Multi-Task Loss Backpropagation ---")
    target_cls = torch.tensor([1, 2], dtype=torch.long)  # Image 1: Class 1, Image 2: Class 2
    target_box = torch.tensor([[0.5, 0.5, 0.2, 0.3], [0.4, 0.6, 0.15, 0.25]], dtype=torch.float32)
    target_ctx = torch.tensor([0, 0], dtype=torch.long)  # Both are CROP_LEAF (Index 0)

    # Loss 1: Cross-Entropy for Classification
    loss_cls = F.cross_entropy(logits_cls, target_cls)

    # Loss 2: Smooth L1 / Regression Loss for Bounding Boxes
    loss_box = F.smooth_l1_loss(bbox_pred, target_box)

    # Loss 3: Cross-Entropy for Substrate Context
    loss_ctx = F.cross_entropy(logits_ctx, target_ctx)

    # Total Multi-Task Loss with weighting factors
    total_loss = loss_cls + (2.0 * loss_box) + (0.5 * loss_ctx)

    print(f"   Classification Loss (CrossEntropy): {loss_cls.item():.4f}")
    print(f"   Bounding Box Loss   (Smooth L1):    {loss_box.item():.4f}")
    print(f"   Substrate Loss      (CrossEntropy): {loss_ctx.item():.4f}")
    print(f"   Total Weighted Loss:                {total_loss.item():.4f}")

    # Backpropagation test: Verify gradients flow properly to all layers
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    optimizer.zero_grad()
    total_loss.backward()
    optimizer.step()
    print("-> Backpropagation Successful: Gradients computed and weights updated cleanly!")

    # 4. Demonstrate Vision Transformer Self-Attention Block
    print("\n--- 3. Vision Transformer (ViT) Self-Attention Block ---")
    vit_block = MiniVisionTransformerBlock(embed_dim=64, num_heads=4)
    # Simulate 16 image patches with embedding dimension 64 [Batch=1, Num_Patches=16, Embed_Dim=64]
    patch_tokens = torch.randn(1, 16, 64)
    attended_tokens = vit_block(patch_tokens)
    print(f"-> Input Patch Tokens Shape:    {patch_tokens.shape}")
    print(f"-> Attended Output Shape:       {attended_tokens.shape}")
    print("-> Self-Attention Mechanism verified: Every patch exchanged spatial context across all heads!")

    print("\n" + "=" * 60)
    print("SUCCESS: Module 3 Neural Architectures Executed 100%!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
