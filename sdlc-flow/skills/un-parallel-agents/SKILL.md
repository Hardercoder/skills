---
name: "un-parallel-agents"
description: "Dispatch independent tasks to fresh sub-agents in parallel, each with only its task spec and relevant code context (no shared state or sequence dependency). Use when 2+ tasks can be done independently. Part of sdlc-flow discipline layer."
agent_created: true
---

# un-parallel-agents

Run independent tasks concurrently via fresh sub-agents to reduce drift and wall-clock time.

## When to use
- Multiple independent tasks produced by `un-task-breakdown` with no ordering
  dependency and no shared mutable state.

## Workflow
1. **Confirm independence**: no shared mutable state, no sequence dependency
   between the tasks. If there is, serialize them instead.
2. For each task: spin a fresh sub-agent with (a) the task spec and (b) only the
   relevant files it needs — not the whole repo history.
3. Collect results; run `un-verify-before-done` on each before integrating.
4. Integrate with `un-git-worktree` isolation.

## Trade-offs
- Each sub-agent rebuilds minimal context → higher token cost, but far lower drift
  than one long session.
- Don't parallelize tasks that share state; the coordination overhead isn't worth it.

## Cross-references
- Depends on `un-task-breakdown` (for the task list) and `un-git-worktree` (isolation).
- Each sub-agent should still follow `un-tdd-guard` and `un-verify-before-done`.
