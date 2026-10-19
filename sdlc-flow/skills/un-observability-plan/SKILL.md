---
name: "un-observability-plan"
description: "Observability plan: structured logging, metrics, tracing, alerting, and dashboards for the new system; outputs .sdlc/observability-plan.md. Use before production rollout. Part of sdlc-flow."
agent_created: true
---

# un-observability-plan

You can't operate what you can't see.

## When to use
- After the test phase, before a system goes to production.

## Workflow
1. Define the **signal trio**:
   - structured **logs** (what happened, with context),
   - **metrics** (rate, error, duration — RED),
   - **traces** (request flow across services).
2. Specify **alerts** on the metrics that page a human, with thresholds.
3. Sketch the **dashboards** a responder needs during an incident.
4. Write `.sdlc/observability-plan.md` from `../../shared/observability-template.md`.

## Output
`.sdlc/observability-plan.md` — signals, alerts, dashboards, ownership.

## Rules
- Alert on symptoms users feel, not on every log line.
- Make sure `un-release-checklist` health checks use these signals.

## Cross-references
- Feeds `un-release-checklist` health checks and `un-postmortem` post-incident.
