from typing import Optional, List
from sids_ai.knowledge.schemas import EconomicThresholdRecord, KnowledgeSource, SourceType

def get_economic_threshold(pest_id: str, crop_id: str) -> Optional[EconomicThresholdRecord]:
    """
    Fetch structured economic threshold for a specific pest and crop.
    This currently mocks a database lookup.
    """
    # Mock data retrieval
    if pest_id == "fall_armyworm" and crop_id == "maize":
        return EconomicThresholdRecord(
            pest_id=pest_id,
            crop_id=crop_id,
            threshold_value=20.0,
            unit="percent_infested_plants",
            condition="Early whorl stage",
            source=KnowledgeSource(
                source_type=SourceType.GOVERNMENT_DPP,
                name="Department of Plant Protection",
                url="https://example.gov/dpp/thresholds"
            )
        )
    return None

def list_economic_thresholds(crop_id: str) -> List[EconomicThresholdRecord]:
    """
    List all thresholds for a crop.
    """
    threshold = get_economic_threshold("fall_armyworm", crop_id)
    if threshold:
        return [threshold]
    return []
