import json
import logging
from pathlib import Path

from pydantic import ValidationError
from sids_ai.model_registry.manifest import ModelManifest, ModelStatus

logger = logging.getLogger(__name__)

class ModelRegistry:
    def __init__(self, manifests_dir: Path):
        self.manifests_dir = manifests_dir
        self.manifests: dict[str, ModelManifest] = {}
        self._load_manifests()
        
    def _load_manifests(self) -> None:
        if not self.manifests_dir.exists():
            logger.warning(f"Manifests directory not found: {self.manifests_dir}")
            return
            
        for manifest_file in self.manifests_dir.glob("*.json"):
            try:
                with open(manifest_file, "r") as f:
                    data = json.load(f)
                manifest = ModelManifest(**data)
                self.manifests[manifest.model_id] = manifest
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode manifest JSON {manifest_file}: {e}")
            except ValidationError as e:
                logger.error(f"Manifest validation failed for {manifest_file}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error loading manifest {manifest_file}: {e}")

    def get_manifest(self, model_id: str) -> ModelManifest | None:
        """Retrieve a specific model manifest by ID."""
        return self.manifests.get(model_id)

    def get_current_model(self, model_type: str) -> ModelManifest | None:
        """Finds the model of a specific type with CURRENT status."""
        for manifest in self.manifests.values():
            if manifest.model_type == model_type and manifest.status == ModelStatus.CURRENT:
                return manifest
        return None
