from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Environment-based application configuration."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    APP_NAME: str = "CampusAssist AI"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    CAMPUSASSIST_API_KEY: str = ""

    LLM_PROVIDER: str = "gemini"  # Supported: gemini, openai
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GEMINI_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/interactions"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-6-astra"
    OPENAI_API_BASE_URL: str = "https://api.openai.com/v1/responses"
    LLM_TIMEOUT_SECONDS: float = 60.0
    LLM_MAX_OUTPUT_TOKENS: int = 1200
    MAX_QUESTION_CHARS: int = 1500
    MAX_HISTORY_MESSAGES: int = 8
    MAX_HISTORY_MESSAGE_CHARS: int = 2000
    CAMPUS_KNOWLEDGE_PATH: str = "data/campus_knowledge.json"

    EXTERNAL_API_TIMEOUT_SECONDS: float = 8.0
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"

    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    MAX_REQUEST_BODY_BYTES: int = 20000


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
