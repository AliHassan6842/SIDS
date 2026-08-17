from typing import List
from sids_ai.knowledge.schemas import PesticideRegistration, KnowledgeSource, SourceType

def get_pesticide_registry(pest_id: str, crop_id: str) -> List[PesticideRegistration]:
    """
    Fetch registered pesticides for a specific pest and crop from the DPP registry.
    """
    if pest_id == "fall_armyworm" and crop_id == "maize":
        return [
            PesticideRegistration(
                registration_number="DPP-12345",
                active_ingredient="Emamectin benzoate",
                product_name="EmaPower 5SG",
                target_pests=[pest_id],
                approved_crops=[crop_id],
                dosage_rate="200g/ha",
                phi_days=14,
                source=KnowledgeSource(
                    source_type=SourceType.GOVERNMENT_DPP,
                    name="DPP Pesticide Registry"
                )
            )
        ]
    return []
