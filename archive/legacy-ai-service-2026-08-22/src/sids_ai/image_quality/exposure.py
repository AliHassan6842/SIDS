
import cv2
import numpy as np
from sids_ai.schemas.analysis import QualityIssue


def evaluate_exposure(image: np.ndarray, min_threshold: float, max_threshold: float) -> list[QualityIssue]:
    issues = []
    
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
        
    mean_intensity = float(np.mean(gray))
    
    if mean_intensity < min_threshold:
        issues.append(QualityIssue(
            code="UNDEREXPOSED",
            severity="WARNING",
            measurement=mean_intensity,
            threshold=min_threshold
        ))
    elif mean_intensity > max_threshold:
        issues.append(QualityIssue(
            code="OVEREXPOSED",
            severity="WARNING",
            measurement=mean_intensity,
            threshold=max_threshold
        ))
        
    return issues
