from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class IncidentAnalyzeRequest(BaseModel):
    service_name: str = Field(..., example="payment-service")
    error_message: str = Field(..., example="TimeoutError: connection pool exhausted")
    environment: str = Field(..., example="production")


class IncidentAnalysisResponse(BaseModel):
    analysis: str = Field(
        ..., example="Summary: The service experienced a connection pool exhaustion. Root cause: the database pool is too small for the traffic pattern. Suggested fix: increase the pool size and add retry/backoff logic."
    )


class IncidentCreate(BaseModel):
    title: str = Field(..., example="Database connection timeout")
    description: str = Field(..., example="The payment API is unable to connect to the database under heavy load.")
    service_name: str = Field(..., example="payment-service")
    environment: str = Field(..., example="production")
    priority: str = Field(..., example="critical")
    detected_at: Optional[datetime] = Field(None, example="2026-05-25T14:45:00Z")


class IncidentRead(IncidentCreate):
    id: int
    status: str = Field(..., example="active")
    resolved_at: Optional[datetime] = Field(None, example="2026-05-25T15:30:00Z")

    class Config:
        from_attributes = True
