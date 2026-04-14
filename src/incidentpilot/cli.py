"""IncidentPilot CLI entry point."""

from __future__ import annotations

import json
import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from incidentpilot.core.config import PilotConfig
from incidentpilot.models.incident import Incident
from incidentpilot.agents.coordinator import run_incident_workflow

app = typer.Typer(name="incident-pilot", help="Multi-agent incident response orchestrator.")
console = Console()


@app.command()
def main(
    title: str = typer.Option(..., "--title", "-t", help="Incident title"),
    service: str = typer.Option("unknown", "--service", "-s", help="Affected service"),
    severity: str = typer.Option("", "--severity", help="Override severity (critical/high/medium/low)"),
    description: str = typer.Option("", "--description", "-d", help="Additional context"),
    output_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Run the full incident response workflow for an incident."""
    config = PilotConfig.from_env()

    incident = Incident(
        id=f"INC-{__import__('datetime').datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        title=title,
        service=service,
        severity=severity,
        description=description,
    )

    console.print(f"\n[bold blue]IncidentPilot[/bold blue] — processing: [yellow]{title}[/yellow]\n")

    response = run_incident_workflow(incident, config)

    if output_json:
        print(json.dumps(response.model_dump(), indent=2))
        return

    if response.triage:
        console.print(Panel.fit(
            f"Severity: [bold red]{response.triage.severity.upper()}[/bold red]\n"
            f"Affected: {', '.join(response.triage.affected_services)}\n"
            f"Impact: {response.triage.impact_summary}",
            title="Triage",
        ))

    if response.escalation:
        console.print(Panel.fit(
            f"Team: [cyan]{response.escalation.oncall_team}[/cyan]\n"
            f"Channels: {', '.join(response.escalation.notification_channels)}\n"
            f"Bridge: {response.escalation.bridge_url}",
            title="Escalation",
        ))

    if response.runbook:
        steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(response.runbook.key_steps[:5]))
        console.print(Panel.fit(
            f"Runbook: [green]{response.runbook.runbook_name}[/green]\n"
            f"Est. resolution: {response.runbook.estimated_resolution_minutes} min\n\n"
            f"Key steps:\n{steps}",
            title="Runbook",
        ))

    if response.postmortem:
        console.print(Panel.fit(
            f"{response.postmortem.summary}\n\n"
            f"[bold]Root cause:[/bold] {response.postmortem.root_cause}\n\n"
            f"[bold]Compliance:[/bold] {response.postmortem.compliance_notes}",
            title="Post-mortem draft",
        ))

    console.print(f"\n[green]✓ Workflow complete[/green] — {response.completed_at}\n")


if __name__ == "__main__":
    app()