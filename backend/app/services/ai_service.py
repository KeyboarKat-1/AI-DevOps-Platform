"""Fallback incident analysis service without external AI.

When OpenAI is unavailable, return a concise deterministic analysis string
that provides a summary, likely root cause, and a suggested fix. This keeps
the system functional without external API keys or network calls.
"""

def analyze_incident(service_name: str, error_message: str, environment: str) -> str:
    summary = f"Service {service_name} in {environment} reported: {error_message}"[:300]
    root = "Likely root cause: investigate recent deployments, failing dependencies, or resource exhaustion."
    fix = "Suggested fix: check logs, restart affected services, and roll back recent changes if needed."
    return f"{summary} | {root} | {fix}"
