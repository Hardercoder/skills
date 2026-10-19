---
name: "un-tdd-guard"
description: "Enforce test-driven development in the dev phase: RED-GREEN-REFACTOR, write a failing test before any implementation, delete code written without a test, never weaken a test to pass. Use before/while implementing features. Part of sdlc-flow discipline layer."
agent_created: true
---

# un-tdd-guard

Test-driven development **enforcement**. Its job is to stop the agent from writing
implementation code before there is a failing test that specifies the behavior.

## When to use
- Before writing any feature, function, or behavior in the dev phase.
- Whenever the agent is about to write production code without a corresponding test.
- Especially under `un-multi-platform-dev` — apply TDD per platform target.

## Workflow (mandatory cycle)
1. **Pick the smallest behavior** to implement (one assertion worth of behavior).
2. **RED**: write a failing test that specifies that behavior. Run it; confirm it
   fails for the *right reason* (not a typo).
3. **GREEN**: write the *minimal* code that makes the test pass. Run; confirm green.
4. **REFACTOR**: clean up only while tests stay green.
5. If production code already exists without a preceding failing test → **delete it**
   and restart from RED.

## Hard rules
- No production code without a preceding failing test.
- Tests must be real assertions covering edge cases and failure modes — not
  "mirror the implementation" rubber stamps that only cover the happy path.
- Never delete, skip, or weaken a test to make code pass.

## Output
Green test suite + minimal implementation, committed together per behavior.

## Cross-references
- Pairs with `un-unit-test-gen` (generate skeletons) and `un-verify-before-done`
  (the final gate).
- In multi-platform work, run the cycle per platform target.
