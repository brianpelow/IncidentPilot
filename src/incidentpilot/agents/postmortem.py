"""Postmortem agent — drafts structured post-mortem documents."""

from __future__ import annotations

from datetime import datetime
from incidentpilot.models.incident import Incident, TriageResult, EscalationResult, RunbookResult, PostmortemResult
from incidentpilot.core.config import PilotConfig


def draft_postmortem(
    incident: Incident,
    triage: TriageResult,
    escalation: EscalationResult,
    runbook: RunbookResult,
    config: PilotConfig,
) -> PostmortemResult:
    """Draft a structured post-mortem for the incident."""
    if config.has_api_key:
        return _ai_postmortem(incident, triage, escalation, runbook, config)
    return _template_postmortem(incident, triage, escalation, runbook, config)


def _ai_postmortem(
    incident: Incident,
    triage: TriageResult,
    escalation: EscalationResult,
    runbook: RunbookResult,
    config: PilotConfig,
) -> PostmortemResult:
    try:
        import anthropic
        import json
        client = anthropic.Anthropic(api_key=config.anthropic_api_key)

        prompt = f"""You are an SRE writing a blameless post-mortem for a {config.industry} engineering team.

Incident: {incident.title}
Service: {incident.service}
Severity: {triage.severity}
Affected services: {', '.join(triage.affected_services)}
Impact: {triage.impact_summary}
On-call team: {escalation.oncall_team}
Runbook used: {runbook.runbook_name}
Estimated resolution: {runbook.estimated_resolution_minutes} minutes

Write a blameless post-mortem as JSON with:
- title: string
- summary: 2-3 sentence executive summary
- timeline: list of 5-7 timeline entries (format: "HH:MM - event description")
- root_cause: 1-2 sentence root cause statement
- contributing_factors: list of 3-5 contributing factors
- action_items: list of 5-7 specific, assignable action items
- compliance_notes: compliance implications for {config.industry} (SOX, PCI-DSS, FFIEC as relevant)

Return only valid JSON."""

        message = client.messages.create(
            model=config.model,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(message.content[0].text)
        return PostmortemResult(**data)
    except Exception:
        return _template_postmortem(incident, triage, escalation, runbook, config)


def _template_postmortem(
    incident: Incident,
    triage: TriageResult,
    escalation: EscalationResult,
    runbook: RunbookResult,
    config: PilotConfig,
) -> PostmortemResult:
    now = datetime.utcnow().strftime("%H:%M")
    return PostmortemResult(
        title=f"Post-Mortem: {incident.title}",
        summary=(
            f"A {triage.severity} severity incident affected {incident.service} "
            f"and was handled by {escalation.oncall_team}. "
            f"Estimated resolution time: {runbook.estimated_resolution_minutes} minutes."
        ),
        timeline=[
            f"{now} - Incident triggered: {incident.title}",
            f"{now} - Triage completed, severity classified as {triage.severity}",
            f"{now} - {escalation.oncall_team} paged via {', '.join(escalation.notification_channels[:2])}",
            f"{now} - Runbook {runbook.runbook_name} retrieved and executed",
            f"{now} - Service restored, monitoring confirmed stable",
            f"{now} - Post-mortem drafted",
        ],
        root_cause=f"Root cause under investigation for {incident.service}. See action items.",
        contributing_factors=[
            "Insufficient alerting threshold calibration",
            "Missing automated runbook execution",
            "Gap in end-to-end monitoring coverage",
        ],
        action_items=[
            f"Review and tune alerting thresholds for {incident.service}",
            "Add automated health check for affected code path",
            f"Update runbook {runbook.runbook_name} with lessons learned",
            "Schedule chaos engineering exercise to validate detection",
            f"Review on-call rotation for {escalation.oncall_team}",
            "Implement automated rollback trigger for this failure mode",
        ],
        compliance_notes=(
            f"This incident must be logged in the change management system within 1 hour per "
            f"{'FFIEC and SOX requirements' if config.industry == 'fintech' else 'IEC 62443 requirements'}. "
            f"Post-mortem review required within 5 business days."
        ),
    )