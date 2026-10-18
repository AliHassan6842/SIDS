from enum import Enum

from pydantic import BaseModel, Field


class ModelStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    CURRENT = "CURRENT"
    RETIRED = "RETIRED"
    FAILED = "FAILED"

class ModelArtifact(BaseModel):
    file_name: str
    sha256: str
    size_bytes: int

class ModelManifest(BaseModel):
    model_id: str
    version: str
    model_type: str  # e.g., "pest_detection", "disease_classification"
    status: ModelStatus
    artifacts: list[ModelArtifact]
    metrics: dict[str, float] = Field(default_factory=dict)
    created_at: str
    dataset_version: str | None = None
    training_commit: str | None = None
