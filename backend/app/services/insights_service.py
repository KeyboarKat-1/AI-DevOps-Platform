"""Deterministic insights generator that does not rely on external AI services.

This will always return a valid local insights payload derived from system
metrics. It intentionally avoids calling OpenAI or raising OpenAI-related
exceptions so the system remains functional without external AI.
"""

from typing import Dict
from app.services.metrics_service import get_system_metrics


def _build_health_summary(metrics: Dict) -> str:
    lines = [
        f"CPU: {metrics.get('cpu_usage', 0)}% ({metrics.get('component_status',{}).get('cpu_usage','healthy')})",
        f"Memory: {metrics.get('memory_usage', 0)}% ({metrics.get('component_status',{}).get('memory_usage','healthy')})",
        f"Disk: {metrics.get('disk_usage', 0)}% ({metrics.get('component_status',{}).get('disk_usage','healthy')})",
    ]
    return " | ".join(lines)


async def generate_ai_insights() -> dict:
    metrics = get_system_metrics()

    # Base deterministic recommendations
    recs = []
    if metrics.get('component_status', {}).get('cpu_usage') != 'healthy':
        recs.append(
            f"CPU at {metrics.get('cpu_usage')}% — consider scaling compute or throttling heavy jobs."
        )
    if metrics.get('component_status', {}).get('memory_usage') != 'healthy':
        recs.append(
            f"Memory at {metrics.get('memory_usage')}% — investigate memory usage and tune caches."
        )
    if metrics.get('component_status', {}).get('disk_usage') != 'healthy':
        recs.append(
            f"Disk at {metrics.get('disk_usage')}% — rotate logs or increase volume size."
        )

    if not recs:
        recs = [
            "Monitor long-running processes and schedule maintenance windows.",
            "Keep system packages and dependencies up-to-date.",
        ]

    return {
        "health_summary": _build_health_summary(metrics),
        "recommendations": recs,
        "status": metrics.get('status', 'healthy'),
        "cpu_usage": metrics.get('cpu_usage', 0),
        "memory_usage": metrics.get('memory_usage', 0),
        "disk_usage": metrics.get('disk_usage', 0),
        "component_status": metrics.get('component_status', {}),
        "alerts": metrics.get('alerts', []),
    }


async def generate_contextual_suggestion(context: str) -> dict:
    metrics = get_system_metrics()
    insights = await generate_ai_insights()
    return {
        "suggestion": (
            f"Based on your request, '{context}', the system health is {insights['status']} "
            f"({insights['health_summary']}). Key recommendations: {insights['recommendations'][0]}. "
            f"Additional note: {insights['recommendations'][1] if len(insights['recommendations']) > 1 else ''}"
        )
    }
