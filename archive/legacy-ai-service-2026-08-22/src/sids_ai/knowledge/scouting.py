from typing import Optional, List
from sids_ai.knowledge.schemas import ScoutingGuidance, KnowledgeSource, SourceType

def get_scouting_guidance(pest_id: str, crop_id: str) -> Optional[ScoutingGuidance]:
    """
    Fetch structured scouting guidance for a specific pest and crop.
    """
    if pest_id == "fall_armyworm" and crop_id == "maize":
        return ScoutingGuidance(
            pest_id=pest_id,
            crop_id=crop_id,
            scouting_method="W pattern field walk, check 20 consecutive plants at 5 locations",
            frequency_days=7,
            key_indicators=["window pane feeding", "frass in whorl", "egg masses on leaf underside"],
            source=KnowledgeSource(
                source_type=SourceType.UNIVERSITY_EXTENSION,
                name="Ag Extension Office"
            )
        )
    return None
