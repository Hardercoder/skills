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

## 真源与溯源（Source of Truth & Provenance）

**核心原则：契约是永久真源，端只是实现。** 不要长期把某个具体端当作"真源"——
那会把"哪个端是真源"变成需要反复横跳的状态。正确做法：用 platform-first 冷启动
（把首个真源端提升成契约）后，让契约接管；之后任何端领先了，都把它的变更 promote
进契约，再让其它端追上契约（见 `workflows.md` 的 Mode C「真源迁移」）。

本契约记录每条功能 / 检查点的溯源，便于漂移检查与真源迁移时回答：
"功能 X 的最新真源是哪个端、各端是否追平了？"

- `version:`（契约顶层）— 契约版本号，每次真源迁移 promote 后 +1。
- 每个 `checkpoint` 可带：
  - `source:` — 当前真源端（最后设定或领先该检查点的一端，如 `flutter`）。
  - `since:` — 该真源设定的日期（YYYY-MM-DD）。
- 各端"已实现到第几版契约"可记在下方 Platform Notes（如 `iOS: v1`、`flutter: v2`）。

> 漂移检查（`drift_check.py`）会读取这里的 `source` / `since`，在覆盖矩阵里标注每条
> 功能的"当前真源端"与"设定日期"，并支持 `--source <端>` 以某端为临时真源对比其它端
> 落后多少（真源迁移 / 追赶视图）。

## 检查点（Checkpoints，供 drift_check.py 使用，可选但强烈推荐）
<!-- 把"这个功能在每端应该长什么样"落成可机器检查的检查点。drift_check.py 会按
     这里的 match.<端名> 正则去各端代码里 grep，产出"功能 × 端"覆盖矩阵，从而发现
     某一端漏做。某端没单独给 match 就退而求其次用 default_match，再不行用 id 本身。
     端名：ios / android / flutter / react_native / react_web / vue_web / h5_web /
     wechat_mp / uniapp。正则里的括号、点等要转义。 -->
```yaml
version: 1                       # 契约版本；真源迁移 promote 后 +1
default_match: "<feature-keyword>"
checkpoints:
  - id: user-login
    desc: 用户登录入口
    source: flutter              # 该检查点当前真源端（最后设定/领先的一端）
    since: 2026-10-19           # 真源设定日期
    match.ios: "LoginManager"
    match.android: "LoginRepository"
    match.flutter: "login"
    match.react_web: "login\\("
  - id: logout
    desc: 退出登录
    source: flutter
    since: 2026-10-19
    match.ios: "LogoutManager"
    match.android: "LogoutRepository"
    match.flutter: "logout"
    match.react_web: "logout\\("
```
<!-- 没有契约时，也可以先跑 drift_check.py 的 symbol 模式从现有代码反向生成这份
     检查点草稿（见 references/drift-check.md）。 -->
