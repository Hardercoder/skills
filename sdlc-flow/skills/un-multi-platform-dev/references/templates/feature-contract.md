# Feature Contract: <feature-name>

> Platform-agnostic source of truth. Describe WHAT the feature does — never HOW
> per platform. No `UIViewController`, `Activity`, `Widget`, `useState`, `Page`,
> or platform SDK calls belong in the body below. Platform specifics go only in
> the "Platform Notes" section, filled in during implementation.

## Purpose
<!-- One or two sentences: why this feature exists and who benefits. -->

## Behavior
<!-- User stories. Behavior-first, not implementation-first. -->
- As a <role>, I want <capability> so that <value>.
- ...

## Data Model
<!-- Entities, fields, types, constraints, validation. Use neutral names. -->
| Entity | Field | Type | Constraints |
|--------|-------|------|-------------|
| <Entity> | <field> | <type> | <constraints> |
| ... | ... | ... | ... |

## Interface / API Contract
<!-- Operations, inputs, outputs, error cases — platform-neutral. -->
| Operation | Inputs | Outputs | Errors |
|-----------|--------|---------|--------|
| <op> | <inputs> | <outputs> | <errors> |
| ... | ... | ... | ... |

## UI States
<!-- Screens/states, loading/empty/error states, navigation intent. -->
- <state>: <description> (edge cases: <...>)
- ...

## Edge Cases & Non-Goals
<!-- Explicitly list out-of-scope items to prevent drift across platforms. -->
- Edge cases: ...
- Non-goals: ...

## Acceptance Scenarios (Given/When/Then)
<!-- Every targeted platform MUST satisfy these. -->
- **Scenario: <name>**
  - GIVEN <context>
  - WHEN <action>
  - THEN <expected result>
- ...

## Platform Notes (added during implementation)
<!-- Divergences, library choices, limitations per platform. Filled in as code is written. -->
### iOS
- ...
### Android
- ...
### Flutter
- ...
### React / H5
- ...
### React Native
- ...
### WeChat Mini Program
- ...
### Uni-app
- ...

## 检查点（Checkpoints，供 drift_check.py 使用，可选但强烈推荐）
<!-- 把"这个功能在每端应该长什么样"落成可机器检查的检查点。drift_check.py 会按
     这里的 match.<端名> 正则去各端代码里 grep，产出"功能 × 端"覆盖矩阵，从而发现
     某一端漏做。某端没单独给 match 就退而求其次用 default_match，再不行用 id 本身。
     端名：ios / android / flutter / react_native / react_web / vue_web / h5_web /
     wechat_mp / uniapp。正则里的括号、点等要转义。 -->
```yaml
default_match: "<feature-keyword>"
checkpoints:
  - id: user-login
    desc: 用户登录入口
    match.ios: "LoginManager"
    match.android: "LoginRepository"
    match.flutter: "login"
    match.react_web: "login\\("
  - id: logout
    desc: 退出登录
    match.ios: "LogoutManager"
    match.android: "LogoutRepository"
    match.flutter: "logout"
    match.react_web: "logout\\("
```
<!-- 没有契约时，也可以先跑 drift_check.py 的 symbol 模式从现有代码反向生成这份
     检查点草稿（见 references/drift-check.md）。 -->
