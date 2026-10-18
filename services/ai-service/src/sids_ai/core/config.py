from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_SERVICE_", extra="ignore")

    environment: str = "production"
    max_upload_bytes: int = Field(default=8 * 1024 * 1024, ge=1024)
    max_image_pixels: int = Field(default=20_000_000, ge=1_000_000)
    min_width: int = Field(default=224, ge=64)
    min_height: int = Field(default=224, ge=64)
    dark_mean: float = Field(default=38.0, ge=0, le=255)
    bright_mean: float = Field(default=225.0, ge=0, le=255)
    blur_variance_min: float = Field(default=45.0, ge=0)
    candidate_edge_density_min: float = Field(default=0.012, ge=0, le=1)
    candidate_edge_density_max: float = Field(default=0.48, ge=0, le=1)
    model_manifest: Path = Path("models/manifests/sids-pest-detector.json")
    small_subject_model_manifest: Path = Path(
        "models/manifests/sids-pest-detector-small-subject.json"
    )
    general_insect_model_manifest: Path | None = Path(
        "models/manifests/sids-general-insect-classifier.json"
    )
    max_inference_concurrency: int = Field(default=2, ge=1, le=8)
    service_token: str = Field(min_length=24)

    @field_validator("service_token")
    @classmethod
    def service_token_must_not_be_a_placeholder(cls, value: str) -> str:
        normalized = value.lower()
        if any(marker in normalized for marker in ("change-me", "replace-with", "development-only")):
            raise ValueError("AI service token must not be a published placeholder")
        return value


@lru_cache
def get_settings() -> Settings:
    # BaseSettings supplies required values from AI_SERVICE_* environment variables.
    return Settings()  # type: ignore[call-arg]
