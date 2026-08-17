
from pydantic import BaseModel


class QualityIssue(BaseModel):
    code: str
    severity: str
    measurement: float | None = None
    threshold: float | None = None

class QualityResult(BaseModel):
    acceptable: bool
    issues: list[QualityIssue]
    requestedAction: str | None = None

class RoutingResult(BaseModel):
    problemType: str
    confidence: float

class Prediction(BaseModel):
    classId: str
    commonName: str
    scientificName: str
    confidence: float
    count: int | None = 0
    boundingBoxes: list[dict] = []

class Uncertainty(BaseModel):
    unknown: bool
    requiresMoreEvidence: bool
    requestedViews: list[str] = []

class ModelInfo(BaseModel):
    id: str
    version: str
    datasetVersion: str

class AnalysisResponse(BaseModel):
    analysisId: str
    quality: QualityResult
    routing: RoutingResult
    predictions: list[Prediction]
    severity: float | None = None
    uncertainty: Uncertainty
    model: ModelInfo
    latencyMs: int
