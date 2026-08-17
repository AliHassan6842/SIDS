
from pydantic import BaseModel


class ImageContext(BaseModel):
    fieldId: str

class ImageRequest(BaseModel):
    imageKey: str
    
class AnalysisRequest(BaseModel):
    analysisId: str
    crop: str
    mode: str = "QUICK_DIAGNOSIS"
    images: list[ImageRequest]
    context: ImageContext | None = None
