import json
import os
from typing import Optional, List
from sids_ai.knowledge.schemas import EconomicThresholdRecord, KnowledgeSource, SourceType

_THRESHOLDS_CACHE: Optional[List[EconomicThresholdRecord]] = None

def _load_thresholds() -> List[EconomicThresholdRecord]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
    file_path = os.path.join(project_root, "knowledge", "processed", "punjab_thresholds.json")
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    records = []
    for item in data:
        conditions = item.get("conditions", {})
        cond_str = ", ".join(f"{k}: {v}" for k, v in conditions.items()) if conditions else None
        
        record = EconomicThresholdRecord(
            pest_id=item.get("problem_id", ""),
            crop_id=item.get("crop_id", ""),
            threshold_value=float(item.get("minimum_value", 0.0)),
            unit=item.get("unit", ""),
            condition=cond_str,
            source=KnowledgeSource(
                source_type=SourceType.GOVERNMENT_DPP,
                name=item.get("source_id", "Unknown"),
                url=item.get("source_url"),
                last_updated=item.get("retrieved_at")
            )
        )
        records.append(record)
    return records

def get_economic_threshold(pest_id: str, crop_id: str) -> Optional[EconomicThresholdRecord]:
    """
    Fetch structured economic threshold for a specific pest and crop.
    """
    global _THRESHOLDS_CACHE
    if _THRESHOLDS_CACHE is None:
        _THRESHOLDS_CACHE = _load_thresholds()
        
    for t in _THRESHOLDS_CACHE:
        if t.pest_id == pest_id and t.crop_id == crop_id:
            return t
    return None

def list_economic_thresholds(crop_id: str) -> List[EconomicThresholdRecord]:
    """
    List all thresholds for a crop.
    """
    global _THRESHOLDS_CACHE
    if _THRESHOLDS_CACHE is None:
        _THRESHOLDS_CACHE = _load_thresholds()
        
    return [t for t in _THRESHOLDS_CACHE if t.crop_id == crop_id]
