import logging
from pathlib import Path
from typing import Any

from sids_ai.model_registry.integrity import verify_artifact_integrity
from sids_ai.model_registry.manifest import ModelManifest
from sids_ai.model_registry.registry import ModelRegistry

logger = logging.getLogger(__name__)

class ModelIntegrityError(Exception):
    """Raised when an artifact fails checksum verification."""

class ModelStatusError(Exception):
    """Raised when an artifact does not meet status requirements (e.g. not CURRENT)."""

class ModelLoader:
    def __init__(self, registry: ModelRegistry, artifacts_dir: Path):
        self.registry = registry
        self.artifacts_dir = artifacts_dir

    def resolve_and_verify(self, model_type: str) -> tuple[ModelManifest, Path]:
        """
        Locates the CURRENT model for a given type, verifies its integrity,
        and returns the manifest along with the local artifact path.
        """
        manifest = self.registry.get_current_model(model_type)
        if not manifest:
            raise ModelStatusError(f"No CURRENT model found for type: {model_type}")
            
        if not manifest.artifacts:
            raise ModelIntegrityError(f"Model {manifest.model_id} has no artifacts defined.")
            
        # Assuming the first artifact is the primary model file
        primary_artifact = manifest.artifacts[0]
        artifact_path = self.artifacts_dir / primary_artifact.file_name
        
        if not artifact_path.exists():
            raise ModelIntegrityError(f"Artifact file not found: {artifact_path}")
            
        logger.info(f"Verifying integrity of artifact {artifact_path} for model {manifest.model_id}")
        if not verify_artifact_integrity(artifact_path, primary_artifact.sha256):
            raise ModelIntegrityError(
                f"SHA-256 checksum failed for artifact: {artifact_path}. "
                f"Expected {primary_artifact.sha256}"
            )
            
        logger.info(f"Integrity verified for model {manifest.model_id}")
        return manifest, artifact_path

    def load_model(self, model_type: str) -> Any:
        """
        Resolves, verifies, and loads the model into memory.
        In a real implementation, this would instantiate the model architecture 
        (e.g., PyTorch, ONNX) with the verified weights file.
        """
        manifest, artifact_path = self.resolve_and_verify(model_type)
        
        logger.info(f"Loading verified model {manifest.model_id} of type {model_type}")
        # The specific loading logic would go here, branching by model format.
        # Returning artifact path for now as a verified reference.
        return artifact_path
