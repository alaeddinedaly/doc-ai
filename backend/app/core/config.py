"""Application configuration and settings utilities."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, validator
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    # General
    app_name: str = Field(default="DOC-IA")
    environment: Literal["local", "development", "staging", "production"] = Field(
        default="local"
    )
    debug: bool = Field(default=True)

    # Paths
    data_dir: Path = Field(default=PROJECT_ROOT / "data")
    uploads_dir: Path = Field(default=PROJECT_ROOT / "uploads")

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./docia.db")

    # Celery / Redis
    redis_url: str = Field(default="redis://redis:6379/0")
    celery_broker_url: str = Field(default="redis://redis:6379/1")
    celery_backend_url: str = Field(default="redis://redis:6379/2")

    # OCR
    tesseract_cmd: str | None = Field(default=None, description="Override path")
    ocr_languages: str = Field(default="fra+eng")

    # Gemini / Generative AI
    gemini_api_key: str = Field(default="changeme")
    gemini_model: str = Field(default="gemini-pro")
    gemini_temperature: float = Field(default=0.1)

    # Security
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])
    max_upload_size_mb: int = Field(default=50)
    max_upload_files: int = Field(default=10)

    # Rate limiting (prototype, enforced via headers)
    max_uploads_per_hour: int = Field(default=100)

    class Config:
        env_file = PROJECT_ROOT / "backend" / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("uploads_dir", "data_dir", pre=True)
    def _ensure_path(cls, value: str | Path) -> Path:  # noqa: D401
        """Ensure paths are `Path` objects."""
        path = Path(value)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


settings = get_settings()

