---
name: "un-tech-spike"
description: "Run a time-boxed technical spike to de-risk feasibility before PRD: validate the riskiest assumption (tech choice, integration, performance) with a minimal prototype and a clear go/no-go. Produces .sdlc/tech-spike.md. Precedes un-prd-writer. Part of sdlc-flow."
agent_created: true
---

# un-tech-spike

De-risk the biggest unknown *before* committing it to a PRD.

## When to use
- Before `un-prd-writer` when there is a high-risk unknown: a new technology,
  a tricky integration, a performance/scale assumption, or a "can we even build this" question.

## Workflow
1. State the **single riskiest assumption** to validate (one per spike).
2. Time-box (e.g. 0.5–2 days). Build the *minimal* prototype needed to answer it.
3. Capture result in `.sdlc/tech-spike.md` using `../../shared/tech-spike-template.md`.
4. Conclude with an explicit **go / no-go / go-with-condition**.
5. Hand the spike outcome to `un-prd-writer` so the PRD reflects what is actually feasible.

## Output
`.sdlc/tech-spike.md` — question, approach, evidence, decision, residual risks.

## Rules
- A spike proves or disproves one thing; don't let it become the real implementation.
- Throw away prototype code unless the spike result is "go and reuse".

## Cross-references
- Feeds `un-prd-writer`. In multi-platform work, the spike should cover the riskiest platform target.
