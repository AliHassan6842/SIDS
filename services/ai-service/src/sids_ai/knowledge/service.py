from typing import Dict, Any, List
from sids_ai.knowledge.thresholds import get_economic_threshold
from sids_ai.knowledge.scouting import get_scouting_guidance
from sids_ai.knowledge.pesticides import get_pesticide_registry
from sids_ai.knowledge.retrieval import search_knowledge_base
from sids_ai.knowledge.schemas import (
    EconomicThresholdRecord,
    ScoutingGuidance,
    PesticideRegistration
)

class KnowledgeService:
    @staticmethod
    def get_comprehensive_pest_info(pest_id: str, crop_id: str) -> Dict[str, Any]:
        """
        Central orchestrator to fetch all knowledge evidence for a pest/crop combo.
        """
        threshold = get_economic_threshold(pest_id, crop_id)
        scouting = get_scouting_guidance(pest_id, crop_id)
        pesticides = get_pesticide_registry(pest_id, crop_id)
        
        return {
            "threshold": threshold,
            "scouting": scouting,
            "pesticides": pesticides
        }
        
    @staticmethod
    def search(query: str) -> List[Any]:
        return search_knowledge_base(query)
