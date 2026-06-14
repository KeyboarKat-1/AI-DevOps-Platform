"""Service for managing agent-based system metrics."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.system_metric import SystemMetric
from app.models.agent_api_key import AgentApiKey
from app.models.user import User
from app.schemas.agent_metrics import SystemMetricSubmit, HostnameMetrics

logger = logging.getLogger(__name__)


def validate_agent_api_key(db: Session, api_key: str) -> Optional[Tuple[User, AgentApiKey]]:
    """
    Validate an agent API key and return the associated user and key record.
    
    Args:
        db: Database session
        api_key: The API key to validate
    
    Returns:
        Tuple of (User, AgentApiKey) if valid, None otherwise
    """
    try:
        key_record = db.query(AgentApiKey).filter(
            and_(
                AgentApiKey.api_key == api_key,
                AgentApiKey.is_active == True
            )
        ).first()
        
        if not key_record:
            logger.warning(f"Invalid or inactive API key attempted: {api_key[:8]}...")
            return None
        
        # Update last_used timestamp
        key_record.last_used = datetime.utcnow()
        db.commit()
        
        user = key_record.user
        return (user, key_record)
    
    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return None


def store_metric(
    db: Session,
    user_id: int,
    metric_data: SystemMetricSubmit
) -> Optional[SystemMetric]:
    """
    Store a system metric submitted by an agent.
    
    Args:
        db: Database session
        user_id: ID of the user who owns the agent
        metric_data: The metric data from the agent
    
    Returns:
        The created SystemMetric object, or None on error
    """
    try:
        metric = SystemMetric(
            user_id=user_id,
            hostname=metric_data.hostname,
            cpu_usage=metric_data.cpu_usage,
            memory_usage=metric_data.memory_usage,
            disk_usage=metric_data.disk_usage,
            operating_system=metric_data.operating_system,
            timestamp=metric_data.timestamp or datetime.utcnow()
        )
        
        db.add(metric)
        db.commit()
        db.refresh(metric)
        
        logger.info(f"Stored metric for hostname={metric.hostname}, user={user_id}")
        return metric
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing metric: {str(e)}")
        return None


def get_latest_metrics_by_user(
    db: Session,
    user_id: int
) -> List[HostnameMetrics]:
    """
    Get the latest metrics for each unique hostname for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
    
    Returns:
        List of HostnameMetrics with latest data for each hostname
    """
    try:
        # Get list of unique hostnames
        hostnames = db.query(SystemMetric.hostname).filter(
            SystemMetric.user_id == user_id
        ).distinct().all()
        
        results = []
        now = datetime.utcnow()
        
        for (hostname,) in hostnames:
            # Get latest metric for this hostname
            latest = db.query(SystemMetric).filter(
                and_(
                    SystemMetric.user_id == user_id,
                    SystemMetric.hostname == hostname
                )
            ).order_by(desc(SystemMetric.timestamp)).first()
            
            if latest:
                # Calculate seconds since last seen
                time_diff = now - latest.timestamp
                seconds_ago = int(time_diff.total_seconds())
                
                results.append(HostnameMetrics(
                    hostname=latest.hostname,
                    cpu_usage=latest.cpu_usage,
                    memory_usage=latest.memory_usage,
                    disk_usage=latest.disk_usage,
                    operating_system=latest.operating_system,
                    timestamp=latest.timestamp,
                    last_seen_seconds_ago=seconds_ago
                ))
        
        return sorted(results, key=lambda x: x.hostname)
    
    except Exception as e:
        logger.error(f"Error getting latest metrics: {str(e)}")
        return []


def get_metrics_history(
    db: Session,
    user_id: int,
    hostname: str,
    hours: int = 24
) -> List[SystemMetric]:
    """
    Get historical metrics for a specific hostname and user.
    
    Args:
        db: Database session
        user_id: ID of the user
        hostname: The hostname to get history for
        hours: Number of hours to look back (default 24)
    
    Returns:
        List of SystemMetric records in chronological order
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = db.query(SystemMetric).filter(
            and_(
                SystemMetric.user_id == user_id,
                SystemMetric.hostname == hostname,
                SystemMetric.timestamp >= cutoff_time
            )
        ).order_by(SystemMetric.timestamp).all()
        
        return metrics
    
    except Exception as e:
        logger.error(f"Error getting metrics history: {str(e)}")
        return []


def get_metric_stats_for_hostname(
    db: Session,
    user_id: int,
    hostname: str,
    hours: int = 1
) -> dict:
    """
    Calculate statistics (average, max, min) for metrics over a time period.
    
    Args:
        db: Database session
        user_id: ID of the user
        hostname: The hostname
        hours: Time window in hours
    
    Returns:
        Dictionary with avg, max, min for CPU, memory, disk
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = db.query(SystemMetric).filter(
            and_(
                SystemMetric.user_id == user_id,
                SystemMetric.hostname == hostname,
                SystemMetric.timestamp >= cutoff_time
            )
        ).all()
        
        if not metrics:
            return {}
        
        cpu_values = [m.cpu_usage for m in metrics]
        mem_values = [m.memory_usage for m in metrics]
        disk_values = [m.disk_usage for m in metrics]
        
        return {
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory": {
                "avg": sum(mem_values) / len(mem_values),
                "max": max(mem_values),
                "min": min(mem_values)
            },
            "disk": {
                "avg": sum(disk_values) / len(disk_values),
                "max": max(disk_values),
                "min": min(disk_values)
            }
        }
    
    except Exception as e:
        logger.error(f"Error calculating stats: {str(e)}")
        return {}


def cleanup_old_metrics(db: Session, days: int = 30) -> int:
    """
    Delete metrics older than specified number of days.
    
    Args:
        db: Database session
        days: Number of days to keep
    
    Returns:
        Number of records deleted
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        result = db.query(SystemMetric).filter(
            SystemMetric.timestamp < cutoff_time
        ).delete()
        
        db.commit()
        logger.info(f"Cleaned up {result} old metrics")
        return result
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning up old metrics: {str(e)}")
        return 0
