"""
Out-of-Distribution (OOD) and uncertainty detection logic.
"""
import math
from typing import Any

from sids_ai.core.config import settings
from sids_ai.schemas.analysis import Uncertainty


class UncertaintyEvaluator:
    """
    Evaluates prediction uncertainty to detect Out-Of-Distribution (OOD)
    or cases that require more evidence/manual review.
    """
    def __init__(self, 
                 confidence_threshold: float = getattr(settings, 'unknown_confidence_threshold', 0.5), 
                 entropy_threshold: float = getattr(settings, 'unknown_entropy_threshold', 1.0),
                 margin_threshold: float = getattr(settings, 'unknown_margin_threshold', 0.1)):
        self.confidence_threshold = confidence_threshold
        self.entropy_threshold = entropy_threshold
        self.margin_threshold = margin_threshold

    def evaluate_from_probs(self, class_probs: list[float]) -> tuple[bool, bool, dict[str, Any]]:
        """
        Evaluate full probability distribution for uncertainty.
        
        Returns:
            is_ood: bool (True if suspected Out-Of-Distribution)
            requires_more_evidence: bool (True if uncertain and needs review)
            metrics: dict containing calculated uncertainty metrics
        """
        if not class_probs:
            return True, True, {}
            
        sorted_probs = sorted(class_probs, reverse=True)
        top_prob = sorted_probs[0]
        margin = top_prob - sorted_probs[1] if len(sorted_probs) > 1 else top_prob
        
        entropy = 0.0
        for p in class_probs:
            if p > 0:
                entropy -= p * math.log(p)
                
        metrics = {
            "top_confidence": top_prob,
            "margin": margin,
            "entropy": entropy
        }
        
        is_ood = entropy > self.entropy_threshold
        requires_more_evidence = top_prob < self.confidence_threshold or margin < self.margin_threshold
        
        return is_ood, requires_more_evidence, metrics

# Singleton instance using config settings
evaluator = UncertaintyEvaluator()

def evaluate_uncertainty(max_confidence: float) -> Uncertainty:
    """
    Evaluates uncertainty based on the maximum confidence provided.
    This is used by the orchestrator when only top predictions are available.
    """
    is_unknown = max_confidence < evaluator.confidence_threshold
    
    return Uncertainty(
        unknown=is_unknown,
        requiresMoreEvidence=is_unknown,
        requestedViews=["LEAF_UNDERSIDE", "WHOLE_PLANT"] if is_unknown else []
    )
