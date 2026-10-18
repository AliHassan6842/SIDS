from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ValidationReason(StrEnum):
    TOO_DARK = "TOO_DARK"
    TOO_BRIGHT = "TOO_BRIGHT"
    TOO_BLURRY = "TOO_BLURRY"
    SUBJECT_TOO_SMALL = "SUBJECT_TOO_SMALL"
    NO_INSECT_CANDIDATE = "NO_INSECT_CANDIDATE"
    INVALID_IMAGE = "INVALID_IMAGE"


class QualityBand(StrEnum):
    LOW = "LOW"
    OK = "OK"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class QualitySummary(StrictModel):
    brightness: QualityBand
    blur: QualityBand
    subjectSize: QualityBand


class ValidateFrameResponse(StrictModel):
    valid: bool
    reason: ValidationReason | None
    insectCandidate: bool
    quality: QualitySummary


class IdentificationStatus(StrEnum):
    IDENTIFIED = "IDENTIFIED"
    UNKNOWN = "UNKNOWN"
    REJECTED_IMAGE = "REJECTED_IMAGE"


class IdentificationMode(StrEnum):
    CROP_PEST = "CROP_PEST"
    GENERAL_INSECT = "GENERAL_INSECT"


class UnknownReason(StrEnum):
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    NO_DETECTION = "NO_DETECTION"
    CLASS_UNCERTAIN = "CLASS_UNCERTAIN"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"


class BoundingBox(StrictModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)


class Prediction(StrictModel):
    pestId: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    confidence: float = Field(ge=0, le=1)
    bbox: BoundingBox | None = None


class ModelMetadata(StrictModel):
    id: str
    version: str
    datasetVersion: str


class IdentifyResponse(StrictModel):
    status: IdentificationStatus
    reason: ValidationReason | UnknownReason | None
    prediction: Prediction | None
    model: ModelMetadata
