"""Escalation agent — determines on-call routing and notification strategy."""

from __future__ import annotations

from incidentpilot.models.incident import Incident, TriageResult, EscalationResult
from incidentpilot.core.config import PilotConfig


SERVICE_TEAMS = {
    "payments-service": "payments-team",
    "payments": "payments-team",
    "fx-rate-service": "trading-team",
    "trading-engine": "trading-team",
    "auth-service": "platform-team",
    "audit-service": "platform-team",
    "api-gateway": "platform-team",
}

ESCALATION_PATHS = {
    "critical": ["L1 On-call", "L2 Team Lead", "Engineering Manager", "VP Engineering"],
    "high": ["L1 On-call", "L2 Team Lead"],
    "medium": ["L1 On-call"],
    "low": ["L1 On-call (async)"],
}


def escalate_incident(
    incident: Incident,
    triage: TriageResult,
    config: PilotConfig,
) -> EscalationResult:
    """Determine escalation path and notification strategy."""
    team = _resolve_team(incident.service, triage.affected_services)
    path = ESCALATION_PATHS.get(triage.severity, ["L1 On-call"])

    channels = ["#incidents"]
    if triage.severity in ("critical", "high"):
        channels.append(f"#{team}")
        channels.append("#engineering-leadership")

    return EscalationResult(
        oncall_team=team,
        escalation_path=[f"{team} {level}" for level in path],
        notification_channels=channels,
        bridge_url=f"https://meet.example.com/incident-{incident.id or 'bridge'}",
        rationale=f"{triage.severity.title()} severity incident on {incident.service} routed to {team}.",
    )


def _resolve_team(service: str, affected_services: list[str]) -> str:
    service_lower = service.lower()
    for svc_key, team in SERVICE_TEAMS.items():
        if svc_key in service_lower:
            return team
    for svc in affected_services:
        for svc_key, team in SERVICE_TEAMS.items():
            if svc_key in svc.lower():
                return team
    return "platform-team"