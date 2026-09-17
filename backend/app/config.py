from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    gemini_api_key: str | None = None
    gemini_model_primary: str = "gemini-2.0-flash"
    gemini_model_fallback: str = "gemini-1.5-flash"

    vertex_project_id: str | None = None
    vertex_location: str = "us-central1"
    lyria_model: str = "lyria-002"

    database_url: str = "sqlite:///./bean_sounds.db"

    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    api_key: str | None = None
    rate_limit_generate: str = "10/minute"
    rate_limit_audio: str = "5/minute"

    audio_storage_dir: str = "./audio_storage"
    audio_public_prefix: str = "/audio"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
