"""Deterministic insights for agent-monitored hosts."""
from typing import Dict, List
from datetime import datetime, timedelta
import logging

from app.services.agent_metrics_service import get_latest_metrics_by_user, get_metric_stats_for_hostname
from app.core.config import settings

logger = logging.getLogger(__name__)


def _severity_label(value: float, warning: int, critical: int) -> str:
    if value >= critical:
        return "critical"
    if value >= warning:
        return "warning"
    return "healthy"


def _format_host_list(hostnames: List[str]) -> str:
    if not hostnames:
        return ""
    if len(hostnames) == 1:
        return hostnames[0]
    return ", ".join(hostnames[:-1]) + f" and {hostnames[-1]}"


def generate_agent_insights(user_id: int, db) -> Dict[str, object]:
    """Generate agent-specific health insights for a user."""
    latest_hosts = get_latest_metrics_by_user(db, user_id)

    if not latest_hosts:
        return {
            "health_summary": "No monitored hosts have reported metrics yet.",
            "recommendations": [
                "Install the monitoring agent on your hosts and register the API key.",
                "Ensure agents can reach the backend and that the API key is valid.",
            ],
            "status": "unknown",
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "component_status": {
                "cpu_usage": "unknown",
                "memory_usage": "unknown",
                "disk_usage": "unknown",
            },
            "alerts": [],
        }

    active_values = [host for host in latest_hosts if host.last_seen_seconds_ago is not None and host.last_seen_seconds_ago <= 60]
    offline_values = [host for host in latest_hosts if host.last_seen_seconds_ago is not None and host.last_seen_seconds_ago > 60]
    avg_cpu = sum(host.cpu_usage for host in latest_hosts) / len(latest_hosts)
    avg_memory = sum(host.memory_usage for host in latest_hosts) / len(latest_hosts)
    avg_disk = sum(host.disk_usage for host in latest_hosts) / len(latest_hosts)

    cpu_status = _severity_label(avg_cpu, settings.CPU_WARNING_THRESHOLD, settings.CPU_CRITICAL_THRESHOLD)
    memory_status = _severity_label(avg_memory, settings.MEMORY_WARNING_THRESHOLD, settings.MEMORY_CRITICAL_THRESHOLD)
    disk_status = _severity_label(avg_disk, settings.DISK_WARNING_THRESHOLD, settings.DISK_CRITICAL_THRESHOLD)

    status_priority = {"healthy": 0, "warning": 1, "critical": 2, "unknown": -1}
    overall_status = max([cpu_status, memory_status, disk_status], key=lambda level: status_priority[level])

    alerts = []
    recommendations = []

    if cpu_status != "healthy":
        cpu_hosts = [host.hostname for host in latest_hosts if host.cpu_usage >= settings.CPU_WARNING_THRESHOLD]
        alerts.append(
            f"High CPU usage on {len(cpu_hosts)} host(s): {_format_host_list(cpu_hosts)}."
        )
        if cpu_status == "critical":
            recommendations.append(
                "Investigate CPU-intensive processes and consider distributing workloads across more hosts."
            )
        else:
            recommendations.append(
                "Monitor CPU spikes and consider auto-scaling options."
            )

    if memory_status != "healthy":
        memory_hosts = [host.hostname for host in latest_hosts if host.memory_usage >= settings.MEMORY_WARNING_THRESHOLD]
        alerts.append(
            f"Memory usage is elevated on {len(memory_hosts)} host(s): {_format_host_list(memory_hosts)}."
        )
        if memory_status == "critical":
            recommendations.append(
                "Review memory utilization patterns and identify potential leaks."
            )
        else:
            recommendations.append(
                "Check memory usage per process and tune caching or buffers."
            )

    if disk_status != "healthy":
        disk_hosts = [host.hostname for host in latest_hosts if host.disk_usage >= settings.DISK_WARNING_THRESHOLD]
        alerts.append(
            f"Disk usage is high on {len(disk_hosts)} host(s): {_format_host_list(disk_hosts)}."
        )
        if disk_status == "critical":
            recommendations.append(
                "Free disk space, rotate logs, or increase volume capacity."
            )
        else:
            recommendations.append(
                "Review storage usage and remove unnecessary files."
            )

    if offline_values:
        alerts.append(
            f"{len(offline_values)} host(s) have not reported in over 60 seconds: {_format_host_list([host.hostname for host in offline_values])}."
        )
        recommendations.append(
            "Verify network connectivity and agent health on the offline hosts."
        )

    if not alerts:
        recommendations = [
            "All monitored hosts are within normal operating ranges.",
            "Continue monitoring and configure alerts for long-running trends.",
        ]

    health_summary = (
        f"Average CPU: {round(avg_cpu)}%, Memory: {round(avg_memory)}%, Disk: {round(avg_disk)}%"
    )

    return {
        "health_summary": health_summary,
        "recommendations": recommendations,
        "status": overall_status,
        "cpu_usage": round(avg_cpu),
        "memory_usage": round(avg_memory),
        "disk_usage": round(avg_disk),
        "component_status": {
            "cpu_usage": cpu_status,
            "memory_usage": memory_status,
            "disk_usage": disk_status,
        },
        "alerts": alerts,
    }
