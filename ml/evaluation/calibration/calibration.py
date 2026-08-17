"""
Expected Calibration Error and Brier Score calculations.
"""
import numpy as np


def calculate_ece(confidences: np.ndarray, accuracies: np.ndarray, num_bins: int = 15) -> float:
    """
    Calculate the Expected Calibration Error (ECE).
    
    Args:
        confidences: 1D array of predicted confidences (probabilities of the predicted class).
        accuracies: 1D array of binary indicators (1 if prediction is correct, 0 otherwise).
        num_bins: Number of bins to use for calibration.
        
    Returns:
        float: The ECE value.
    """
    bin_boundaries = np.linspace(0.0, 1.0, num_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]
    
    ece = 0.0
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        # The upper bound is inclusive for the last bin, exclusive otherwise (or just <= is fine)
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = in_bin.mean()
        
        if prop_in_bin > 0:
            accuracy_in_bin = accuracies[in_bin].mean()
            avg_confidence_in_bin = confidences[in_bin].mean()
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
            
    return float(ece)

def calculate_brier_score(probs: np.ndarray, labels: np.ndarray, num_classes: int = None) -> float:
    """
    Calculate the Brier Score for multi-class classification.
    
    Args:
        probs: 2D array of predicted probabilities of shape (N, C).
        labels: 1D array of true class indices of shape (N,).
        num_classes: Number of classes (inferred from probs if not provided).
        
    Returns:
        float: The Brier Score.
    """
    if num_classes is None:
        num_classes = probs.shape[1]
        
    # Create one-hot encoding of labels
    labels_one_hot = np.eye(num_classes)[labels]
    
    # Calculate Brier score: mean squared difference across all classes
    brier_score = np.mean(np.sum((probs - labels_one_hot) ** 2, axis=1))
    return float(brier_score)
