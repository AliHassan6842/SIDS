from typing import Any

import numpy as np


def calculate_severity(
    affected_mask: np.ndarray, 
    valid_plant_mask: np.ndarray
) -> dict[str, float | int | str]:
    """
    Calculate visible sample severity from segmentation masks.
    
    Severity is defined as: affected_pixels / valid_plant_pixels
    
    Args:
        affected_mask (np.ndarray): Boolean or binary mask of the affected area (e.g., disease or damage).
        valid_plant_mask (np.ndarray): Boolean or binary mask of the valid plant area (excluding background).
        
    Returns:
        Dict containing severity score, affected pixels, and valid plant pixels.
    """
    if affected_mask.shape != valid_plant_mask.shape:
        raise ValueError(f"Mask shapes must match. Got affected_mask: {affected_mask.shape}, valid_plant_mask: {valid_plant_mask.shape}")
        
    # Ensure masks are boolean
    affected = affected_mask.astype(bool)
    valid_plant = valid_plant_mask.astype(bool)
    
    # Calculate intersection (affected area must be within valid plant area)
    actual_affected = affected & valid_plant
    
    affected_pixels = int(np.sum(actual_affected))
    valid_plant_pixels = int(np.sum(valid_plant))
    
    if valid_plant_pixels == 0:
        return {
            "severity": 0.0,
            "affected_pixels": 0,
            "valid_plant_pixels": 0,
            "error": "No valid plant pixels found."
        }
        
    severity = affected_pixels / valid_plant_pixels
    
    return {
        "severity": float(severity),
        "affected_pixels": affected_pixels,
        "valid_plant_pixels": valid_plant_pixels
    }

class SeverityCalculator:
    """Runtime interface for severity calculation."""
    def __init__(self):
        pass
        
    def process(self, affected_mask: np.ndarray, valid_plant_mask: np.ndarray) -> dict[str, Any]:
        return calculate_severity(affected_mask, valid_plant_mask)
