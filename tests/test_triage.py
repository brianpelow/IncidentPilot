"""Tests for triage agent."""

from incidentpilot.core.config import PilotConfig
from incidentpilot.models.incident import Incident
from incidentpilot.agents.triage import triage_incident, _rule_based_triage


def make_config() -> PilotConfig:
    return PilotConfig()


def test_triage_critical_incident() -> None:
    incident = Incident(title="Complete payment service outage", service="payments-service")
    result = _rule_based_triage(incident)
    assert result.severity == "critical"


def test_triage_high_incident() -> None:
    incident = Incident(title="Payment service latency spike", service="payments-service")
    result = _rule_based_triage(incident)
    assert result.severity == "high"


def test_triage_returns_actions() -> None:
    incident = Incident(title="Auth service degraded", service="auth-service")
    result = _rule_based_triage(incident)
    assert len(result.recommended_actions) > 0


def test_triage_includes_service() -> None:
    incident = Incident(title="FX rate feed slow", service="fx-rate-service")
    result = _rule_based_triage(incident)
    assert "fx-rate-service" in result.affected_services


def test_triage_no_api_key_uses_rules() -> None:
    config = make_config()
    incident = Incident(title="Database connection errors", service="payments-db")
    result = triage_incident(incident, config)
    assert result.severity in ("critical", "high", "medium", "low")