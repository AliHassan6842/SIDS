from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class KnowledgeSource(BaseModel):
    source_id: str
    name: str
    authority: str
    authority_level: str
    country: str
    province: Optional[str] = None
    source_type: str
    allowed_domains: List[str]
    crop_scope: List[str]
    problem_scope: List[str]
    language: str
    retrieval_method: str
    license_or_usage_notes: Optional[str] = None
    last_checked: Optional[datetime] = None
    last_successful_ingestion: Optional[datetime] = None
    content_checksum: Optional[str] = None
    review_status: str
    active: bool = True

class EconomicThresholdRecord(BaseModel):
    threshold_id: str
    crop_id: str
    problem_id: str
    common_name: str
    scientific_name: Optional[str] = None
    measurement_type: str
    minimum_value: Optional[float] = None
    maximum_value: Optional[float] = None
    unit: str
    sample_unit: Optional[str] = None
    season: Optional[str] = None
    month_start: Optional[int] = None
    month_end: Optional[int] = None
    growth_stage: Optional[str] = None
    conditions: Dict[str, Any] = Field(default_factory=dict)
    source_id: str
    source_url: str
    retrieved_at: datetime
    effective_date: Optional[datetime] = None
    source_checksum: str
    parser_version: str
    review_status: str

class ScoutingGuidance(BaseModel):
    guidance_id: str
    crop_id: str
    problem_id: str
    sampling_unit: str
    observation_method: str
    frequency: str
    season: Optional[str] = None
    distribution_guidance: Optional[str] = None
    source_id: str
    source_url: str
    retrieved_at: datetime
    review_status: str

class PesticideRegistration(BaseModel):
    registration_id: str
    product_name: str
    registrant: str
    active_ingredients: List[str]
    concentration: Optional[str] = None
    formulation: Optional[str] = None
    registered_crops: List[str]
    registered_targets: List[str]
    registration_status: str
    source_id: str
    source_url: str
    retrieved_at: datetime
    checksum: str
    review_status: str

class IPMManagementOption(BaseModel):
    option_id: str
    crop_id: str
    problem_id: str
    category: str
    description: str
    source_id: str
    source_url: str
    retrieved_at: datetime
    review_status: str

class KnowledgeDocument(BaseModel):
    document_id: str
    source_id: str
    title: str
    source_url: str
    retrieved_at: datetime
    content_checksum: str
    version: str
    jurisdiction_country: str
    jurisdiction_province: Optional[str] = None
    crops: List[str]
    problems: List[str]
    active: bool = True

class KnowledgeChunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    tokens: int
    heading_hierarchy: List[str]
