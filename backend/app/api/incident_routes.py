import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from openai import OpenAIError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.incident import Incident
from app.schemas.incident import (
    IncidentAnalyzeRequest,
    IncidentAnalysisResponse,
    IncidentCreate,
    IncidentRead,
)
from app.services.ai_service import analyze_incident

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/analyze-incident",
    response_model=IncidentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Incident"],
)
async def analyze_incident_endpoint(incident: IncidentAnalyzeRequest):
    """Analyze an incident using OpenAI and return a concise production-ready analysis."""
    try:
        analysis_text = await analyze_incident(
            service_name=incident.service_name,
            error_message=incident.error_message,
            environment=incident.environment,
        )
    except OpenAIError as exc:
        logger.exception("OpenAI analysis request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Incident analysis is temporarily unavailable. Please try again later.",
        ) from exc
    except ValueError as exc:
        logger.exception("OpenAI returned an unexpected response")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error while analyzing incident")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze incident due to a server error.",
        ) from exc

    return IncidentAnalysisResponse(analysis=analysis_text)


@router.get(
    "/incidents",
    response_model=List[IncidentRead],
    status_code=status.HTTP_200_OK,
    tags=["Incident"],
)
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.detected_at.desc()).all()


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentRead,
    status_code=status.HTTP_200_OK,
    tags=["Incident"],
)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


@router.post(
    "/incidents",
    response_model=IncidentRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Incident"],
)
def create_incident(incident_in: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(
        title=incident_in.title,
        description=incident_in.description,
        service_name=incident_in.service_name,
        environment=incident_in.environment,
        priority=incident_in.priority,
        status="active",
        detected_at=incident_in.detected_at or datetime.utcnow(),
    )

    db.add(incident)
    try:
        db.commit()
        db.refresh(incident)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create incident record.",
        ) from exc

    return incident


@router.put(
    "/incidents/{incident_id}/resolve",
    response_model=IncidentRead,
    status_code=status.HTTP_200_OK,
    tags=["Incident"],
)
def resolve_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    incident.status = "resolved"
    incident.resolved_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(incident)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to resolve incident.",
        ) from exc

    return incident
