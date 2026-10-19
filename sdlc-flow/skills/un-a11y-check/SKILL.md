---
name: "un-a11y-check"
description: "Accessibility checklist for UI work: WCAG target level, keyboard navigation, color contrast, ARIA usage, and a screen-reader pass; outputs .sdlc/a11y-check.md. Use alongside un-ui-spec or after UI implementation. Part of sdlc-flow."
agent_created: true
---

# un-a11y-check

Make accessibility a checklist item, not an afterthought.

## When to use
- During `un-ui-spec` or after UI implementation, before sign-off.

## Workflow
1. Set the **WCAG target** level (e.g. AA) from requirements.
2. Walk the checklist in `.sdlc/a11y-check.md` (from `../../shared/a11y-template.md`):
   - keyboard operability (no mouse-only paths),
   - color contrast ≥ 4.5:1 (text) / 3:1 (UI),
   - ARIA roles/labels correct, no orphaned controls,
   - a real **screen-reader pass** on key flows.
3. Record failures and the tasks needed to fix them.

## Output
`.sdlc/a11y-check.md` — WCAG level, per-check result, open issues.

## Rules
- Automated checks catch ~30%; the screen-reader pass is the real test.
- Tie open issues back to `un-task-breakdown`.

## Cross-references
- Consumes `un-ui-spec`; complements `un-i18n-plan` (RTL) and `un-verify-before-done`.
