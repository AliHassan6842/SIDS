from fastapi import APIRouter
from sids_ai.inference.orchestrator import analyze_image
from sids_ai.schemas.analysis import AnalysisResponse
from sids_ai.schemas.image import AnalysisRequest

router = APIRouter(prefix="/internal/v1")

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_endpoint(request: AnalysisRequest):
    return analyze_image(request)

from sids_ai.knowledge.thresholds import get_economic_threshold
from sids_ai.knowledge.scouting import get_scouting_guidance
from sids_ai.knowledge.pesticides import get_pesticide_registry
from sids_ai.knowledge.retrieval import search_knowledge_base
from sids_ai.case_evidence.resolver import CaseEvidenceService
from sids_ai.case_evidence.schemas import EvidenceBundle
from fastapi import Query

@router.get("/knowledge/thresholds")
async def get_thresholds_endpoint(pest_id: str, crop_id: str):
    return get_economic_threshold(pest_id, crop_id)

@router.get("/knowledge/scouting")
async def get_scouting_endpoint(pest_id: str, crop_id: str):
    return get_scouting_guidance(pest_id, crop_id)

@router.get("/knowledge/pesticides")
async def get_pesticides_endpoint(pest_id: str, crop_id: str):
    return get_pesticide_registry(pest_id, crop_id)

@router.get("/knowledge/search")
async def get_search_endpoint(query: str):
    return search_knowledge_base(query)

@router.post("/evidence/resolve", response_model=EvidenceBundle)
async def resolve_evidence_endpoint(vision_prediction: dict, crop_id: str = Query(...)):
    return CaseEvidenceService.resolve_evidence(vision_prediction, crop_id)
