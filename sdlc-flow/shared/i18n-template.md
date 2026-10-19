# i18n Plan — <product>

- **Date**: YYYY-MM-DD
- **Owner**: <name>

## 1. Locale scope
| Locale | Priority | RTL? |
|---|---|---|
| en | P0 | no |
| zh-CN | P0 | no |
| ar | P2 | **yes** |

## 2. String externalization
- Rule: no user-facing text in code/markup. Source of truth: <i18n file / CMS>.
- Pluralization: <CLDR rules / library>.

## 3. Formatting
- Date / number / currency: use locale-aware formatting (no manual concat).
- Pseudo-localization: <enabled in CI? yes/no>.

## 4. RTL (if applicable)
- Layout mirroring strategy; test with Arabic/Hebrew.

## 5. Tooling
- <extraction tool> · <platform i18n mechanism>
