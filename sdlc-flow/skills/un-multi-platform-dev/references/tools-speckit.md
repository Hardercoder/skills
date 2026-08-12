# SpecKit as the cross-platform source of truth

SpecKit (GitHub's `spec-kit`) is an AI-native, spec-driven development toolkit.
Its CLI is `specify`. It pairs a project "constitution" with per-feature specs,
which makes it a strong fit for enforcing cross-platform principles.

## Install

Requires Python 3.11+ and the `uv` package manager.

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
# Add the installed binary to PATH, e.g. $HOME/.local/bin on macOS/Linux
specify --version
```

> ⚠️ The `specify-cli` package on PyPI is **not** official. Install only from the
> GitHub repo URL above.

## Initialize a project

```bash
specify init my-project --ai claude      # or: --ai copilot | cursor | gemini
cd my-project
```

This creates:

```
.specify/
├── memory/constitution.md   # Project-wide principles (single source of truth)
└── templates/
specs/
└── 001-feature-name/
    ├── spec.md              # WHAT — platform-agnostic
    ├── plan.md              # HOW — technical plan (can be per-platform)
    ├── tasks.md             # Implementation tasks
    ├── data-model.md
    ├── contracts/           # API contracts
    └── checklists/
CLAUDE.md
```

## Slash-command workflow

| Command | Purpose |
|---------|---------|
| `/speckit.constitution` | Define project principles (run first) |
| `/speckit.specify` | Write the natural-language feature spec (WHAT/WHY) |
| `/speckit.clarify` | Resolve ambiguity via structured questions |
| `/speckit.plan` | Technical plan + architecture decisions |
| `/speckit.tasks` | Break the plan into atomic tasks |
| `/speckit.analyze` | Cross-artifact consistency & coverage check |
| `/speckit.implement` | Execute tasks, generate code |
| `/speckit.checklist` | Auto-generate quality checklists |

## Using SpecKit for multi-platform work

- Put cross-platform principles in `constitution.md`, e.g. "specs are the single
  source of truth; no platform API belongs in `spec.md`", "every platform must
  satisfy the same acceptance scenarios".
- Author the feature in `specs/<NNN>/spec.md` as platform-agnostic WHAT.
- Fork `plan.md` per platform (platform-specific HOW) while keeping `spec.md`
  shared — this naturally separates the contract from implementation.
- For **sync mode**: run `/speckit.specify` from the source platform's behavior,
  then `/speckit.plan` + `/speckit.tasks` per target platform.
- Update the top-level spec when requirements change; downstream plans/tasks
  propagate the change.

## Pros / cons for this skill

- **Pros**: explicit `constitution.md` enforces cross-platform rules; end-to-end
  traceability (constitution → spec → plan → tasks → code); GitHub-backed,
  slash-command driven, good DX with Copilot/Claude.
- **Cons**: requires `uv` + Python 3.11+; younger plugin ecosystem; more
  structure to maintain than OpenSpec.
