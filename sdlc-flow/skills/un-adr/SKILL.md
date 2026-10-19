---
name: "un-adr"
description: "Record Architecture Decision Records in the design phase: capture each significant decision, its context, options considered, the chosen approach, and consequences. Outputs .sdlc/adr/<nnn>-<title>.md. Part of sdlc-flow."
agent_created: true
---

# un-adr

Architecture decisions are cheap to record and expensive to forget.

## When to use
- During `un-tech-design`, whenever a **significant** decision is made (tech choice,
  pattern, trade-off) that future readers will question.

## Workflow
1. Number sequentially: `.sdlc/adr/<nnn>-<kebab-title>.md`.
2. Fill from `../../shared/adr-template.md`:
   - **Context**: what forces the decision.
   - **Options**: 2+ realistic alternatives with pros/cons.
   - **Decision**: what we chose.
   - **Consequences**: what gets easier/harder, including the reversibility cost.
3. Link the ADR from `.sdlc/design.md` where the decision is used.

## Output
One ADR file per decision under `.sdlc/adr/`.

## Rules
- Record the decision *and* why the alternatives were rejected — that's the value.
- Don't ADR trivial choices; reserve for things that are hard to change later.

## Cross-references
- Sits inside the design phase; referenced by `un-task-breakdown` and future maintainers.
