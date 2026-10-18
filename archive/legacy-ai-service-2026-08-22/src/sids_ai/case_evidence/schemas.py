from typing import Any, Optional, Dict
from pydantic import BaseModel, Field

class EvidenceBundle(BaseModel):
    decision: None = Field(default=None, description="AI must never make a decision, always None")
    visionEvidence: Dict[str, Any] = Field(description="Structured vision analysis results")
    knowledgeEvidence: Dict[str, Any] = Field(description="Structured agronomic knowledge retrieved")
    reason: Optional[str] = None
