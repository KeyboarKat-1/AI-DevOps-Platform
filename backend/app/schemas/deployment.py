from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DeploymentBase(BaseModel):
    service_name: str = Field(..., example="payment-service")
    environment: str = Field(..., example="production")
    status: str = Field(..., example="success")
    deployed_at: Optional[datetime] = Field(
        None,
        example="2026-05-21T15:30:00Z",
        description="UTC timestamp when the service was deployed. If omitted, server time is used.",
    )


class DeploymentCreate(DeploymentBase):
    pass


class DeploymentRead(DeploymentBase):
    id: int

    class Config:
        from_attributes = True
