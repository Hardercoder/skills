---
name: "un-cicd"
description: "Set up or revise the CI/CD pipeline: build, test, lint, and deploy stages, branch strategy, secrets handling, and quality gates; outputs a pipeline config snippet plus .sdlc/cicd.md. Use when the project lacks or needs to revise CI/CD. Part of sdlc-flow."
agent_created: true
---

# un-cicd

Make "it builds on my machine" a non-event by automating the path to production.

## When to use
- When the project has no CI/CD, or the existing pipeline needs revision
  (new test stage, deploy target, gate, etc.).

## Workflow
1. Pick the **branch strategy** (trunk-based, git-flow, etc.) and the trigger events.
2. Define **stages** in order: install → lint → build → test (unit + the e2e from
   `un-e2e-test-gen`) → (optional) deploy.
3. Wire **quality gates**: a red build/test fails the pipeline; no manual override.
4. Handle **secrets** via the CI provider's secret store — never commit them.
5. Emit `.sdlc/cicd.md` describing the pipeline + the actual config snippet
   (GitHub Actions / GitLab CI / etc.).

## Output
`.sdlc/cicd.md` + a ready-to-commit pipeline config file.

## Rules
- The pipeline must run the same tests `un-verify-before-done` relies on.
- Deploy stage should be separable (deploy only after manual approval or tag).

## Cross-references
- Consumes `un-test-case-gen` / `un-e2e-test-gen` / `un-unit-test-gen`;
  pairs with `un-release-checklist`.
