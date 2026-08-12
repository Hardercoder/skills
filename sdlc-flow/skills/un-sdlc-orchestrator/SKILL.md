---
name: un-sdlc-orchestrator
description: "研发全流程编排器：把『需求 PRD → 设计 → 开发 → 测试』整条链路串成一个可执行的 pipeline。接收一句话需求或任意阶段的产物，按阶段路由到对应的子 skill（un-prd-writer / un-requirement-clarify / un-acceptance-criteria / un-user-story-map / un-tech-design / un-api-design / un-ui-spec / un-task-breakdown / un-multi-platform-dev / un-code-implement / un-code-review / un-test-case-gen / un-unit-test-gen / un-e2e-test-gen / un-bug-triage / un-test-report），并在 workspace 的 .sdlc/ 目录维护各阶段产物、自动喂给下一阶段。也支持用户单独调用某个子 skill。多端场景会把设计阶段产出的平台无关契约直接作为 un-multi-platform-dev 的真源。"
agent_created: true
---

# SDLC Orchestrator（研发全流程编排器）

## Overview

总入口 skill，不写业务，只做两件事：

1. **路由** —— 判断当前处于哪个阶段，调用对应子 skill。
2. **串联产物** —— 在 `.sdlc/` 目录维护阶段产物（PRD.md → AC.md → design.md →
   tasks.md → 代码 → test-cases.md → report.md），把上一阶段输出自动喂给下一阶段。

每个子 skill 都可被单独调用（用户直接说「写个 PRD」就走 `un-prd-writer`）；本编排器
在用户给的是一个端到端需求、或希望按流程推进时使用。

## When to use

- 「把这个需求从 PRD 一路做到测试」—— 端到端跑全流程。
- 「继续下一步」「下一步做什么」—— 根据 `.sdlc/` 现有产物推断当前阶段并推进。
- 「只写测试用例」—— 直接路由到 `un-test-case-gen`，不跑全流程。

## Pipeline 与路由

```
需求 → un-prd-writer → un-requirement-clarify → un-acceptance-criteria
     → un-tech-design → un-api-design / un-ui-spec → un-task-breakdown
     → 多端? un-multi-platform-dev : un-code-implement → (un-code-review)
     → un-test-case-gen → un-unit-test-gen / un-e2e-test-gen → un-bug-triage → un-test-report
```

### 阶段判定（读 `.sdlc/`）
- 无 PRD → 从 `un-prd-writer` 起。
- 有 PRD 无 AC → 先 `un-requirement-clarify` 再 `un-acceptance-criteria`。
- 有 PRD+AC 无 design → `un-tech-design`（按需接 `un-api-design`/`un-ui-spec`）→ `un-task-breakdown`。
- 有 design 无代码 → 多端走 `un-multi-platform-dev`，单端走 `un-code-implement`。
- 有代码/AC 无 test-cases → `un-test-case-gen` 起测试链路。

## Workflow

1. **确定入口**：用户给的是一句话需求（从头跑），还是某阶段产物（从中间接）。
2. **定位阶段**：按上面的判定读 `.sdlc/`，或缺省从头。
3. **调用子 skill**：把上一阶段产物作为参数/上下文传给子 skill，要求其按
   `shared/` 下对应模板产出文档，写入 `.sdlc/`。
4. **推进指针**：每完成一个阶段，向用户报告产物路径与「下一步建议」，等待确认或
   自动继续（用户说「继续」才继续，避免越过人工决策点）。
5. **跨端衔接**：进入开发阶段前，若 `design.md` 含「平台无关契约」且目标为多端，
   把该段落作为 `un-multi-platform-dev` 的 contract（字段对齐见 `shared/contract-bridge.md`）。
6. **闭环**：`un-multi-platform-dev` 的 `drift_check.py` 分歧、或 `un-bug-triage` 结论，
   回写对应设计/需求文档。

## 产物目录约定

在 workspace 根建 `.sdlc/`（不存在则创建），各阶段写：
- `PRD.md`（un-prd-writer / un-requirement-clarify 修订）
- `AC.md`（un-acceptance-criteria）
- `design.md`（un-tech-design + un-api-design + un-ui-spec 合并，含平台无关契约）
- `tasks.md`（un-task-breakdown）
- `test-cases.md`（un-test-case-gen）
- `report.md`（un-test-report）

代码落在用户指定的工程目录（由 `un-multi-platform-dev` 或 `un-code-implement` 探测/确认）。

## Rules

- 不替代子 skill 的业务产出——只路由 + 传递上下文 + 管理产物。
- 每个阶段产物落盘后再进入下一阶段；不凭空造数据。
- 涉及人工决策（范围裁剪、平台取舍、发布与否）必须停下来交回用户。
- 多端开发严格走 `un-multi-platform-dev`；其契约红线见 `shared/contract-bridge.md`。

## Resources

- `../plugin.md` —— 插件总说明与 skill 目录。
- `../../shared/` —— prd / ac / design / tasks / testcase / report 模板，及 contract-bridge 对齐约定。
- `../un-multi-platform-dev/` —— 多端开发技能（含 `scripts/drift_check.py`）。
