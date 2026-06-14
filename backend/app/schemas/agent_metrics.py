"""Pydantic schemas for agent-based system metrics."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class SystemMetricSubmit(BaseModel):
    """Schema for metrics submitted by monitoring agents."""

    hostname: str = Field(..., description="Hostname of the monitored machine")
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage (0-100)")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage (0-100)")
    disk_usage: float = Field(..., ge=0, le=100, description="Disk usage percentage (0-100)")
    operating_system: str = Field(..., description="Operating system name (e.g., Windows, Linux)")
    timestamp: Optional[datetime] = Field(default=None, description="Metric timestamp (UTC)")

    @validator('hostname')
    def validate_hostname(cls, v: str) -> str:
        """Ensure hostname is not empty."""
        if not v or not v.strip():
            raise ValueError('Hostname cannot be empty')
        return v.strip()

    @validator('operating_system')
    def validate_os(cls, v: str) -> str:
        """Ensure OS is not empty."""
        if not v or not v.strip():
            raise ValueError('Operating system cannot be empty')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "hostname": "desktop-machine",
                "cpu_usage": 45.5,
                "memory_usage": 62.3,
                "disk_usage": 75.8,
                "operating_system": "Windows",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class SystemMetricResponse(BaseModel):
    """Schema for returning a system metric record."""

    id: int
    user_id: int
    hostname: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    operating_system: str
    timestamp: datetime

    class Config:
        from_attributes = True


class HostnameMetrics(BaseModel):
    """Schema for the latest metrics from a specific hostname."""

    hostname: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    operating_system: str
    timestamp: datetime
    last_seen_seconds_ago: Optional[int] = None

    class Config:
        from_attributes = True


class HostnamesMetricsResponse(BaseModel):
    """Schema for returning metrics grouped by hostname."""

    hostnames: List[HostnameMetrics]


class MetricsHistoryResponse(BaseModel):
    """Schema for returning historical metrics for charts."""

    hostname: str
    metrics: List[SystemMetricResponse]


class AgentApiKeyCreate(BaseModel):
    """Schema for creating a new agent API key."""

    name: str = Field(..., description="Human-readable name for this key (e.g., Office Desktop)")
    hostname: Optional[str] = Field(None, description="Optional hostname to associate with this key")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Office Desktop",
                "hostname": "office-pc-01"
            }
        }


class AgentApiKeyResponse(BaseModel):
    """Schema for returning an agent API key (with key visible only on creation)."""

    id: int
    name: str
    hostname: Optional[str]
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime]

    class Config:
        from_attributes = True


class AgentApiKeyWithSecret(BaseModel):
    """Schema for returning a newly created API key (includes the secret)."""

    id: int
    name: str
    hostname: Optional[str]
    api_key: str = Field(..., description="The actual API key - only shown once")
    is_active: bool
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Office Desktop",
                "hostname": "office-pc-01",
                "api_key": "abc123def456...",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
