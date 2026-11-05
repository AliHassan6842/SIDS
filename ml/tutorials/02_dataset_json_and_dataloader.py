"""
Module 2: Dataset Engineering, JSON Schemas & PyTorch DataLoaders
==================================================================
Author: SIDS AI Research & Engineering Tutor Team
Target: Learn how to construct COCO JSON annotations, write custom PyTorch
        Datasets and DataLoaders with variable-length collate functions,
        and simulate VLM Zero-Shot Auto-Labeling.

Run:
    python ml/tutorials/02_dataset_json_and_dataloader.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image, ImageDraw
from torch.utils.data import DataLoader, Dataset


def step_1_create_sample_dataset_files(data_dir: Path) -> list[dict[str, Any]]:
    """
    Creates 4 synthetic images representing different field & indoor scenarios:
      Img 1: Rice leaf with 2 pests (leaf-roller, water-weevil)
      Img 2: Cotton leaf with 1 beneficial predator (ladybird-beetle)
      Img 3: Indoor floor with 1 domestic bug (non-crop context)
      Img 4: Clean healthy wheat leaf (0 insects - hard negative sample)
    """
    print("\n" + "=" * 60)
    print("STEP 1: Generating Multi-Context Agricultural Samples")
    print("=" * 60)

    data_dir.mkdir(parents=True, exist_ok=True)
    images_dir = data_dir / "images"
    images_dir.mkdir(exist_ok=True)

    samples_meta = [
        {
            "id": 1,
            "filename": "rice_field_01.jpg",
            "bg_color": (34, 139, 34),  # Green canopy
            "context": "CROP_CANOPY",
            "crop": "rice",
            "insects": [
                {"label": "rice-leaf-roller", "cat_id": 1, "box": [80, 100, 160, 200], "role": "HARMFUL_PEST"},
                {"label": "rice-water-weevil", "cat_id": 2, "box": [220, 240, 300, 320], "role": "HARMFUL_PEST"},
            ],
        },
        {
            "id": 2,
            "filename": "cotton_field_02.jpg",
            "bg_color": (46, 125, 50),  # Cotton leaf
            "context": "CROP_CANOPY",
            "crop": "cotton",
            "insects": [
                {"label": "ladybird-beetle", "cat_id": 3, "box": [150, 150, 250, 250], "role": "BENEFICIAL_PREDATOR"}
            ],
        },
        {
            "id": 3,
            "filename": "indoor_kitchen_03.jpg",
            "bg_color": (210, 180, 140),  # Brown tile floor
            "context": "INDOOR_DOMESTIC",
            "crop": "none",
            "insects": [
                {"label": "ground-beetle", "cat_id": 4, "box": [180, 160, 240, 260], "role": "DOMESTIC_NON_CROP"}
            ],
        },
        {
            "id": 4,
            "filename": "healthy_wheat_04.jpg",
            "bg_color": (50, 160, 60),  # Clean wheat leaf
            "context": "CROP_CANOPY",
            "crop": "wheat",
            "insects": [],  # Zero insects (Hard Negative!)
        },
    ]

    for item in samples_meta:
        img = Image.new("RGB", (384, 384), color=item["bg_color"])
        draw = ImageDraw.Draw(img)

        # Draw insects
        for ins in item["insects"]:
            box = ins["box"]
            color = (139, 69, 19) if "beetle" in ins["label"] else (70, 70, 70)
            draw.ellipse(box, fill=color, outline=(0, 0, 0), width=2)
            draw.text((box[0], box[1] - 12), ins["label"], fill=(255, 255, 255))

        img_path = images_dir / item["filename"]
        img.save(img_path, format="JPEG", quality=95)
        print(f"-> Created: {item['filename']} | Context={item['context']} | Bugs Count={len(item['insects'])}")

    return samples_meta


def step_2_build_coco_master_json(samples: list[dict[str, Any]], output_file: Path) -> dict[str, Any]:
    """
    Constructs an official COCO-compliant JSON file.
    """
    print("\n" + "=" * 60)
    print("STEP 2: Building Microsoft COCO Master JSON Schema")
    print("=" * 60)

    categories = [
        {"id": 1, "name": "rice-leaf-roller", "supercategory": "pest"},
        {"id": 2, "name": "rice-water-weevil", "supercategory": "pest"},
        {"id": 3, "name": "ladybird-beetle", "supercategory": "beneficial"},
        {"id": 4, "name": "ground-beetle", "supercategory": "domestic"},
    ]

    images_entry = []
    annotations_entry = []
    ann_id = 1

    for sample in samples:
        images_entry.append({
            "id": sample["id"],
            "file_name": sample["filename"],
            "width": 384,
            "height": 384,
            "substrate_context": sample["context"],
            "crop": sample["crop"],
        })

        for ins in sample["insects"]:
            box = ins["box"]
            xmin, ymin, xmax, ymax = box
            w = float(xmax - xmin)
            h = float(ymax - ymin)
            annotations_entry.append({
                "id": ann_id,
                "image_id": sample["id"],
                "category_id": ins["cat_id"],
                "bbox": [float(xmin), float(ymin), w, h],  # COCO format: [xmin, ymin, w, h]
                "area": float(w * h),
                "iscrowd": 0,
                "biological_role": ins["role"],
            })
            ann_id += 1

    coco_data = {
        "info": {"description": "SIDS Master Agricultural Pest & Context Dataset", "version": "1.0"},
        "categories": categories,
        "images": images_entry,
        "annotations": annotations_entry,
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(coco_data, f, indent=2)

    print(f"-> Saved COCO JSON to: {output_file}")
    print(f"-> Total Images Registered:      {len(images_entry)}")
    print(f"-> Total Bounding Box Instances: {len(annotations_entry)}")
    return coco_data


def step_3_vlm_zero_shot_autolabeler_simulation(img_path: Path) -> dict[str, Any]:
    """
    Demonstrates how a Large Vision-Language Model (Qwen2.5-VL / BioCLIP)
    is prompted to generate structured pseudo-labels without human annotation.
    """
    print("\n" + "=" * 60)
    print("STEP 3: Simulating VLM (Qwen2.5-VL) Zero-Shot Auto-Labeling")
    print("=" * 60)

    # In production, this sends the image to Qwen2.5-VL / Claude with a strict schema prompt
    # Here we show the exact parsed response structure returned by the model:
    simulated_vlm_response = {
        "image_file": img_path.name,
        "scene_analysis": {
            "substrate": "CROP_CANOPY",
            "detected_crop": "cotton",
            "leaf_health": "slight_chlorosis_spots",
        },
        "identified_entities": [
            {
                "taxon_name": "Coccinellidae (Ladybird Beetle)",
                "common_slug": "ladybird-beetle",
                "biological_role": "BENEFICIAL_PREDATOR",
                "food_source": "Eats aphids and whitefly nymphs",
                "bbox_voc_normalized": [0.39, 0.39, 0.65, 0.65],
                "confidence": 0.962,
            }
        ],
        "safety_action": "DO_NOT_SPRAY_BENEFICIAL_PRESENT",
    }

    print("Prompt Sent to VLM: 'Analyze leaf, detect insects, output strictly JSON with bbox & biological status'")
    print("-> Raw VLM JSON Output Received:")
    print(json.dumps(simulated_vlm_response, indent=2))
    return simulated_vlm_response


class SidsAgriPestDataset(Dataset):
    """
    Custom PyTorch Dataset that loads images and parses COCO annotations.
    """

    def __init__(self, data_dir: Path, coco_json_path: Path) -> None:
        self.images_dir = data_dir / "images"
        with open(coco_json_path, encoding="utf-8") as f:
            self.coco = json.load(f)

        self.images_map = {img["id"]: img for img in self.coco["images"]}
        self.annotations_by_image: dict[int, list[dict[str, Any]]] = {img["id"]: [] for img in self.coco["images"]}

        for ann in self.coco["annotations"]:
            self.annotations_by_image[ann["image_id"]].append(ann)

        self.image_ids = list(self.images_map.keys())

    def __len__(self) -> int:
        return len(self.image_ids)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, dict[str, Any]]:
        img_id = self.image_ids[index]
        img_info = self.images_map[img_id]
        img_path = self.images_dir / img_info["file_name"]

        # Load image via PIL and convert to tensor [3, H, W]
        pil_img = Image.open(img_path).convert("RGB")
        img_tensor = torch.from_numpy(np.array(pil_img)).permute(2, 0, 1).float() / 255.0

        # Extract target annotations
        anns = self.annotations_by_image[img_id]
        boxes = []
        labels = []
        roles = []

        for ann in anns:
            xmin, ymin, w, h = ann["bbox"]
            boxes.append([xmin, ymin, xmin + w, ymin + h])  # Pascal VOC format: [xmin, ymin, xmax, ymax]
            labels.append(ann["category_id"])
            roles.append(ann["biological_role"])

        target = {
            "image_id": torch.tensor([img_id]),
            "boxes": torch.as_tensor(boxes, dtype=torch.float32) if boxes else torch.zeros((0, 4), dtype=torch.float32),
            "labels": torch.as_tensor(labels, dtype=torch.int64) if labels else torch.zeros((0,), dtype=torch.int64),
            "substrate_context": img_info["substrate_context"],
            "crop": img_info["crop"],
            "num_insects": len(boxes),
        }

        return img_tensor, target


def detection_collate_fn(batch: list[tuple[torch.Tensor, dict[str, Any]]]) -> tuple[torch.Tensor, list[dict[str, Any]]]:
    """
    CRITICAL LESSON: How PyTorch handles variable-length bounding boxes.
    Stacks images into [B, 3, H, W], while preserving targets as a list of dictionaries.
    """
    images, targets = zip(*batch)
    stacked_images = torch.stack(images, dim=0)  # Shape: [B, 3, H, W]
    return stacked_images, list(targets)


def step_4_pytorch_dataloader_execution(data_dir: Path, coco_json_path: Path) -> None:
    """
    Executes the PyTorch Dataset and DataLoader with batch size 2.
    """
    print("\n" + "=" * 60)
    print("STEP 4: PyTorch Custom Dataset & DataLoader Batch Execution")
    print("=" * 60)

    dataset = SidsAgriPestDataset(data_dir, coco_json_path)
    print(f"-> Initialized Dataset with {len(dataset)} items.")

    # Create DataLoader with batch_size=2 and custom collate_fn
    loader = DataLoader(dataset, batch_size=2, shuffle=True, collate_fn=detection_collate_fn)

    print(f"-> DataLoader Batch Size: 2 | Total Batches: {len(loader)}")

    for batch_idx, (batch_images, batch_targets) in enumerate(loader):
        print(f"\n--- Processing Batch {batch_idx + 1} ---")
        print(f"  Batch Images Tensor Shape: {batch_images.shape} (BCHW: [Batch, Channels, Height, Width])")
        for i, target in enumerate(batch_targets):
            print(
                f"  Item {i+1}: Image ID={target['image_id'].item()} | "
                f"Context={target['substrate_context']} | "
                f"Crop={target['crop']} | "
                f"Boxes Count={target['num_insects']} | "
                f"Boxes Shape={target['boxes'].shape}"
            )


def main() -> None:
    print("============================================================")
    print("  SIDS MACHINE LEARNING MASTERCLASS - MODULE 2 EXECUTION    ")
    print("============================================================")

    scratch_dir = Path("d:/vs code/uniSIDS/FinalYearProject/scratch/tutorial_data")
    coco_json_path = scratch_dir / "annotations" / "sids_pest_coco.json"

    # 1. Create sample dataset
    samples = step_1_create_sample_dataset_files(scratch_dir)

    # 2. Build COCO JSON
    _ = step_2_build_coco_master_json(samples, coco_json_path)

    # 3. Simulate VLM Auto-Labeling
    _ = step_3_vlm_zero_shot_autolabeler_simulation(scratch_dir / "images" / "cotton_field_02.jpg")

    # 4. Execute PyTorch DataLoader
    step_4_pytorch_dataloader_execution(scratch_dir, coco_json_path)

    print("\n" + "=" * 60)
    print("SUCCESS: Module 2 Dataset & DataLoader Pipeline Executed 100%!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
