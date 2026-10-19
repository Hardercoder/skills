# Release Checklist — <version>

- **Date**: YYYY-MM-DD
- **Owner**: <name>
- **Target env**: <staging / prod>

## Go / No-go items (all must be ✅)
| # | Item | Status | Notes |
|---|---|---|---|
| 1 | Version bump + changelog | ✅/❌ | |
| 2 | DB / data migrations written | ✅/❌ | |
| 3 | Migration **rollback** script exists | ✅/❌ | |
| 4 | Env vars & secrets present in target | ✅/❌ | |
| 5 | Rollback plan documented | ✅/❌ | <steps> |
| 6 | Health checks & alerts armed | ✅/❌ | |
| 7 | Tests green in CI (incl. e2e) | ✅/❌ | |
| 8 | Docs updated (README / runbook) | ✅/❌ | |

## Rollback plan
- Steps to undo this release: <1> <2> <3>

## Blockers
- <item> → <owner>
