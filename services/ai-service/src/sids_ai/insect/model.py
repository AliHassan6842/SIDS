from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from sids_ai.registry.manifest import ModelManifest
from sids_ai.schemas import BoundingBox, Prediction


@dataclass(frozen=True)
class Detection:
    prediction: Prediction


class PestDetector:
    def __init__(self, manifest: ModelManifest) -> None:
        from ultralytics import YOLO

        self.manifest = manifest
        self._model: Any = YOLO(str(Path(manifest.artifact_path)))

    def identify(self, rgb: np.ndarray, crop_id: str) -> Detection | None:
        allowed = set(self.manifest.crop_classes.get(crop_id, []))
        if not allowed:
            return None
        # The bounded training set is strongly landscape-oriented. Normalize portrait
        # captures before inference so the same insect is not rejected only because a
        # phone stored it vertically. Bounding boxes are mapped back below.
        portrait_rotated = rgb.shape[0] > rgb.shape[1]
        inference_rgb = np.ascontiguousarray(np.rot90(rgb, k=3)) if portrait_rotated else rgb
        inference_height, inference_width = inference_rgb.shape[:2]
        crop_width = max(1, int(inference_width * 0.8))
        crop_height = max(1, int(inference_height * 0.8))
        crop_x = (inference_width - crop_width) // 2
        crop_y = (inference_height - crop_height) // 2
        views = [(inference_rgb, 0, 0)]
        if self.manifest.evaluation_summary.get("inference_views") == "FULL_PLUS_CENTER_80_PERCENT":
            views.append(
                (
                    np.ascontiguousarray(
                        inference_rgb[crop_y : crop_y + crop_height, crop_x : crop_x + crop_width]
                    ),
                    crop_x,
                    crop_y,
                )
            )
        # Ultralytics treats ndarray inputs as OpenCV/BGR. The decoder deliberately
        # produces RGB, so convert at this explicit runtime boundary.
        results = self._model.predict(
            source=[np.ascontiguousarray(view[..., ::-1]) for view, _, _ in views],
            imgsz=self.manifest.input_size,
            conf=0.01,
            verbose=False,
        )
        height, width = rgb.shape[:2]
        best: Prediction | None = None
        for result, (_, offset_x, offset_y) in zip(results, views, strict=True):
            for box in result.boxes:
                class_index = int(box.cls.item())
                slug = self.manifest.classes.get(class_index)
                confidence = float(box.conf.item())
                if slug not in allowed or confidence < self.manifest.acceptance_threshold:
                    continue
                x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]
                x1, x2 = x1 + offset_x, x2 + offset_x
                y1, y2 = y1 + offset_y, y2 + offset_y
                if portrait_rotated:
                    normalized_x = y1 / inference_height
                    normalized_y = 1.0 - (x2 / inference_width)
                    normalized_width = (y2 - y1) / inference_height
                    normalized_height = (x2 - x1) / inference_width
                else:
                    normalized_x = x1 / width
                    normalized_y = y1 / height
                    normalized_width = (x2 - x1) / width
                    normalized_height = (y2 - y1) / height
                candidate = Prediction(
                    pestId=slug,
                    confidence=confidence,
                    bbox=BoundingBox(
                        x=max(0.0, min(1.0, normalized_x)),
                        y=max(0.0, min(1.0, normalized_y)),
                        width=max(1 / width, min(1.0, normalized_width)),
                        height=max(1 / height, min(1.0, normalized_height)),
                    ),
                )
                if best is None or candidate.confidence > best.confidence:
                    best = candidate
        return Detection(best) if best is not None else None


class GeneralInsectClassifier:
    def __init__(self, manifest: ModelManifest) -> None:
        import torch
        from torchvision import transforms

        self.manifest = manifest
        self._device = torch.device("cpu")
        artifact_path = Path(manifest.artifact_path)
        if str(artifact_path).startswith("../"):
            # Resolve relative to ai-service directory
            service_root = Path(__file__).resolve().parent.parent.parent.parent
            artifact_path = service_root / artifact_path.relative_to("../")
        elif not artifact_path.is_absolute():
            # If not absolute, assume relative to cwd (or ai-service dir)
            artifact_path = Path.cwd() / artifact_path
            
        self._model = torch.jit.load(str(artifact_path), map_location=self._device)
        self._model.eval()
        self._transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(256),
            transforms.CenterCrop(manifest.input_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def identify(self, rgb: np.ndarray) -> Detection | None:
        import torch
        with torch.no_grad():
            tensor = self._transform(rgb).unsqueeze(0).to(self._device)
            output = self._model(tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
            # Find the top class
            prob, class_idx = torch.max(probabilities, dim=0)
            confidence = float(prob.item())
            class_index = int(class_idx.item())
            
            slug = self.manifest.classes.get(class_index)
            
            # If slug is not recognized, or confidence is below threshold, or it is explicitly unknown
            if not slug or slug == "unknown-insect" or confidence < self.manifest.acceptance_threshold:
                return None
                
            return Detection(
                prediction=Prediction(
                    pestId=slug,
                    confidence=confidence,
                    # Classification doesn't give a bounding box, so we return a default one encompassing the image
                    bbox=BoundingBox(x=0.0, y=0.0, width=1.0, height=1.0)
                )
            )
