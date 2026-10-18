
import cv2
import numpy as np
from sids_ai.schemas.analysis import QualityIssue


def evaluate_blur(image: np.ndarray, threshold: float) -> list[QualityIssue]:
    issues = []
    
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
        
    variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    
    if variance < threshold:
        issues.append(QualityIssue(
            code="IMAGE_TOO_BLURRY",
            severity="ERROR",
            measurement=variance,
            threshold=threshold
        ))
        
    return issues
