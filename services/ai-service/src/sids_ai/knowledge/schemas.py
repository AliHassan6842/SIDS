from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class SourceType(str, Enum):
    GOVERNMENT_DPP = "GOVERNMENT_DPP"
    RESEARCH_INSTITUTE = "RESEARCH_INSTITUTE"
    UNIVERSITY_EXTENSION = "UNIVERSITY_EXTENSION"

class KnowledgeSource(BaseModel):
    source_type: SourceType
    name: str
    url: Optional[str] = None
    last_updated: Optional[str] = None

class EconomicThresholdRecord(BaseModel):
    pest_id: str
    crop_id: str
    threshold_value: float
    unit: str
    condition: Optional[str] = None
    source: KnowledgeSource

class ScoutingGuidance(BaseModel):
    pest_id: str
    crop_id: str
    scouting_method: str
    frequency_days: int
    key_indicators: List[str]
    source: KnowledgeSource

class PesticideRegistration(BaseModel):
    registration_number: str
    active_ingredient: str
    product_name: str
    target_pests: List[str]
    approved_crops: List[str]
    dosage_rate: str
    phi_days: Optional[int] = Field(None, description="Pre-harvest interval in days")
    source: KnowledgeSource

class IPMManagementOption(BaseModel):
    strategy_type: str = Field(description="e.g., CULTURAL, BIOLOGICAL, CHEMICAL")
    description: str
    target_pest_id: str
    crop_id: Optional[str] = None
    source: KnowledgeSource
