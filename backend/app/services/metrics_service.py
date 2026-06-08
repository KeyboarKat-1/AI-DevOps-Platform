"""Service layer to collect system metrics using psutil.

Provides `get_system_metrics()` which returns a compact, API-friendly
dictionary containing percent-based `cpu_usage`, `memory_usage`,
and `disk_usage` as integers and a simple `status` string.

This service follows clean architecture: it is a pure use-case layer
and depends only on `psutil` (no FastAPI imports).
"""
from typing import Dict

import psutil

from app.core.config import settings


def _choose_disk_mountpoint() -> str:
    """Return a sensible disk mountpoint for disk usage checks.

    Prefer root (`/`) for Unix-like systems; fall back to the first
    mounted partition for Windows or other environments.
    """
    try:
        return "/"
    except Exception:
        parts = psutil.disk_partitions()
        return parts[0].mountpoint if parts else "/"


def get_system_metrics() -> Dict[str, object]:
    """Gather system metrics and derive a health `status`.

    Returns a dict like:
    {
      "cpu_usage": 35,
      "memory_usage": 60,
      "disk_usage": 40,
      "status": "healthy"
    }
    """
    # Small blocking call to get a recent CPU usage sample
    cpu = psutil.cpu_percent(interval=0.5)

    mem = psutil.virtual_memory()
    memory_percent = mem.percent

    # Determine a mountpoint that will work cross-platform
    try:
        disk = psutil.disk_usage("/")
    except Exception:
        parts = psutil.disk_partitions()
        mountpoint = parts[0].mountpoint if parts else "/"
        disk = psutil.disk_usage(mountpoint)

    disk_percent = disk.percent

    # Convert to int percentages for API simplicity
    cpu_int = int(round(cpu))
    mem_int = int(round(memory_percent))
    disk_int = int(round(disk_percent))

    def classify(value: int, warning_threshold: int, critical_threshold: int) -> str:
        if value >= critical_threshold:
            return "critical"
        if value >= warning_threshold:
            return "warning"
        return "healthy"

    cpu_status = classify(cpu_int, settings.CPU_WARNING_THRESHOLD, settings.CPU_CRITICAL_THRESHOLD)
    memory_status = classify(mem_int, settings.MEMORY_WARNING_THRESHOLD, settings.MEMORY_CRITICAL_THRESHOLD)
    disk_status = classify(disk_int, settings.DISK_WARNING_THRESHOLD, settings.DISK_CRITICAL_THRESHOLD)

    status_priority = {"healthy": 0, "warning": 1, "critical": 2}
    overall_status = max([cpu_status, memory_status, disk_status], key=lambda level: status_priority[level])
    alert_level = overall_status

    alerts = []
    if cpu_status != "healthy":
        alerts.append(
            f"CPU usage is {cpu_int}% and classified as {cpu_status}. Consider scaling CPU capacity or reducing intensive processes."
        )
    if memory_status != "healthy":
        alerts.append(
            f"Memory usage is {mem_int}% and classified as {memory_status}. Check memory-heavy applications or increase available RAM."
        )
    if disk_status != "healthy":
        alerts.append(
            f"Disk usage is {disk_int}% and classified as {disk_status}. Free disk space or clean temporary files."
        )

    return {
        "cpu_usage": cpu_int,
        "memory_usage": mem_int,
        "disk_usage": disk_int,
        "status": overall_status,
        "alert_level": alert_level,
        "component_status": {
            "cpu_usage": cpu_status,
            "memory_usage": memory_status,
            "disk_usage": disk_status,
        },
        "alerts": alerts,
    }
