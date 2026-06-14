"""API routes for agent-based monitoring and agent API key management."""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.agent_metrics import (
    SystemMetricSubmit,
    SystemMetricResponse,
    HostnamesMetricsResponse,
    MetricsHistoryResponse,
    AgentApiKeyCreate,
    AgentApiKeyResponse,
    AgentApiKeyWithSecret,
)
from app.services.agent_metrics_service import (
    validate_agent_api_key,
    store_metric,
    get_latest_metrics_by_user,
    get_metrics_history,
    get_metric_stats_for_hostname,
)
from app.models.agent_api_key import AgentApiKey

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["Agent Monitoring"])


# ==================== Agent Metrics Endpoints ====================


@router.post(
    "/metrics/collect",
    response_model=SystemMetricResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Agent Metrics - Public"],
)
def collect_metrics(
    metric: SystemMetricSubmit,
    x_agent_key: str = Header(..., alias="X-Agent-Key"),
    db: Session = Depends(get_db),
):
    """
    Receive system metrics from a monitoring agent.
    
    This endpoint is used by agents to submit CPU, memory, and disk usage metrics.
    Requires the X-Agent-Key header with a valid API key.
    
    Args:
        metric: The metric data
        x_agent_key: The agent API key (in X-Agent-Key header)
        db: Database session
    
    Returns:
        The stored metric record
    """
    # Validate the API key
    result = validate_agent_api_key(db, x_agent_key)
    if not result:
        logger.warning(f"Invalid API key attempted for metric collection")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )
    
    user, key_record = result
    
    # Store the metric
    stored_metric = store_metric(db, user.id, metric)
    if not stored_metric:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store metric"
        )
    
    return stored_metric


@router.get(
    "/metrics/latest",
    response_model=HostnamesMetricsResponse,
    status_code=status.HTTP_200_OK,
)
def get_latest_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the latest metrics for all monitored hostnames.
    
    Returns the most recent metric for each unique hostname, including
    "last seen" information.
    """
    hostnames_metrics = get_latest_metrics_by_user(db, current_user.id)
    return HostnamesMetricsResponse(hostnames=hostnames_metrics)


@router.get(
    "/metrics/history/{hostname}",
    response_model=MetricsHistoryResponse,
    status_code=status.HTTP_200_OK,
)
def get_history(
    hostname: str,
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get historical metrics for a specific hostname.
    
    Args:
        hostname: The hostname to get history for
        hours: Number of hours to look back (default 24, max 720 for 30 days)
        db: Database session
        current_user: The authenticated user
    
    Returns:
        Historical metrics for the specified hostname
    """
    metrics = get_metrics_history(db, current_user.id, hostname, hours)
    return MetricsHistoryResponse(hostname=hostname, metrics=metrics)


@router.get(
    "/metrics/stats/{hostname}",
    status_code=status.HTTP_200_OK,
)
def get_stats(
    hostname: str,
    hours: int = Query(1, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get statistics (average, min, max) for a hostname over a time period.
    
    Useful for dashboards to show aggregated information.
    """
    stats = get_metric_stats_for_hostname(db, current_user.id, hostname, hours)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No metrics found for hostname: {hostname}"
        )
    return stats


# ==================== Agent API Key Management ====================


@router.post(
    "/api-keys",
    response_model=AgentApiKeyWithSecret,
    status_code=status.HTTP_201_CREATED,
)
def create_api_key(
    key_request: AgentApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new agent API key for the current user.
    
    The returned key is only shown once - save it securely.
    It will be used in the X-Agent-Key header when submitting metrics.
    
    Args:
        key_request: Request with name and optional hostname
        db: Database session
        current_user: The authenticated user
    
    Returns:
        The newly created API key (with the secret visible)
    """
    try:
        # Generate a new API key
        api_key = AgentApiKey.generate_api_key()
        
        # Create the record
        new_key = AgentApiKey(
            user_id=current_user.id,
            api_key=api_key,
            name=key_request.name,
            hostname=key_request.hostname,
            is_active=True
        )
        
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        
        logger.info(f"Created new API key for user {current_user.id}: {key_request.name}")
        
        return AgentApiKeyWithSecret(
            id=new_key.id,
            name=new_key.name,
            hostname=new_key.hostname,
            api_key=api_key,
            is_active=new_key.is_active,
            created_at=new_key.created_at,
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )


@router.get(
    "/api-keys",
    response_model=List[AgentApiKeyResponse],
    status_code=status.HTTP_200_OK,
)
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all API keys for the current user.
    
    Shows key information but NOT the actual secret (only available at creation time).
    """
    keys = db.query(AgentApiKey).filter(
        AgentApiKey.user_id == current_user.id
    ).all()
    return keys


@router.get(
    "/api-keys/{key_id}",
    response_model=AgentApiKeyResponse,
    status_code=status.HTTP_200_OK,
)
def get_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get details for a specific API key.
    """
    key = db.query(AgentApiKey).filter(
        and_(
            AgentApiKey.id == key_id,
            AgentApiKey.user_id == current_user.id
        )
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return key


@router.put(
    "/api-keys/{key_id}",
    response_model=AgentApiKeyResponse,
    status_code=status.HTTP_200_OK,
)
def update_api_key(
    key_id: int,
    key_request: AgentApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an API key's name or associated hostname.
    """
    key = db.query(AgentApiKey).filter(
        and_(
            AgentApiKey.id == key_id,
            AgentApiKey.user_id == current_user.id
        )
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    try:
        key.name = key_request.name
        if key_request.hostname is not None:
            key.hostname = key_request.hostname
        
        db.commit()
        db.refresh(key)
        
        logger.info(f"Updated API key {key_id} for user {current_user.id}")
        return key
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update API key"
        )


@router.delete(
    "/api-keys/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an API key.
    
    Once deleted, agents using this key will no longer be able to submit metrics.
    """
    key = db.query(AgentApiKey).filter(
        and_(
            AgentApiKey.id == key_id,
            AgentApiKey.user_id == current_user.id
        )
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    try:
        db.delete(key)
        db.commit()
        logger.info(f"Deleted API key {key_id} for user {current_user.id}")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key"
        )


@router.put(
    "/api-keys/{key_id}/deactivate",
    response_model=AgentApiKeyResponse,
    status_code=status.HTTP_200_OK,
)
def deactivate_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deactivate an API key without deleting it.
    
    Agents using this key will no longer be able to submit metrics.
    """
    key = db.query(AgentApiKey).filter(
        and_(
            AgentApiKey.id == key_id,
            AgentApiKey.user_id == current_user.id
        )
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    try:
        key.is_active = False
        db.commit()
        db.refresh(key)
        logger.info(f"Deactivated API key {key_id} for user {current_user.id}")
        return key
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deactivating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate API key"
        )


@router.put(
    "/api-keys/{key_id}/activate",
    response_model=AgentApiKeyResponse,
    status_code=status.HTTP_200_OK,
)
def activate_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reactivate a deactivated API key."""
    key = db.query(AgentApiKey).filter(
        and_(
            AgentApiKey.id == key_id,
            AgentApiKey.user_id == current_user.id
        )
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    try:
        key.is_active = True
        db.commit()
        db.refresh(key)
        logger.info(f"Activated API key {key_id} for user {current_user.id}")
        return key
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error activating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate API key"
        )


# Import sqlalchemy's 'and_' function at the top if not already there
from sqlalchemy import and_
