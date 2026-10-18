import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from sids_ai.core.errors import ModelUnavailable


class ModelManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str
    version: str
    task: str = Field(pattern="^(pest-detection|classification)$")
    classes: dict[int, str]
    crop_classes: dict[str, list[str]]
    artifact_path: Path
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    input_size: int = Field(ge=160, le=2048)
    acceptance_threshold: float = Field(gt=0, lt=1)
    dataset_version: str
    evaluation_summary: dict[str, float | int | str]

    @model_validator(mode="after")
    def class_slugs_are_unique(self) -> "ModelManifest":
        if len(set(self.classes.values())) != len(self.classes):
            raise ValueError("Model class slugs must be unique")
        return self


def load_manifest(path: Path) -> ModelManifest:
    try:
        manifest = ModelManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ModelUnavailable(f"Approved model manifest is unavailable: {path}") from exc
    artifact = manifest.artifact_path
    if not artifact.is_absolute():
        artifact = (path.parent / artifact).resolve()
    if not artifact.is_file():
        raise ModelUnavailable("Approved model artifact is missing")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if digest != manifest.sha256:
        raise ModelUnavailable("Approved model checksum does not match")
    manifest.artifact_path = artifact
    return manifest
