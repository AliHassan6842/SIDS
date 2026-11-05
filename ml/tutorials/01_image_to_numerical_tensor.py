"""
Module 1: Image to Numerical Tensor & Spatial Mathematics
===========================================================
Author: SIDS AI Research & Engineering Tutor Team
Target: Learn how images become 3D/4D tensors, normalization math,
        coordinate conversion (VOC, COCO, YOLO), and body mask extraction.

Run:
    python ml/tutorials/01_image_to_numerical_tensor.py
"""

from __future__ import annotations

import numpy as np
import torch
from PIL import Image, ImageDraw


def step_1_create_synthetic_agri_image(width: int = 400, height: int = 400) -> Image.Image:
    """
    Simulates a camera capturing an agricultural leaf with a small insect.
    Returns a standard RGB PIL Image.
    """
    print("\n" + "=" * 60)
    print("STEP 1: Digital Image Creation & Channels")
    print("=" * 60)

    # Background: Green crop leaf (R=34, G=139, B=34)
    img = Image.new("RGB", (width, height), color=(34, 139, 34))
    draw = ImageDraw.Draw(img)

    # Draw leaf veins (lighter green)
    draw.line([(0, 200), (400, 200)], fill=(50, 180, 50), width=4)
    draw.line([(100, 200), (50, 50)], fill=(50, 180, 50), width=2)
    draw.line([(250, 200), (320, 350)], fill=(50, 180, 50), width=2)

    # Draw an insect body in the center: Brown/Black Beetle at [xmin=160, ymin=140, xmax=240, ymax=260]
    # Coordinates: xmin=160, ymin=140, xmax=240, ymax=260 (width=80, height=120)
    draw.ellipse([160, 140, 240, 260], fill=(101, 67, 33), outline=(0, 0, 0), width=2)

    # Insect head
    draw.ellipse([180, 120, 220, 150], fill=(40, 20, 10))

    print(f"-> Generated Synthetic Image Size: {img.size} (Width x Height)")
    print(f"-> Image Mode: {img.mode} (3 Color Channels: Red, Green, Blue)")
    return img


def step_2_numpy_matrix_representation(pil_img: Image.Image) -> np.ndarray:
    """
    Demonstrates how a PIL Image is represented as a NumPy 3D Matrix.
    """
    print("\n" + "=" * 60)
    print("STEP 2: NumPy Matrix Representation (H x W x C)")
    print("=" * 60)

    np_array = np.array(pil_img, dtype=np.uint8)
    h, w, c = np_array.shape

    print(f"-> NumPy Array Shape: {np_array.shape} (Height={h}, Width={w}, Channels={c})")
    print(f"-> Data Type: {np_array.dtype} (unsigned 8-bit integer: 0 to 255)")
    print(f"-> Memory Size: {np_array.nbytes} bytes ({np_array.nbytes / 1024:.2f} KB)")

    # Inspect a single pixel on the leaf background vs the insect body
    leaf_pixel = np_array[50, 50]  # y=50, x=50
    insect_pixel = np_array[200, 200]  # center of insect

    print(f"-> Sample Leaf Pixel [y=50, x=50]: R={leaf_pixel[0]}, G={leaf_pixel[1]}, B={leaf_pixel[2]}")
    print(f"-> Sample Insect Pixel [y=200, x=200]: R={insect_pixel[0]}, G={insect_pixel[1]}, B={insect_pixel[2]}")

    return np_array


def step_3_convert_to_pytorch_tensor_and_normalize(np_array: np.ndarray) -> torch.Tensor:
    """
    Converts HWC NumPy array to PyTorch BCHW Tensor and applies ImageNet Standardization.
    """
    print("\n" + "=" * 60)
    print("STEP 3: PyTorch Tensor Conversion & Normalization Math")
    print("=" * 60)

    # 1. Transpose from HWC (400, 400, 3) to CHW (3, 400, 400)
    # PyTorch layers expect Channels first!
    tensor_chw = torch.from_numpy(np_array).permute(2, 0, 1)
    print(f"-> Permuted PyTorch Shape (CHW): {tensor_chw.shape}")

    # 2. Convert from uint8 [0, 255] to float32 [0.0, 1.0]
    tensor_float = tensor_chw.to(dtype=torch.float32) / 255.0
    print(f"-> Float Scaled Range: Min={tensor_float.min():.4f}, Max={tensor_float.max():.4f}")

    # 3. Apply ImageNet Standardization: z = (x - mean) / std
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

    standardized_tensor = (tensor_float - mean) / std
    print(f"-> Standardized Mean per channel: {standardized_tensor.mean(dim=(1, 2))}")
    print(f"-> Standardized Std per channel:  {standardized_tensor.std(dim=(1, 2))}")

    # 4. Add Batch Dimension [B, C, H, W] for model inference
    batch_tensor = standardized_tensor.unsqueeze(0)  # Shape: [1, 3, 400, 400]
    print(f"-> Final Batch Tensor Shape for Neural Network (BCHW): {batch_tensor.shape}")

    return batch_tensor


def step_4_coordinate_geometry_and_formats(
    img_w: int, img_h: int, xmin: int, ymin: int, xmax: int, ymax: int
) -> dict[str, list[float]]:
    """
    Demonstrates conversion between Pascal VOC, COCO, and YOLO formats.
    """
    print("\n" + "=" * 60)
    print("STEP 4: Spatial Coordinates (Pascal VOC vs COCO vs YOLO)")
    print("=" * 60)

    # Format 1: Pascal VOC [xmin, ymin, xmax, ymax]
    voc_box = [float(xmin), float(ymin), float(xmax), float(ymax)]

    # Format 2: COCO [xmin, ymin, width, height]
    box_w = float(xmax - xmin)
    box_h = float(ymax - ymin)
    coco_box = [float(xmin), float(ymin), box_w, box_h]

    # Format 3: YOLO [center_x, center_y, norm_w, norm_h] (all normalized to 0.0 - 1.0)
    center_x = (xmin + xmax) / 2.0 / img_w
    center_y = (ymin + ymax) / 2.0 / img_h
    norm_w = box_w / img_w
    norm_h = box_h / img_h
    yolo_box = [center_x, center_y, norm_w, norm_h]

    print(f"1. Pascal VOC Format [xmin, ymin, xmax, ymax]:\n   {voc_box}")
    print(f"2. COCO Format       [xmin, ymin, width, height]:\n   {coco_box}")
    print(f"3. YOLO Format       [center_x, center_y, norm_w, norm_h]:\n   {yolo_box}")

    # Reverse calculation: Prove YOLO converts back to absolute pixels accurately!
    calc_xmin = (center_x - norm_w / 2.0) * img_w
    calc_xmax = (center_x + norm_w / 2.0) * img_w
    calc_ymin = (center_y - norm_h / 2.0) * img_h
    calc_ymax = (center_y + norm_h / 2.0) * img_h

    print(f"-> Reconstructed Pascal VOC from YOLO: [{calc_xmin:.1f}, {calc_ymin:.1f}, {calc_xmax:.1f}, {calc_ymax:.1f}]")
    assert abs(calc_xmin - xmin) < 1e-4 and abs(calc_ymax - ymax) < 1e-4, "Reconstruction error!"
    print("-> Verification: Reverse calculation matches exact ground truth pixels 100%!")

    return {"voc": voc_box, "coco": coco_box, "yolo": yolo_box}


def step_5_instance_mask_hadamard_isolation(np_array: np.ndarray, xmin: int, ymin: int, xmax: int, ymax: int) -> np.ndarray:
    """
    Demonstrates Instance Segmentation: Isolating body pixels using a binary mask (Hadamard product).
    """
    print("\n" + "=" * 60)
    print("STEP 5: Instance Segmentation Mask & Background Elimination")
    print("=" * 60)

    h, w, c = np_array.shape

    # Create an empty binary mask (Height x Width) of zeros
    binary_mask = np.zeros((h, w), dtype=np.uint8)

    # Generate an elliptical body mask matching our insect body
    # (x - h_c)^2 / a^2 + (y - k_c)^2 / b^2 <= 1
    y_indices, x_indices = np.ogrid[:h, :w]
    center_x = (xmin + xmax) / 2.0
    center_y = (ymin + ymax) / 2.0
    semi_axis_x = (xmax - xmin) / 2.0
    semi_axis_y = (ymax - ymin) / 2.0

    ellipse_condition = ((x_indices - center_x) ** 2 / (semi_axis_x ** 2)) + (
        (y_indices - center_y) ** 2 / (semi_axis_y ** 2)
    ) <= 1.0
    binary_mask[ellipse_condition] = 1

    insect_pixels_count = int(np.sum(binary_mask))
    total_pixels = h * w
    percentage = (insect_pixels_count / total_pixels) * 100

    print(f"-> Total Image Pixels:    {total_pixels}")
    print(f"-> Insect Body Pixels:    {insect_pixels_count} ({percentage:.2f}% of total image)")
    print(f"-> Background Pixels:     {total_pixels - insect_pixels_count} (Eliminated)")

    # Mathematical Hadamard Product: Image * Mask (broadcasting mask across 3 RGB channels)
    # Background leaf pixels become (0, 0, 0) pure black!
    mask_3d = np.expand_dims(binary_mask, axis=2)  # Shape: [H, W, 1]
    isolated_insect_matrix = np_array * mask_3d    # Shape: [H, W, 3]

    print(f"-> Isolated Insect Matrix Shape: {isolated_insect_matrix.shape}")
    print(f"-> Corner Pixel (Background Leaf) before: {np_array[0, 0]} -> after mask: {isolated_insect_matrix[0, 0]}")
    print(f"-> Center Pixel (Insect Body)   before: {np_array[int(center_y), int(center_x)]} -> after mask: {isolated_insect_matrix[int(center_y), int(center_x)]}")
    print("-> Result: Background leaves completely zeroed out. Zero background noise for the AI model!")

    return isolated_insect_matrix


def main() -> None:
    print("============================================================")
    print("  SIDS MACHINE LEARNING MASTERCLASS - MODULE 1 EXECUTION    ")
    print("============================================================")

    # Step 1: Create Image
    img = step_1_create_synthetic_agri_image(width=400, height=400)

    # Step 2: Convert to NumPy
    np_array = step_2_numpy_matrix_representation(img)

    # Step 3: Convert to PyTorch Tensor & Normalize
    _ = step_3_convert_to_pytorch_tensor_and_normalize(np_array)

    # Step 4: Spatial Coordinates & Box Formats
    # Insect coordinates inside the synthetic image
    xmin, ymin, xmax, ymax = 160, 140, 240, 260
    _ = step_4_coordinate_geometry_and_formats(400, 400, xmin, ymin, xmax, ymax)

    # Step 5: Instance Segmentation & Hadamard Product
    _ = step_5_instance_mask_hadamard_isolation(np_array, xmin, ymin, xmax, ymax)

    print("\n" + "=" * 60)
    print("SUCCESS: Module 1 Numerical Pipeline Executed Perfectly!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
