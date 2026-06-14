"""API routes for agent monitoring insights."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.schemas.insights import AIInsightsResponse
from app.services.agent_insights_service import generate_agent_insights

router = APIRouter(prefix="/agent", tags=["Agent Insights"])


@router.get(
    "/insights",
    response_model=AIInsightsResponse,
    status_code=status.HTTP_200_OK,
)
def get_agent_insights(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Return agent-monitoring insights for the current user."""
    return generate_agent_insights(current_user.id, db)
