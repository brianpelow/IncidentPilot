"""Tests for incident data models."""

from incidentpilot.models.incident import (
    Incident, TriageResult, EscalationResult, RunbookResult, PostmortemResult, IncidentResponse
)


def test_incident_defaults() -> None:
    inc = Incident(title="Test incident", service="payments-service")
    assert inc.status == "open"
    assert inc.severity == "unknown"


def test_triage_result_defaults() -> None:
    triage = TriageResult()
    assert triage.severity == "unknown"
    assert triage.confidence == "medium"
    assert triage.affected_services == []


def test_escalation_result_defaults() -> None:
    esc = EscalationResult()
    assert esc.oncall_team == ""
    assert esc.escalation_path == []


def test_runbook_result_defaults() -> None:
    rb = RunbookResult()
    assert rb.runbook_found is False
    assert rb.estimated_resolution_minutes == 30


def test_postmortem_result_defaults() -> None:
    pm = PostmortemResult()
    assert pm.action_items == []
    assert pm.timeline == []


def test_incident_response_defaults() -> None:
    inc = Incident(title="Test", service="svc")
    response = IncidentResponse(incident=inc)
    assert response.status == "pending"
    assert response.triage is None