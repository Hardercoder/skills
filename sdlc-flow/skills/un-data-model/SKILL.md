---
name: "un-data-model"
description: "Design the data model in the design phase: entities, relationships, keys, indexes, and lifecycle; outputs .sdlc/data-model.md. Use before any schema implementation. Part of sdlc-flow."
agent_created: true
---

# un-data-model

Turn the design's information needs into a concrete, reviewable data model.

## When to use
- During `un-tech-design`, before any database schema or persistence code is written.

## Workflow
1. Read `.sdlc/design.md` and the acceptance criteria.
2. Identify **entities** and their **attributes**; pick the primary key strategy.
3. Define **relationships** (1:1, 1:N, M:N) and the **cardinality**.
4. Add the **indexes** the access patterns require; flag lifecycle (create/update/archive/delete).
5. Write `.sdlc/data-model.md` from `../../shared/data-model-template.md`.

## Output
`.sdlc/data-model.md` — entities, relationships, keys, indexes, lifecycle, open questions.

## Rules
- Model for the read/write patterns, not just "tables for each noun".
- Keep it technology-agnostic here; the implementation picks SQL/NoSQL later.

## Cross-references
- Feeds implementation (`un-code-implement` / `un-multi-platform-dev`) and `un-task-breakdown`.
