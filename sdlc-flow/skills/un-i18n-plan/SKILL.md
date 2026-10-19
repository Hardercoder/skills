---
name: "un-i18n-plan"
description: "Internationalization plan: scope locales, externalize strings, handle pluralization, date/number/currency formatting, and RTL if needed; outputs .sdlc/i18n-plan.md. Use when the product targets multiple languages. Part of sdlc-flow."
agent_created: true
---

# un-i18n-plan

Plan i18n before strings get hardcoded across the codebase.

## When to use
- During `un-tech-design` / `un-ui-spec` when the product will ship in more than one language.

## Workflow
1. Define the **locale scope** (which languages/regions, and priority).
2. Mandate **string externalization** — no user-facing text in code/markup.
3. Call out **pluralization**, **date/number/currency formatting**, and **RTL** needs.
4. Specify the i18n mechanism per platform (aligns with `un-multi-platform-dev` tokens).
5. Write `.sdlc/i18n-plan.md` from `../../shared/i18n-template.md`.

## Output
`.sdlc/i18n-plan.md` — locales, externalization rules, formatting, RTL, tooling.

## Rules
- Decide locale scope early; retrofitting i18n is costly.
- Treat pseudo-localization as a test step.

## Cross-references
- Consumes `un-ui-spec` design tokens; feeds `un-task-breakdown` and `un-a11y-check`.
