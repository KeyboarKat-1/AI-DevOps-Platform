import logging

from fastapi import APIRouter, status

from app.schemas.insights import (
    AIInsightsResponse,
    AISuggestionRequest,
    AISuggestionResponse,
)
from app.services.insights_service import (
    generate_ai_insights,
    generate_contextual_suggestion,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/ai-insights",
    response_model=AIInsightsResponse,
    status_code=status.HTTP_200_OK,
    tags=["AI"],
)
async def get_ai_insights():
    """Return deterministic local insights for current system metrics."""
    return await generate_ai_insights()


@router.post(
    "/insights/ai-suggestions",
    response_model=AISuggestionResponse,
    status_code=status.HTTP_200_OK,
    tags=["AI"],
)
async def get_ai_suggestions(request: AISuggestionRequest):
    """Generate a local AI suggestion based on the provided request context."""
    return await generate_contextual_suggestion(request.context)


@router.get(
    "/insights",
    response_model=AIInsightsResponse,
    status_code=status.HTTP_200_OK,
    tags=["AI"],
)
async def get_insights():
    """Return current insights through the `/api/insights` endpoint."""
    return await generate_ai_insights()
