from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import os
from typing import Optional

from app.api.routes import router
from app.core.config import settings, mask_api_key, reload_dotenv, get_openai_key
from app.core.exceptions import OpenAIConfigurationError, OpenAIServiceError
from app.db.base import Base
from app.db.session import engine
from app.models.user import User  # Import models so SQLAlchemy metadata is registered
from app.models.deployment import Deployment  # Import deployment model for table creation
from app.models.incident import Incident  # Import incident model for table creation
from app.models.system_metric import SystemMetric  # Import system metric model for agent monitoring
from app.models.agent_api_key import AgentApiKey  # Import agent API key model

logger = logging.getLogger(__name__)

# Use centralized settings for app metadata
app = FastAPI(title=settings.APP_NAME, version=settings.API_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:5173', 'http://localhost:5173', 'http://127.0.0.1:8000', 'https://ai-devops-platform-3.onrender.com'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.exception_handler(OpenAIConfigurationError)
async def openai_configuration_exception_handler(request: Request, exc: OpenAIConfigurationError):
    # Return structured JSON so frontend can handle missing-key gracefully.
    raw_env = os.environ.get("OPENAI_API_KEY")
    masked = mask_api_key(raw_env or get_openai_key())
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": str(exc),
            "type": "openai_configuration_error",
            "openai_configured": False,
            "openai_masked_key": masked,
        },
    )


@app.exception_handler(OpenAIServiceError)
async def openai_service_exception_handler(request: Request, exc: OpenAIServiceError):
    raw_env = os.environ.get("OPENAI_API_KEY")
    masked = mask_api_key(raw_env or get_openai_key())
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "detail": str(exc),
            "type": "openai_service_error",
            "openai_configured": bool(get_openai_key()),
            "openai_masked_key": masked,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later."},
    )


def _try_create_tables(retries: int = 5, delay: float = 2.0) -> Optional[Exception]:
    """Attempt to create DB tables with retries.

    Returns the last exception if all retries fail, otherwise None.
    """
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully.")
            return None
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "Attempt %d/%d: Failed to create database tables: %s",
                attempt,
                retries,
                exc,
            )
            if attempt < retries:
                time.sleep(delay)
    return last_exc


@app.on_event("startup")
def create_tables() -> None:
    """Startup handler that creates DB tables but does not prevent app startup on failure.

    It will retry a few times to allow the database server to come up, then log a clear error
    if it still cannot connect. This avoids a hard crash while making the failure visible.
    """
    exc = _try_create_tables()
    if exc is not None:
        logger.error(
            "Failed to create database tables after retries: %s. "
            "Check DATABASE_URL and database server status.",
            exc,
        )


@app.on_event("startup")
def _log_openai_configuration_on_startup() -> None:
    """Reload dotenv and log masked OpenAI key; set app state.

    This ensures `.env` is read on reloads and the running app knows whether
    OpenAI is available so endpoints can respond quickly and the frontend can
    stop polling when the service is unavailable.
    """
    # Reload dotenv to ensure environment variables are present after reloads
    try:
        reload_dotenv()
    except Exception:
        logger.exception("reload_dotenv() failed at startup")

    raw_env = os.environ.get("OPENAI_API_KEY")
    config_key = get_openai_key()
    masked = mask_api_key(raw_env or config_key)

    # Determine availability and store on app.state so other parts can check cheaply
    available = bool(config_key)
    app.state.openai_configured = available
    app.state.openai_masked_key = masked

    if available:
        logger.info("OpenAI configuration loaded successfully")
        logger.info("OpenAI key loaded successfully (masked)=%s", masked)
    else:
        # Do not abort startup when OpenAI is not configured. Use local fallbacks instead.
        logger.warning("OpenAI API key not present; running with local AI fallbacks.")

    # Extra check for common formatting mistakes in the raw .env value
    if raw_env is not None and raw_env != (str(raw_env).strip().strip('"').strip("'")):
        logger.warning("OPENAI_API_KEY appears to contain extra quotes or spaces in .env.")

# Include modular API router(s)
app.include_router(router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "AI DevOps Platform Backend Running Successfully"}
