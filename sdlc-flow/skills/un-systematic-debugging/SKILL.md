---
name: "un-systematic-debugging"
description: "Systematic 4-phase root-cause debugging instead of print-statement guessing. Use when a bug, test failure, or unexpected behavior appears: reproduce, locate, root-cause, fix-and-verify. Part of sdlc-flow discipline layer."
agent_created: true
---

# un-systematic-debugging

Replace "add some print statements" with a disciplined root-cause process.

## When to use
- Any defect, failing test, or anomalous runtime behavior.
- Pairs with `un-bug-triage` (which assigns severity) — this skill does the fixing.

## Workflow (4 phases)
1. **Reproduce**: get a deterministic, minimal repro. No fix until reproduced.
   Document the exact steps and the observed vs. expected result.
2. **Locate**: narrow the fault domain — git bisect, structured logs, targeted
   instrumentation. Isolate the module/commit where the fault lives.
3. **Root cause**: find the *actual underlying cause*, not the symptom. State it
   in one sentence you can defend.
4. **Fix & verify**: minimal fix addressing the root cause; add a regression test;
   confirm the suite is green.

## Hard rules
- One root cause at a time — resist shotgun fixes that touch unrelated code.
- Prefer *understanding* over *workaround*; record the cause so it doesn't recur.
- The regression test is what proves the fix; without it, the bug is not closed.

## Cross-references
- Complements `un-verify-before-done` (final evidence gate).
- Feeds `un-postmortem` when the defect was a production incident.
