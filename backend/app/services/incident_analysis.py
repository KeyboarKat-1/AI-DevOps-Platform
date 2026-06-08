"""Provide a local deterministic incident analysis without calling OpenAI.

This function returns a small, helpful JSON payload suitable for UI display
when external AI is disabled or unavailable.
"""

from app.schemas.incident import IncidentAnalysisResponse


async def analyze_incident(service_name: str, error_message: str, environment: str) -> IncidentAnalysisResponse:
    summary = (
        f"Summary: {service_name} reported '{error_message}'. "
        "Check recent deployments, database connectivity, and resource limits."
    )
    root = "Likely root cause: resource exhaustion or failing dependency."
    fix = "Suggested fix: inspect logs, restart service, increase resources, or roll back recent changes."
    combined = f"{summary} Root cause: {root} Suggested fix: {fix}"
    return IncidentAnalysisResponse(analysis=combined)
