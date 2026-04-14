# IncidentPilot

> Multi-agent incident response orchestrator built with LangGraph.

![CI](https://github.com/brianpelow/IncidentPilot/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)

## Overview

IncidentPilot is a multi-agent incident response system built with LangGraph.
When an incident fires, a coordinated crew of specialized agents autonomously
triages severity, routes to the right on-call engineer, retrieves relevant
runbooks, and drafts a structured post-mortem.

Built for SRE teams in regulated financial services and manufacturing.

## Agent crew

- TriageAgent - classifies severity and affected services
- EscalationAgent - determines on-call routing
- RunbookAgent - retrieves and summarizes relevant runbooks
- PostmortemAgent - drafts structured post-mortem documents
- CoordinatorAgent - orchestrates the full response workflow

## Quick start

```bash
pip install IncidentPilot
export ANTHROPIC_API_KEY=your_key
incident-pilot --title "Payment latency spike" --service payments-service
```

## License

Apache 2.0