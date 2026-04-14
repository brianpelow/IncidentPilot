"""Tests for the coordinator agent."""

from incidentpilot.core.config import PilotConfig
from incidentpilot.models.incident import Incident
from incidentpilot.agents.coordinator import run_incident_workflow


def test_workflow_returns_complete_response() -> None:
    config = PilotConfig()
    incident = Incident(title="Payment latency spike", service="payments-service")
    response = run_incident_workflow(incident, config)
    assert response.status == "complete"
    assert response.triage is not None
    assert response.escalation is not None
    assert response.runbook is not None
    assert response.postmortem is not None


def test_workflow_sets_severity() -> None:
    config = PilotConfig()
    incident = Incident(title="Complete payment outage", service="payments-service")
    response = run_incident_workflow(incident, config)
    assert incident.severity in ("critical", "high", "medium", "low")


def test_workflow_completes_at_set() -> None:
    config = PilotConfig()
    incident = Incident(title="Test incident", service="auth-service")
    response = run_incident_workflow(incident, config)
    assert response.completed_at is not None


def test_workflow_postmortem_has_action_items() -> None:
    config = PilotConfig()
    incident = Incident(title="Auth service degraded", service="auth-service")
    response = run_incident_workflow(incident, config)
    assert response.postmortem is not None
    assert len(response.postmortem.action_items) > 0