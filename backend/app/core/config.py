from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables and `.env`."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    PROJECT_NAME: str = "Skill Swap"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: SecretStr
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:5173"

    OPENAI_API_KEY: SecretStr = SecretStr("")
    OPENAI_MODEL: str = "gpt-4.1-mini"
    GEMINI_API_KEY: SecretStr = SecretStr("")
    GEMINI_MODEL: str = "gemini-3.8-flash"

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 5

    @property
    def upload_root(self) -> Path:
        return (BACKEND_DIR / self.UPLOAD_DIR).resolve()

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024


    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
