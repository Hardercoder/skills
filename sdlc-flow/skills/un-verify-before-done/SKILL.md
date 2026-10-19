---
name: "un-verify-before-done"
description: "Verification gate before declaring any task complete: evidence-based confirmation the change actually works (tests pass, behavior reproduced, acceptance criteria met), not a claim. Use at the end of every dev/test task. Part of sdlc-flow discipline layer."
agent_created: true
---

# un-verify-before-done

A mandatory gate that runs before anything is marked done or reported complete.

## When to use
- Right before marking a task / feature / bugfix done.
- Before reporting completion to the user or to `un-sdlc-orchestrator`.

## Workflow
1. Re-state the acceptance criteria / definition of done for the task.
2. Produce **evidence** — one of:
   - a passing test run (real output, not "I wrote tests"),
   - a manual repro with observed result,
   - a metric / screenshot / log line proving the behavior.
3. Confirm edge cases are covered, not just the happy path.
4. If there is no evidence → the task is **NOT done**; go back and produce it.

## Hard rule
- "It should work" / "I'm confident" is **not** evidence. Show it.

## Output
A short verification note (what was checked, how, result) appended to the task.

## Cross-references
- Closes the loop started by `un-tdd-guard`.
- Feeds the summary in `un-test-report`.
