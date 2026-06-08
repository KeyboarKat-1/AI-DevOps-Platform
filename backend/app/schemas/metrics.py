from typing import List, Optional

from pydantic import BaseModel


class MetricPoint(BaseModel):
    time: str
    value: int


class ComponentStatus(BaseModel):
    cpu_usage: str
    memory_usage: str
    disk_usage: str


class SystemMetrics(BaseModel):
    """Public response model for the system metrics endpoint.

    - `cpu_usage`, `memory_usage`, `disk_usage` are integers (percent).
    - `status` is the overall health: "healthy", "warning", or "critical".
    - `component_status` contains per-resource severity.
    - `alerts` contains any active usage warnings.
    """

    cpu_usage: int
    memory_usage: int
    disk_usage: int
    status: str
    alert_level: str
    component_status: ComponentStatus
    alerts: list[str] = []
    cpu_history: Optional[List[MetricPoint]] = None
    memory_history: Optional[List[MetricPoint]] = None
    disk_history: Optional[List[MetricPoint]] = None
