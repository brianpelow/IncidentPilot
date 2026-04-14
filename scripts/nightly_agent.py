"""Nightly agent — automated maintenance for IncidentPilot."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

REPO_ROOT = Path(__file__).parent.parent


def run_mock_workflow() -> None:
    """Run a mock incident workflow and save the output."""
    from incidentpilot.core.config import PilotConfig
    from incidentpilot.models.incident import Incident
    from incidentpilot.agents.coordinator import run_incident_workflow

    config = PilotConfig()
    incident = Incident(
        id="NIGHTLY-TEST",
        title="Nightly agent test — payment latency spike",
        service="payments-service",
        description="Automated nightly workflow validation",
    )

    response = run_incident_workflow(incident, config)

    out = REPO_ROOT / "docs" / "nightly-workflow-sample.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(response.model_dump(), indent=2))
    print(f"[agent] Mock workflow complete — severity: {response.triage.severity if response.triage else 'unknown'} -> {out}")


def refresh_changelog() -> None:
    changelog = REPO_ROOT / "CHANGELOG.md"
    if not changelog.exists():
        return
    today = date.today().isoformat()
    content = changelog.read_text()
    if today not in content:
        content = content.replace("## [Unreleased]", f"## [Unreleased]\n\n_Last checked: {today}_", 1)
        changelog.write_text(content)
    print("[agent] Refreshed CHANGELOG timestamp")


if __name__ == "__main__":
    print(f"[agent] Starting nightly agent - {date.today().isoformat()}")
    run_mock_workflow()
    refresh_changelog()
    print("[agent] Done.")