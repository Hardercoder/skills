---
name: "un-threat-modeling"
description: "Security threat modeling in the design phase: identify assets, trust boundaries, threats (STRIDE), and mitigations; outputs .sdlc/threat-model.md. Use when the design touches auth, data, network, or untrusted input. Part of sdlc-flow."
agent_created: true
---

# un-threat-modeling

Think like an attacker while the design is still cheap to change.

## When to use
- During `un-tech-design`, whenever the system handles auth, sensitive data,
  network exposure, or any untrusted input.

## Workflow
1. Read `.sdlc/design.md`.
2. Enumerate **assets** (what's valuable) and **trust boundaries** (where trust changes).
3. Apply **STRIDE** at each boundary: Spoofing, Tampering, Repudiation, Info disclosure,
   Denial of service, Elevation of privilege.
4. For each real threat: likelihood × impact, and a concrete **mitigation**.
5. Write `.sdlc/threat-model.md` from `../../shared/threat-model-template.md`.

## Output
`.sdlc/threat-model.md` — assets, boundaries, STRIDE table, mitigations, open risks.

## Rules
- Focus on the highest-impact boundaries first; don't boil the ocean.
- Each mitigation should be assignable to a task in `un-task-breakdown`.

## Cross-references
- Input to `un-task-breakdown` (security tasks) and `un-verify-before-done` (security checks).
