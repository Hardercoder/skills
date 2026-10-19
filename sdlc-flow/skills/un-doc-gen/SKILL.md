---
name: "un-doc-gen"
description: "Generate project or user documentation after dev: README, API docs, runbook, or user guide, derived from the implemented code and design. Outputs docs under .sdlc/docs/ or the repo docs folder. Part of sdlc-flow."
agent_created: true
---

# un-doc-gen

Turn finished code + design into the docs a reader actually needs.

## When to use
- After the dev phase (and ideally after `un-verify-before-done`), when docs are due:
  onboarding README, API reference, operational runbook, or an end-user guide.

## Workflow
1. Decide the **doc type** needed (README / API / runbook / user guide).
2. Pull facts from the code and `.sdlc/design.md` — do not invent behavior.
3. Write from `../../shared/doc-template.md` into `.sdlc/docs/<type>.md`
   (or the repo's `docs/` if the project has one).
4. Include a quickstart that a new reader can follow verbatim.

## Output
One or more doc files; for README also suggest repo-root placement.

## Rules
- Docs describe actual behavior; if code and doc disagree, flag it, don't paper over.
- Keep the quickstart copy-paste runnable.

## Cross-references
- Consumes `un-tech-design` and the implementation; a good input to `un-release-checklist`.
