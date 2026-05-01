"""Configuration for IncidentPilot."""

from __future__ import annotations

import os
from pydantic import BaseModel, Field


class PilotConfig(BaseModel):
    """Runtime configuration for IncidentPilot."""

    openrouter_api_key: str = Field("", description="OpenRouter API key")
    pagerduty_token: str = Field("", description="PagerDuty API token")
    runbook_dir: str = Field("runbooks", description="Path to runbook files")
    industry: str = Field("fintech", description="Industry context")
    model: str = Field("claude-sonnet-4-20250514", description="Claude model to use")
    max_tokens: int = Field(1024, description="Max tokens per agent response")

    @classmethod
    def from_env(cls) -> "PilotConfig":
        return cls(
            openrouter_api_key=os.environ.get("OPENROUTER_API_KEY", ""),
            pagerduty_token=os.environ.get("PAGERDUTY_TOKEN", ""),
            runbook_dir=os.environ.get("RUNBOOK_DIR", "runbooks"),
            industry=os.environ.get("PILOT_INDUSTRY", "fintech"),
        )

    @property
    def has_api_key(self) -> bool:
        return bool(self.openrouter_api_key)