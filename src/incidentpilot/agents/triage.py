"""Triage agent â€” classifies incident severity and affected services."""

from __future__ import annotations

from incidentpilot.models.incident import Incident, TriageResult
from incidentpilot.core.config import PilotConfig


SEVERITY_KEYWORDS = {
    "critical": ["down", "outage", "unavailable", "breach", "data loss", "payment failure", "complete failure"],
    "high": ["degraded", "slow", "latency", "spike", "elevated", "partial", "intermittent"],
    "medium": ["warning", "increased", "unusual", "anomaly", "approaching"],
    "low": ["informational", "minor", "cosmetic", "non-urgent"],
}


def triage_incident(incident: Incident, config: PilotConfig) -> TriageResult:
    """Classify incident severity and identify affected services."""
    if config.has_api_key:
        return _ai_triage(incident, config)
    return _rule_based_triage(incident)


def _ai_triage(incident: Incident, config: PilotConfig) -> TriageResult:
    """Use Claude to triage the incident."""
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=config.openrouter_api_key)
        prompt = f"""You are an SRE triaging an incident for a {config.industry} platform.

Incident: {incident.title}
Service: {incident.service}
Description: {incident.description}

Respond with a JSON object containing:
- severity: one of critical/high/medium/low
- affected_services: list of service names likely affected
- impact_summary: 1-2 sentence business impact summary
- recommended_actions: list of 3-5 immediate actions
- confidence: high/medium/low

Return only valid JSON, no other text."""

        message = client.chat.completions.create(
            model=config.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        import json
        data = json.loads(message.choices[0].message.content)
        return TriageResult(**data)
    except Exception:
        return _rule_based_triage(incident)


def _rule_based_triage(incident: Incident) -> TriageResult:
    """Rule-based fallback triage."""
    title_lower = incident.title.lower()
    severity = "medium"

    for sev, keywords in SEVERITY_KEYWORDS.items():
        if any(kw in title_lower for kw in keywords):
            severity = sev
            break

    affected = [incident.service] if incident.service else ["unknown"]

    actions = {
        "critical": [
            "Page primary and secondary on-call immediately",
            "Open war room bridge",
            "Notify engineering leadership",
            "Check for recent deployments in last 2 hours",
            "Initiate rollback procedure if deployment-related",
        ],
        "high": [
            "Page primary on-call",
            "Check monitoring dashboards for anomalies",
            "Review recent deployments",
            "Begin investigation in #incidents channel",
        ],
        "medium": [
            "Notify on-call via Slack",
            "Monitor for escalation",
            "Log in incident tracker",
        ],
        "low": [
            "Create ticket for investigation",
            "Monitor during business hours",
        ],
    }.get(severity, ["Investigate and monitor"])

    return TriageResult(
        severity=severity,
        affected_services=affected,
        impact_summary=f"{severity.title()} severity incident affecting {', '.join(affected)}.",
        recommended_actions=actions,
        confidence="medium",
    )