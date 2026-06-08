import os
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
APP_DIR = BASE_DIR / "app"
ROOT_ENV_PATH = BASE_DIR / ".env"
APP_ENV_PATH = APP_DIR / ".env"
ENV_PATHS = [ROOT_ENV_PATH, APP_ENV_PATH]

logger = logging.getLogger(__name__)


def _is_placeholder_api_key(value: str) -> bool:
    raw_value = str(value).strip().strip('"').strip("'")
    if not raw_value:
        return True
    lower = raw_value.lower()
    return (
        lower.startswith("your_")
        or "replace" in lower
        or lower.startswith("sk-replace")
        or lower == "sk-xxxxxxxx"
        or lower == "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        or lower.endswith("xxxxxxxx")
    )


def _normalize_api_key(value: str) -> str:
    return str(value).strip().strip('"').strip("'")


def mask_api_key(value: str | None) -> str | None:
    """Return a masked OpenAI API key for safe logging, e.g. sk-proj-****abcd."""
    if not value:
        return None
    raw = _normalize_api_key(value)
    if len(raw) <= 8:
        return "****"
    # Keep prefix up to last 4 chars, mask the middle
    prefix = raw[:-4]
    suffix = raw[-4:]
    # Shorten prefix to a sensible length for display
    if len(prefix) > 12:
        prefix = prefix[:12]
    return f"{prefix}****{suffix}"


def load_env_files() -> None:
    """Load environment variables from absolute backend .env file paths."""
    loaded_files = []
    for env_path in ENV_PATHS:
        if env_path.exists():
            load_dotenv(env_path, override=False)
            loaded_files.append(str(env_path))
    logger.debug("Loaded env files: %s; OPENAI_API_KEY present=%s", loaded_files, bool(os.getenv("OPENAI_API_KEY")))


load_env_files()


class Settings(BaseSettings):
    APP_NAME: str = "AI DevOps Platform"
    API_VERSION: str = "v1"
    DEBUG: bool = False
    SECRET_KEY: str
    DATABASE_URL: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CPU_WARNING_THRESHOLD: int = 70
    CPU_CRITICAL_THRESHOLD: int = 90
    MEMORY_WARNING_THRESHOLD: int = 70
    MEMORY_CRITICAL_THRESHOLD: int = 90
    DISK_WARNING_THRESHOLD: int = 75
    DISK_CRITICAL_THRESHOLD: int = 95

    # Load configuration from the process environment after dotenv values have already been imported.
    model_config = SettingsConfigDict(env_file=None)

    @field_validator("OPENAI_API_KEY", mode="before")
    def validate_openai_api_key(cls, value):
        if value is None:
            raise ValueError("OPENAI_API_KEY must be defined in .env or the environment.")

        raw_key = _normalize_api_key(value)
        if _is_placeholder_api_key(raw_key):
            raise ValueError("OPENAI_API_KEY must be a valid OpenAI secret key, not a placeholder.")

        return raw_key

    @field_validator("SECRET_KEY", mode="before")
    def validate_secret_key(cls, value):
        if not value or len(str(value).strip()) < 16:
            raise ValueError("SECRET_KEY must be set and at least 16 characters long.")
        return str(value).strip()

    @field_validator("DATABASE_URL", mode="before")
    def validate_database_url(cls, value):
        if not value or not str(value).strip():
            raise ValueError("DATABASE_URL must be defined in .env or the environment.")
        return str(value).strip()


# Create a single settings instance for application-wide use
settings = Settings()


def reload_dotenv() -> None:
    """Reload dotenv files from absolute backend paths. Safe to call on restarts.

    This re-reads both the repository root `.env` and the `app/.env` file so
    environment variables are available to the running process (useful when
    running with auto-reload during development).
    """
    try:
        load_env_files()
    except Exception:
        logger.exception("Failed to reload .env files")


def get_openai_key() -> Optional[str]:
    """Return a normalized OpenAI API key from the environment or settings.

    Preference order:
    1. `OPENAI_API_KEY` from process environment (normalized)
    2. `settings.OPENAI_API_KEY` created at import time (already validated)
    Returns `None` if a placeholder or missing.
    """
    raw = os.environ.get("OPENAI_API_KEY")
    if raw:
        norm = _normalize_api_key(raw)
        if not _is_placeholder_api_key(norm):
            return norm

    # fallback to the pydantic settings instance which was loaded at import
    val = getattr(settings, "OPENAI_API_KEY", None)
    if val:
        norm = _normalize_api_key(val)
        if not _is_placeholder_api_key(norm):
            return norm

    return None


def is_openai_configured() -> bool:
    return get_openai_key() is not None
