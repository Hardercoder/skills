---
name: "un-postmortem"
description: "Incident postmortem: timeline, impact, root cause, contributing factors, and action items; outputs .sdlc/postmortem/<date>-<title>.md. Use after a production incident, blameless. Part of sdlc-flow."
agent_created: true
---

# un-postmortem

A blameless retro that turns an incident into prevention.

## When to use
- After a production incident is resolved and service is restored.

## Workflow
1. Create `.sdlc/postmortem/<YYYY-MM-DD>-<title>.md` from
   `../../shared/postmortem-template.md`.
2. **Timeline**: factual sequence with timestamps (detect → mitigate → resolve).
3. **Impact**: who/what was affected, duration, magnitude.
4. **Root cause** + **contributing factors** (the latter is where real fixes live).
5. **Action items**: each assigned, with a due date, and traced to a `un-task-breakdown` task.

## Output
One postmortem file per incident.

## Rules
- Blameless: focus on systems and process, not individuals.
- Every action item must be owned and scheduled or it never happens.

## Cross-references
- Consumes `un-observability-plan` (the signals that detected the incident) and
  `un-systematic-debugging` (the fix). Feeds back into `un-tech-design` via ADRs.
