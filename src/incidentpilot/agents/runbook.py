"""Runbook agent â€” retrieves and summarizes relevant runbooks."""

from __future__ import annotations

import re
from pathlib import Path

from incidentpilot.models.incident import Incident, TriageResult, RunbookResult
from incidentpilot.core.config import PilotConfig


def fetch_runbook(
    incident: Incident,
    triage: TriageResult,
    config: PilotConfig,
) -> RunbookResult:
    """Retrieve and summarize relevant runbook for the incident."""
    runbook_dir = Path(config.runbook_dir)
    content = _find_runbook(incident, triage, runbook_dir)

    if not content:
        return _generic_runbook(incident, triage)

    if config.has_api_key:
        return _ai_summarize_runbook(content, incident, config)

    return _extract_runbook_steps(content, incident)


def _find_runbook(incident: Incident, triage: TriageResult, runbook_dir: Path) -> str | None:
    if not runbook_dir.exists():
        return None

    search_terms = [incident.service.lower(), incident.title.lower().split()[0]]
    search_terms.extend(s.lower() for s in triage.affected_services)

    for rb_file in runbook_dir.glob("*.md"):
        stem = rb_file.stem.lower()
        if any(term in stem for term in search_terms):
            return rb_file.read_text(errors="ignore")

    return None


def _ai_summarize_runbook(content: str, incident: Incident, config: PilotConfig) -> RunbookResult:
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=config.openrouter_api_key)
        prompt = f"""Summarize this runbook for an on-call engineer responding to: {incident.title}

Runbook content:
{content[:3000]}

Return a JSON object with:
- runbook_found: true
- runbook_name: string
- key_steps: list of 5-7 actionable steps
- estimated_resolution_minutes: integer
- escalation_triggers: list of conditions that require escalation

Return only valid JSON."""

        import json
        message = client.chat.completions.create(
            model=config.model,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(message.choices[0].message.content)
        return RunbookResult(**data)
    except Exception:
        return _extract_runbook_steps(content, incident)


def _extract_runbook_steps(content: str, incident: Incident) -> RunbookResult:
    steps = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "-", "*")):
            clean = re.sub(r'^[\d\.\-\*\s]+', '', stripped).strip()
            if len(clean) > 10:
                steps.append(clean)
    return RunbookResult(
        runbook_found=True,
        runbook_name=f"{incident.service}-runbook",
        key_steps=steps[:7] if steps else ["Follow standard incident procedure"],
        estimated_resolution_minutes=30,
        escalation_triggers=["No improvement after 30 minutes", "Impact spreading to additional services"],
    )


def _generic_runbook(incident: Incident, triage: TriageResult) -> RunbookResult:
    steps = triage.recommended_actions[:5] if triage.recommended_actions else [
        "Check service health dashboards",
        "Review recent deployments",
        "Check error rates and latency",
        "Verify database connectivity",
        "Consider rollback if deployment-related",
    ]
    return RunbookResult(
        runbook_found=False,
        runbook_name="generic-incident-runbook",
        key_steps=steps,
        estimated_resolution_minutes=45,
        escalation_triggers=["No improvement after 30 minutes", "Customer impact confirmed"],
    )