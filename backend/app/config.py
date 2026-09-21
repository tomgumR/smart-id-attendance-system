from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart ID Attendance"
    database_url: str = "sqlite:///./smart_attendance.db"
    jwt_secret: str = "change-me-in-development"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 480
    face_match_threshold: float = 0.45
    live_face_threshold: float = 0.45
    insightface_model_root: str = "models/insightface"
    yolo_model_path: str = "models/id_card.pt"
    upload_directory: str = "uploads"
    allow_manual_id_fallback: bool = True
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_directory)

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
