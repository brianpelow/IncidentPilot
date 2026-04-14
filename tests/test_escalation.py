"""Tests for escalation agent."""

from incidentpilot.core.config import PilotConfig
from incidentpilot.models.incident import Incident, TriageResult
from incidentpilot.agents.escalation import escalate_incident, _resolve_team


def test_resolve_payments_team() -> None:
    assert _resolve_team("payments-service", []) == "payments-team"


def test_resolve_trading_team() -> None:
    assert _resolve_team("fx-rate-service", []) == "trading-team"


def test_resolve_platform_team_fallback() -> None:
    assert _resolve_team("unknown-service", []) == "platform-team"


def test_escalation_critical_has_leadership() -> None:
    incident = Incident(title="Payment outage", service="payments-service")
    triage = TriageResult(severity="critical", affected_services=["payments-service"])
    config = PilotConfig()
    result = escalate_incident(incident, triage, config)
    assert "#engineering-leadership" in result.notification_channels


def test_escalation_low_minimal_channels() -> None:
    incident = Incident(title="Minor warning", service="payments-service")
    triage = TriageResult(severity="low", affected_services=["payments-service"])
    config = PilotConfig()
    result = escalate_incident(incident, triage, config)
    assert "#incidents" in result.notification_channels