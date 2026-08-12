# OpenSpec as the cross-platform source of truth

OpenSpec is a lightweight, markdown-based, spec-driven development workflow. It
is tool-agnostic (works with any AI coding assistant) and well-suited to
cross-platform work because the "spec" is naturally platform-agnostic.

## Install

Requires Node.js 20.19.0+.

```bash
npm install -g @fission-ai/openspec@latest
```

## Initialize in a project

```bash
cd /path/to/project
openspec init --tools all      # or: --tools claude,cursor,copilot
```

This creates an `openspec/` directory:

```
openspec/
├── specs/          # Source of truth — current system behavior (by domain)
│   └── <domain>/spec.md
├── changes/        # One folder per proposed change
│   └── <change-name>/
│       ├── proposal.md
│       ├── design.md
│       ├── tasks.md
│       └── specs/   # Delta specs (ADDED / MODIFIED / REMOVED)
│           └── <domain>/spec.md
└── config.yaml
```

## Core workflow

```
new → plan → apply → verify → archive
```

| Command | Purpose |
|---------|---------|
| `openspec new change <name>` | Create a change folder |
| `openspec instructions --change <name> --json` | Get enriched prompts for the next artifact |
| `openspec status --change <name> --json` | Artifact completion status |
| `openspec validate [name] --json` | Validate change/spec completeness |
| `openspec archive --yes` | Merge delta specs into `openspec/specs/` |

Use `--json` for programmatic/agent use.

## Using OpenSpec for multi-platform work

- Create **one change per feature**, e.g. `openspec new change add-login`.
- Write platform-agnostic requirements in
  `changes/add-login/specs/<domain>/spec.md` using `## ADDED Requirements`
  (or `MODIFIED`/`REMOVED`) with `#### Scenario:` Given/When/Then blocks and
  RFC 2119 keywords (`MUST`/`SHALL`). Keep the spec free of platform APIs.
- Put platform-specific decisions in `design.md` or a dedicated
  `platform-notes.md`; keep `spec.md` the shared contract.
- For **sync mode**: create a change, write the delta spec from the source
  platform's behavior, then implement each target platform from `tasks.md`.
- After implementation and verification, `openspec archive --yes` consolidates
  the delta into `openspec/specs/` — the permanent cross-platform source of
  truth that future changes build on.

## Pros / cons for this skill

- **Pros**: minimal setup, markdown-only, change isolation (parallel changes
  don't collide), works in brownfield codebases, tool-agnostic.
- **Cons**: no built-in "constitution"; cross-platform principles must be
  agreed verbally or written into `design.md`/`config.yaml` and enforced by the
  agent.
