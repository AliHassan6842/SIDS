import json
import os
from typing import List
from sids_ai.knowledge.schemas import PesticideRegistration, KnowledgeSource, SourceType

_PESTICIDES_CACHE: List[PesticideRegistration] = None

def _load_pesticides() -> List[PesticideRegistration]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
    file_path = os.path.join(project_root, "knowledge", "processed", "dpp_pesticides.json")
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    records = []
    for item in data:
        # Some active ingredients might be a list, just take the first or join them
        active_ingredients = item.get("active_ingredients", [])
        ai_str = ", ".join(active_ingredients) if active_ingredients else "Unknown"
        
        record = PesticideRegistration(
            registration_number=item.get("registration_id", ""),
            active_ingredient=ai_str,
            product_name=item.get("product_name", ""),
            target_pests=item.get("registered_targets", []),
            approved_crops=item.get("registered_crops", []),
            dosage_rate="N/A",  # Not provided in the example JSON
            phi_days=None,
            source=KnowledgeSource(
                source_type=SourceType.GOVERNMENT_DPP,
                name=item.get("source_id", "Unknown"),
                url=item.get("source_url"),
                last_updated=item.get("retrieved_at")
            )
        )
        records.append(record)
    return records

def get_pesticide_registry(pest_id: str, crop_id: str) -> List[PesticideRegistration]:
    """
    Fetch registered pesticides for a specific pest and crop from the DPP registry.
    """
    global _PESTICIDES_CACHE
    if _PESTICIDES_CACHE is None:
        _PESTICIDES_CACHE = _load_pesticides()
        
    results = []
    for p in _PESTICIDES_CACHE:
        if pest_id in p.target_pests and crop_id in p.approved_crops:
            results.append(p)
    return results
