
import cv2
import numpy as np
from sids_ai.core.config import settings
from sids_ai.schemas.analysis import QualityIssue, QualityResult

from .blur import evaluate_blur
from .exposure import evaluate_exposure
from .resolution import evaluate_resolution


def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode image.")
    return img

def build_quality_result(image_bytes: bytes) -> tuple[QualityResult, np.ndarray | None]:
    try:
        img = decode_image_bytes(image_bytes)
    except Exception:
        issues = [QualityIssue(
            code="INVALID_CODEC", 
            severity="ERROR",
            measurement=0.0,
            threshold=0.0
        )]
        return QualityResult(acceptable=False, issues=issues, requestedAction="RETAKE"), None

    h, w = img.shape[:2]
    
    issues: list[QualityIssue] = []
    
    # 1. Resolution
    issues.extend(evaluate_resolution(
        width=w, 
        height=h, 
        min_width=settings.iq_min_width, 
        min_height=settings.iq_min_height
    ))
    
    # 2. Blur (Laplacian variance)
    issues.extend(evaluate_blur(
        image=img, 
        threshold=settings.iq_blur_threshold
    ))
    
    # 3. Exposure (Mean intensity)
    issues.extend(evaluate_exposure(
        image=img, 
        min_threshold=settings.iq_exposure_min, 
        max_threshold=settings.iq_exposure_max
    ))
    
    # Determine acceptance and action
    error_issues = [i for i in issues if i.severity == "ERROR"]
    acceptable = len(error_issues) == 0
    
    requested_action = None
    if not acceptable:
        requested_action = "RETAKE"
        
    return QualityResult(
        acceptable=acceptable, 
        issues=issues,
        requestedAction=requested_action
    ), img
