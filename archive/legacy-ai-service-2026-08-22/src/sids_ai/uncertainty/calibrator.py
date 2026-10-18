"""
Runtime inference calibration tools for SIDS AI.
"""
import numpy as np


class ConfidenceCalibrator:
    """
    Applies calibration to model confidences at runtime.
    Can be loaded with temperature values derived from offline calibration tuning.
    """
    def __init__(self, temperature: float = 1.0):
        self.temperature = temperature
        
    def calibrate_logits(self, logits: np.ndarray) -> np.ndarray:
        """
        Apply temperature scaling to a 1D or 2D array of logits and return probabilities.
        
        Args:
            logits: Model logits (N, C) or (C,)
            
        Returns:
            np.ndarray: Calibrated probabilities
        """
        scaled_logits = logits / self.temperature
        
        # Softmax computation (numerically stable)
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=-1, keepdims=True))
        return exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
