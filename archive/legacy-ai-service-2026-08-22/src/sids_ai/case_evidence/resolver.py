from typing import Dict, Any
from sids_ai.case_evidence.schemas import EvidenceBundle
from sids_ai.knowledge.service import KnowledgeService

class CaseEvidenceService:
    @staticmethod
    def resolve_evidence(vision_prediction: Dict[str, Any], crop_id: str) -> EvidenceBundle:
        """
        Connects AI predictions with knowledge evidence.
        """
        prediction_status = vision_prediction.get("status", "UNKNOWN")
        confidence = vision_prediction.get("confidence", 0.0)
        pest_id = vision_prediction.get("pest_id")
        
        knowledge_evidence = {}
        reason = None
        
        if prediction_status == "UNKNOWN" or confidence < 0.5 or not pest_id:
            # Must NOT retrieve threshold if prediction is unknown or low confidence
            knowledge_evidence = {
                "threshold": None,
                "scouting": None,
                "pesticides": []
            }
            reason = "DIAGNOSIS_NOT_CONFIRMED"
        else:
            knowledge_evidence = KnowledgeService.get_comprehensive_pest_info(pest_id, crop_id)
            
        return EvidenceBundle(
            decision=None,
            visionEvidence=vision_prediction,
            knowledgeEvidence=knowledge_evidence,
            reason=reason
        )
