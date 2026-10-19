---
name: un-multi-platform-dev
description: "面向 iOS、Android、Flutter、React、React Native、H5/Web、微信小程序、Uni-app 等多端客户端的单 query 协同开发编排技能。当用户希望一次把某个功能在多个端同时落地（多端同时开发 / 跨端开发），或把某一端已有的功能同步、移植到其他端（从一端同步功能到多端 / 跨端功能移植 / 一端实现多端复用），又或为跨端代码建立统一的真源（单一事实来源）时使用。会先探测工作区已有工程来确定目标端，或按用户指定；支持“先写平台无关契约”与“指定某一端为真源”两种真源模式；并引导采用规范驱动、契约测试、设计令牌、单源码多端生成、可视化回归等多种手段保证多端一致，以及用确定性检查与 AI 辅助对账来处理规范滞后的问题。OpenSpec、SpecKit 仅是可选工具中的两个例子。"
agent_created: true
---

# Multi-Platform Development Orchestrator (多端开发编排)

## Overview

Orchestrate feature development across multiple client platforms (iOS, Android,
Flutter, React, React Native, H5/Web, WeChat Mini Program, Uni-app) from a
single instruction. The skill supports two working modes:

- **Simultaneous (多端同步开发)** — implement one feature across all target
  platforms at once.
- **Sync / port (从一端同步到多端)** — port an existing feature from one
  platform (the source of truth) to the other platforms.

Both modes flow through a **platform-agnostic feature contract** that acts as
the single source of truth (真源). The skill can also bootstrap spec-driven
tooling (OpenSpec, SpecKit) so cross-platform changes stay reviewable and
aligned.

## When to use

- "把这个登录功能在 iOS、Android、Flutter、H5 都做一遍" — one feature, many platforms.
- "把 Flutter 里的分享模块同步到 iOS 和 Android" — port from a source platform.
- Setting up or using a shared source of truth for cross-platform code.
- Triggers: 多端开发, 跨端, 同步功能到多端, 一端实现多端复用, 跨平台移植,
  multi-platform, multi-end, sync feature across platforms, cross-platform port.

## Core model: the feature contract as 真源

Every cross-platform change is expressed through a **platform-agnostic feature
contract** (the spec). The contract describes WHAT the feature does — behavior,
data model, interface/API contract, UI states, edge cases, acceptance scenarios
— in language independent of any platform SDK. Platform specifics live only in
per-platform implementation notes.

Establish the 真源 in one of two ways:

1. **Spec-first (推荐)** — author the contract directly from the requirement,
   then implement each platform from it. The contract is the source of truth.
2. **Platform-first** — the user designates one existing platform as 真源 (e.g.
   "Flutter 是真源"). Read that implementation, lift it into a platform-agnostic
   contract, then implement the other platforms from the contract.

**契约是永久真源，端只是实现。** Platform-first 只应作为冷启动：把首个真源端提升成
契约后，就让契约接管，不要再长期把某个具体端当作真源（那会导致"哪个端是真源"反复横跳）。
之后任何端领先了，都把它的变更 promote 进契约、再让其它端追上（见下面 Mode C）。

Always confirm the 真源 before writing code on more than one platform.

## 保证多端一致的多种方式（不止 OpenSpec / SpecKit）

OpenSpec / SpecKit 只是"规范驱动"这一类手段里的两个轻量候选，并非唯一答案。
保证多端一致应按工程现状分层选型（完整字典见
`references/cross-platform-consistency.md`）：

- **源头消除（首选）**：能用单代码库就优先用——Flutter、React Native(+Expo)、
  Taro、uni-app 从结构上一处写、多处出，不可能漂移；接口/类型用 OpenAPI /
  GraphQL / Protobuf 代码生成，设计令牌用 Style Dictionary 等生成多端样式。
- **共享契约**：多独立代码库时，把"契约"作为真源——设计令牌（视觉）、
  API Schema（接口）、组件目录（Storybook）、共享动效（Rive/Lottie）。
- **验证兜底**：用契约测试（Pact / Specmatic / oasdiff / Spectral）与可视化回归
  （Chromatic / Percy）在 CI 持续发现分歧，测试不会像文档那样滞后。
- **规范滞后治理**：SpecGov、drift 这类确定性检查 + AI 辅助对账，见下节。

默认推荐顺序：**先看能否单源码 → 否则建平台无关契约为真源 → 再用契约测试 /
可视化回归兜底 → 最后用确定性检查 + AI 对账治理规范滞后。**

## Spec 滞后与正确性（Drift）

规范不可能永远与代码同步，关键是让滞后可被发现、可修复：

- **设计优先**：规范先于实现更新，避免代码跑在规范前面。
- **确定性检查（CI 门禁，不依赖 LLM）**：SpecGov（代码改动绕过规范即告警，
  advisory→strict）、drift（Fiberplane，把规范锚定到具体代码符号，绑定代码变更
  即标过期）、oasdiff / Spectral / Pact / 可视化回归分别从接口、规范、契约、视觉
  维度抓漂移。本技能还自带一个零依赖的 `scripts/drift_check.py`（见
  `references/drift-check.md`）：用契约里的"检查点"去各端代码 grep，产出覆盖矩阵，
  可直接挂 CI 当门禁。
- **活规范 + 反向同步**：规范随代码同提交更新；OpenSpec archive 让规范随变更沉淀；
  当代码领先于规范时，**从代码重新提炼契约并回写**。
- **AI 辅助对账（本技能的内建能力）**：sync 模式的"提升为契约"本质是一次对账。
  周期性地**从各端代码重新提炼契约并与已写规范 diff**，把差异交给人决定——更新
  规范，还是回退代码。规范是否更新永远是人的决定，工具只暴露差异。

## Target platform resolution

Resolve the target platforms before doing anything else:

1. If the user explicitly names platforms, use that set (validate each is
   supported — see `references/platform-detection.md`).
2. Otherwise, scan the workspace with `scripts/detect_platforms.py` to discover
   existing projects, then confirm the set with the user (they may want a
   subset).
3. If nothing is present and nothing is named, ask the user which platforms to
   target and where each project lives.

Run the detector from the workspace root:

```bash
python3 scripts/detect_platforms.py WORKSPACE_PATH [--json]
```

See `references/platform-detection.md` for marker details and conflict
resolution (e.g. React Native vs React Web vs Vue, monorepos with several
platforms).

## Workflow

1. **Resolve targets** — explicit list, or detector output + user confirmation.
2. **Resolve 真源** — spec-first or a designated source platform.
3. **Pick mode** — simultaneous vs sync (below).
4. **Consistency-tooling check** — with the user, pick the right lever for this
   change (full decision dictionary in `references/cross-platform-consistency.md`):
   - If a single-codebase path exists (Flutter / RN+Expo / Taro / uni-app), prefer
     it — divergence is structurally impossible.
   - Otherwise, if no spec tool is present and the work spans ≥2 platforms, offer
     to install a spec-driven tool. OpenSpec (`references/tools-openspec.md`) and
     SpecKit (`references/tools-speckit.md`) are the two lightest candidates;
     also consider Amazon Kiro, Tessl, or BMAD-METHOD. Never install without
     explicit confirmation.
   - For API consistency, propose OpenAPI/GraphQL + oasdiff/Spectral/Pact; for
     visual consistency, propose design tokens (Style Dictionary) + visual
     regression (Chromatic/Percy). For governance of spec lag, propose SpecGov /
     drift. Also consider relevant WorkBuddy skills via `find-skills`.
5. **Author or lift the contract** — use
   `references/templates/feature-contract.md`.
6. **Implement per platform** — follow `references/workflows.md` for
   platform-specific guidance and verification.
7. **Reconcile & report** — produce a sync report
   (`references/templates/sync-report.md`) summarizing what was implemented
   where, divergences, and open items.
8. **Drift check (on-demand / scheduled / CI)** — after code exists on ≥2
   platforms, run `scripts/drift_check.py` to surface divergence (see
   `references/drift-check.md`):
   - `checkpoint` mode: requires a contract with a `## 检查点` block; greps each
     platform for the expected symbols and emits a feature×platform coverage
     matrix. This is the deterministic, CI-friendly gate.
   - `symbol` mode: code-only; compares tokens across comparable platforms
     (default `--axis routes`; also `api` / `model` / `i18n` for endpoint /
     data-model / i18n-key parity across **all** platforms) and emits a
     suggested-checkpoints YAML you can paste back into the contract
     (reverse-sync when code leads).
   - `--source <platform>` (symbol mode): treat a designated platform as the
     temporary truth and report how far every other platform lags it — the
     source-of-truth migration / catch-up view (use with Mode C).
   - The contract may record each checkpoint's `source` / `since` (see
     `feature-contract.md` 的"真源与溯源"); the checkpoint report then shows a
     "真源与溯源" table (current truth platform + date + contract `version`),
     which is the at-a-glance answer to "where is the latest truth for every
     feature".
   Example: `python3 scripts/drift_check.py --platform ios:IOS_PATH
   --platform flutter:FLUTTER_PATH --contract contract.md --report drift.md`
   The drift report is the trigger for the AI reconciliation step below — it
   exposes differences; updating the spec or reverting code is always a human
   decision.

### Mode A — Simultaneous development (多端同步开发)

- One contract, N platform implementations generated in parallel.
- Implement each platform independently from the same contract to avoid drift.
- After each platform, re-check against the contract and append platform notes
  so later platforms benefit from earlier discoveries.

### Mode B — Sync / port from a source platform (从一端同步到多端)

- Read the source platform's feature implementation; extract behavior, data
  model, and edge cases.
- Lift it into the platform-agnostic contract (this is where platform-specific
  quirks get normalized into shared behavior).
- Implement each target platform from the contract. Where a target platform
  cannot match behavior exactly, record the divergence in the contract's
  Platform Notes and in the sync report — do not silently alter the 真源.
- The source platform remains the reference. If a target diverges by design,
  update the contract and (optionally) reflect the change back into the source.

### Mode C — 真源迁移 / Re-baseline（source-of-truth migration）

When a platform (call it B) later leads the contract and becomes the de-facto new
真源, promote B's领先 parts into the contract and bring the other platforms (A/C/D)
up to date, restoring "the contract is the latest 真源 for every feature". Detailed
steps in `references/workflows.md` → Mode C. This is the standard close-out for
"一开始 A 是真源、后来 B 是真源": never keep flip-flopping which platform is truth —
promote the leader's changes into the contract, then catch everyone else up.

## Rules

- Never generate multi-platform code before targets and 真源 are confirmed.
- The contract MUST stay platform-agnostic: no `UIViewController`, `Activity`,
  `Widget`, `useState`, `Page` etc. inside the contract body. Platform specifics
  belong in platform notes / implementation only.
- Prefer spec tooling for any cross-platform work touching 2+ platforms; it
  yields reviewable, archivable history and reduces drift.
- Track progress and verify each platform builds/runs where feasible; record
  results in the sync report.
- For large features, split into multiple contracts/changes rather than one
  giant change.

## Resources

- `scripts/detect_platforms.py` — discover platforms present in a workspace.
- `scripts/drift_check.py` — deterministic cross-platform drift checker (needs
  a contract with checkpoints, or works code-only); see
  `references/drift-check.md`.
- `references/platform-detection.md` — detection markers and conflict rules.
- `references/workflows.md` — detailed per-mode steps + per-platform
  implementation and verification tips.
- `references/cross-platform-consistency.md` — decision dictionary of all
  consistency levers (single-source, tokens, contract tests, visual regression,
  drift governance) and how to handle spec lag.
- `references/drift-check.md` — the deterministic drift-check workflow: both
  modes, how to run the script, CI integration, and the AI-reconciliation bridge.
- `references/tools-openspec.md` — OpenSpec install/usage as cross-platform 真源.
- `references/tools-speckit.md` — SpecKit install/usage as cross-platform 真源.
- `references/templates/feature-contract.md` — the platform-agnostic contract
  template.
- `references/templates/sync-report.md` — post-run sync report template.
