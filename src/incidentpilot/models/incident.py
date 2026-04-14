"""Incident data models."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class Incident(BaseModel):
    """An incident being processed by IncidentPilot."""

    id: str = Field("", description="Incident ID")
    title: str = Field("", description="Incident title")
    service: str = Field("", description="Affected service")
    severity: str = Field("unknown", description="critical/high/medium/low")
    status: str = Field("open", description="open/in-progress/resolved")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    description: str = Field("", description="Additional context")


class TriageResult(BaseModel):
    """Output from the triage agent."""

    severity: str = Field("unknown")
    affected_services: list[str] = Field(default_factory=list)
    impact_summary: str = Field("")
    recommended_actions: list[str] = Field(default_factory=list)
    confidence: str = Field("medium", description="high/medium/low")


class EscalationResult(BaseModel):
    """Output from the escalation agent."""

    oncall_team: str = Field("")
    escalation_path: list[str] = Field(default_factory=list)
    notification_channels: list[str] = Field(default_factory=list)
    bridge_url: str = Field("")
    rationale: str = Field("")


class RunbookResult(BaseModel):
    """Output from the runbook agent."""

    runbook_found: bool = Field(False)
    runbook_name: str = Field("")
    key_steps: list[str] = Field(default_factory=list)
    estimated_resolution_minutes: int = Field(30)
    escalation_triggers: list[str] = Field(default_factory=list)


class PostmortemResult(BaseModel):
    """Output from the postmortem agent."""

    title: str = Field("")
    summary: str = Field("")
    timeline: list[str] = Field(default_factory=list)
    root_cause: str = Field("")
    contributing_factors: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    compliance_notes: str = Field("")


class IncidentResponse(BaseModel):
    """Complete incident response package."""

    incident: Incident
    triage: Optional[TriageResult] = None
    escalation: Optional[EscalationResult] = None
    runbook: Optional[RunbookResult] = None
    postmortem: Optional[PostmortemResult] = None
    status: str = Field("pending")
    completed_at: Optional[str] = None