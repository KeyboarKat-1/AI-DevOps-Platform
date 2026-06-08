from typing import List
from pydantic import BaseModel


class AIInsightsResponse(BaseModel):
    cpu_usage: int
    memory_usage: int
    disk_usage: int
    status: str
    health_summary: str
    recommendations: List[str]
    alerts: list[str] = []
    component_status: dict


class AISuggestionRequest(BaseModel):
    context: str


class AISuggestionResponse(BaseModel):
    suggestion: str
