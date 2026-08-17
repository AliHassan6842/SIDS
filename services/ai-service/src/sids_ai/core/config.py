from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SIDS AI Service"
    environment: str = "development"
    unknown_confidence_threshold: float = 0.5
    model_registry_path: str = "/ml/model-registry"
    valkey_url: str = "redis://localhost:6379/0"
    max_image_size_bytes: int = 10_000_000 # 10MB limit
    
    # Image Quality Thresholds
    iq_min_width: int = 224
    iq_min_height: int = 224
    iq_blur_threshold: float = 85.0
    iq_exposure_min: float = 40.0
    iq_exposure_max: float = 220.0
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
