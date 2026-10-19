---
name: "un-release-checklist"
description: "Pre-release checklist: version bump, changelog, migration notes, env/secrets, rollback plan, and health checks; outputs .sdlc/release-checklist.md. Use before shipping any release. Part of sdlc-flow."
agent_created: true
---

# un-release-checklist

A go/no-go gate so releases stop shipping surprises.

## When to use
- After the test phase, right before tagging / deploying a release.

## Workflow
1. Walk the checklist in `.sdlc/release-checklist.md` (from
   `../../shared/release-checklist-template.md`):
   - version bump + changelog,
   - DB / data migrations and their rollback,
   - environment variables & secrets present in target,
   - **rollback plan** (how to undo this release),
   - post-deploy health checks & alerts.
2. Tick each item; anything unticked blocks the release.
3. Attach the checklist to the release notes / PR.

## Output
`.sdlc/release-checklist.md` — per-item status, blockers, rollback plan.

## Rules
- "We'll watch it" is not a rollback plan. Write the undo steps.
- Pair with `un-observability-plan` so health checks mean something.

## Cross-references
- Consumes `un-doc-gen` (changelog) and `un-observability-plan`; precedes `un-cicd`.
