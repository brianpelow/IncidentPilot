"""Coordinator agent — orchestrates the full incident response workflow."""

from __future__ import annotations

from datetime import datetime
from incidentpilot.models.incident import Incident, IncidentResponse
from incidentpilot.agents.triage import triage_incident
from incidentpilot.agents.escalation import escalate_incident
from incidentpilot.agents.runbook import fetch_runbook
from incidentpilot.agents.postmortem import draft_postmortem
from incidentpilot.core.config import PilotConfig


def run_incident_workflow(incident: Incident, config: PilotConfig) -> IncidentResponse:
    """Run the full multi-agent incident response workflow."""
    response = IncidentResponse(incident=incident, status="in-progress")

    response.triage = triage_incident(incident, config)
    incident.severity = response.triage.severity

    response.escalation = escalate_incident(incident, response.triage, config)

    response.runbook = fetch_runbook(incident, response.triage, config)

    response.postmortem = draft_postmortem(
        incident, response.triage, response.escalation, response.runbook, config
    )

    response.status = "complete"
    response.completed_at = datetime.utcnow().isoformat()
    return response