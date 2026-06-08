from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Query, status

from app.schemas.metrics import MetricPoint, SystemMetrics
from app.services.metrics_service import get_system_metrics

router = APIRouter()


def _build_series(value: int, points: int = 7) -> List[MetricPoint]:
    now = datetime.utcnow()
    offset = points // 2
    series = []
    for index in range(points):
        time_label = (now - timedelta(minutes=(points - index) * 10)).strftime("%H:%M")
        trend_value = max(0, min(100, value + index - offset))
        series.append(MetricPoint(time=time_label, value=trend_value))
    return series


@router.get(
    "/metrics",
    response_model=SystemMetrics,
    status_code=status.HTTP_200_OK,
    tags=["Metrics"],
)
def metrics(time_range: str = Query('1h', alias='time_range')):
    """Return current system metrics and lightweight time-series data."""
    metrics_data = get_system_metrics()
    metrics_data["cpu_history"] = _build_series(metrics_data["cpu_usage"])
    metrics_data["memory_history"] = _build_series(metrics_data["memory_usage"])
    metrics_data["disk_history"] = _build_series(metrics_data["disk_usage"])
    return metrics_data


@router.get(
    "/metrics/cpu",
    response_model=List[MetricPoint],
    status_code=status.HTTP_200_OK,
    tags=["Metrics"],
)
def cpu_metrics(time_range: str = Query('1h', alias='time_range')):
    metrics_data = get_system_metrics()
    return _build_series(metrics_data["cpu_usage"])


@router.get(
    "/metrics/memory",
    response_model=List[MetricPoint],
    status_code=status.HTTP_200_OK,
    tags=["Metrics"],
)
def memory_metrics(time_range: str = Query('1h', alias='time_range')):
    metrics_data = get_system_metrics()
    return _build_series(metrics_data["memory_usage"])


@router.get(
    "/metrics/disk",
    response_model=List[MetricPoint],
    status_code=status.HTTP_200_OK,
    tags=["Metrics"],
)
def disk_metrics(time_range: str = Query('1h', alias='time_range')):
    metrics_data = get_system_metrics()
    return _build_series(metrics_data["disk_usage"])
