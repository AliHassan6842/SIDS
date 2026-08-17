import pytest
from sids_ai.case_evidence.resolver import CaseEvidenceService

def test_high_confidence_retrieves_knowledge_but_no_decision():
    """
    Validates Prompt 3 Rule: The AI must NOT make final agronomic decisions.
    It only provides evidence. The Java backend makes decisions.
    """
    vision_prediction = {
        "status": "DETECTED",
        "confidence": 0.96,
        "pest_id": "fall_armyworm"
    }
    
    evidence_bundle = CaseEvidenceService.resolve_evidence(vision_prediction, crop_id="maize")
    
    # 1. AI Decision must explicitly be None (Java handles it)
    assert evidence_bundle.decision is None, "AI must not make decisions!"
    
    # 2. Vision prediction is preserved
    assert evidence_bundle.visionEvidence["confidence"] == 0.96
    
    # 3. Knowledge evidence is appended
    assert evidence_bundle.knowledgeEvidence is not None
    assert "threshold" in evidence_bundle.knowledgeEvidence
    assert evidence_bundle.knowledgeEvidence["threshold"].pest_id == "fall_armyworm"
    assert evidence_bundle.knowledgeEvidence["threshold"].threshold_value == 20.0

def test_low_confidence_aborts_knowledge_retrieval():
    """
    Validates Prompt 3 Rule: If the model confidence is LOW or UNKNOWN, 
    DO NOT retrieve thresholds and return reason DIAGNOSIS_NOT_CONFIRMED.
    """
    vision_prediction = {
        "status": "UNKNOWN",
        "confidence": 0.30,
        "pest_id": "fall_armyworm"
    }
    
    evidence_bundle = CaseEvidenceService.resolve_evidence(vision_prediction, crop_id="maize")
    
    # 1. AI Decision must explicitly be None
    assert evidence_bundle.decision is None
    
    # 2. Reason is set to DIAGNOSIS_NOT_CONFIRMED
    assert evidence_bundle.reason == "DIAGNOSIS_NOT_CONFIRMED"
    
    # 3. Knowledge evidence retrieval is aborted
    assert evidence_bundle.knowledgeEvidence["threshold"] is None
    assert evidence_bundle.knowledgeEvidence["pesticides"] == []

def test_missing_pest_id_aborts_retrieval():
    """
    Validates that a missing pest ID safely handles the payload.
    """
    vision_prediction = {
        "status": "DETECTED",
        "confidence": 0.99
        # pest_id missing
    }
    
    evidence_bundle = CaseEvidenceService.resolve_evidence(vision_prediction, crop_id="maize")
    assert evidence_bundle.reason == "DIAGNOSIS_NOT_CONFIRMED"
    assert evidence_bundle.knowledgeEvidence["threshold"] is None
