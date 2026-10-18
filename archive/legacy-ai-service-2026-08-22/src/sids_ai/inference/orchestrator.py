import base64
import time
from pathlib import Path

from sids_ai.disease_classification.classifier import DiseaseClassifier
from sids_ai.image_quality.service import build_quality_result
from sids_ai.model_registry.loader import ModelLoader
from sids_ai.model_registry.registry import ModelRegistry
from sids_ai.pest_detection.detector import PestDetector
from sids_ai.routing.router import route_problem
from sids_ai.schemas.analysis import AnalysisResponse, ModelInfo
from sids_ai.schemas.image import AnalysisRequest
from sids_ai.uncertainty.unknown import evaluate_uncertainty

# Initialize ModelRegistry and Loader
registry_dir = Path("models/manifests")
registry_dir.mkdir(parents=True, exist_ok=True)
registry = ModelRegistry(registry_dir)
artifacts_dir = Path("models/artifacts")
artifacts_dir.mkdir(parents=True, exist_ok=True)
loader = ModelLoader(registry, artifacts_dir)

# Initialize models (In a real system, the loader would return the instantiated model object)
# Here we instantiate them using the components as directed
pest_detector = PestDetector()
pest_detector.load()

disease_classifier = DiseaseClassifier()
disease_classifier.load()

class InferenceOrchestrator:
    def __init__(self, registry: ModelRegistry, loader: ModelLoader):
        self.registry = registry
        self.loader = loader
        # Attach the initialized model components
        self.pest_detector = pest_detector
        self.disease_classifier = disease_classifier
        
    def analyze_image(self, request: AnalysisRequest) -> AnalysisResponse:
        start_time = time.time()
        
        # 1. Image Decode and Quality
        try:
            image_bytes = base64.b64decode(request.images[0].imageKey)
        except Exception:
            image_bytes = b"dummy"
            
        quality, img_array = build_quality_result(image_bytes)
        
        if not quality.acceptable or img_array is None:
            # Fast fail for unacceptable images
            return AnalysisResponse(
                analysisId=request.analysisId,
                quality=quality,
                routing=route_problem(request.crop, request.mode),
                predictions=[],
                uncertainty=evaluate_uncertainty(0.0),
                model=ModelInfo(id="none", version="0", datasetVersion="none"),
                latencyMs=int((time.time() - start_time) * 1000)
            )
        
        # 2. Routing
        routing = route_problem(request.crop, request.mode)
        
        # 3. Model Registry & Inference
        predictions = []
        used_model = None
        if routing.problemType == "PEST":
            # Real system would do: self.loader.load_model("pest_detection")
            manifest = self.registry.get_current_model("pest_detection")
            predictions = self.pest_detector.predict(img_array)
            used_model = self.pest_detector
            if manifest:
                used_model.model_id = manifest.model_id
                used_model.version = manifest.version
                used_model.dataset_version = manifest.dataset_version or "0"
        elif routing.problemType == "DISEASE":
            manifest = self.registry.get_current_model("disease_classification")
            predictions = self.disease_classifier.predict(img_array)
            used_model = self.disease_classifier
            if manifest:
                used_model.model_id = manifest.model_id
                used_model.version = manifest.version
                used_model.dataset_version = manifest.dataset_version or "0"
            
        # 4. Uncertainty / Calibration
        max_conf = max([p.confidence for p in predictions]) if predictions else 0.0
        uncertainty = evaluate_uncertainty(max_conf)
        
        # 5. Build Result
        latency = int((time.time() - start_time) * 1000)
        
        return AnalysisResponse(
            analysisId=request.analysisId,
            quality=quality,
            routing=routing,
            predictions=predictions,
            severity=None,
            uncertainty=uncertainty,
            model=ModelInfo(
                id=used_model.model_id if used_model else "unknown",
                version=used_model.version if used_model else "0",
                datasetVersion=used_model.dataset_version if used_model else "0"
            ),
            latencyMs=latency
        )

# Global orchestrator instance
orchestrator = InferenceOrchestrator(registry, loader)

def analyze_image(request: AnalysisRequest) -> AnalysisResponse:
    """Wrapper function to maintain backward compatibility with api/router.py"""
    return orchestrator.analyze_image(request)
