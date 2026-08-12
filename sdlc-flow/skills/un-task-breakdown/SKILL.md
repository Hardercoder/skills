---
name: un-task-breakdown
description: "把技术方案拆成可执行的开发任务（WBS）：任务清单、所属模块、估算、依赖关系、状态，并映射到验收标准 AC。为开发阶段（un-multi-platform-dev / un-code-implement）提供明确的执行单元。属于 sdlc-flow 插件的设计阶段收尾，接在 un-tech-design / un-api-design / un-ui-spec 之后。"
agent_created: true
---

# Task Breakdown（任务拆解）

## Overview

设计落定后，把工作拆成**带依赖、可估时、可追溯 AC** 的任务清单。开发阶段直接照此推进，多端场景还能据此在 `un-multi-platform-dev` 里拆成多个契约/变更。

## When to use

- 设计完成，要进入开发前的任务规划。
- 研发全流程设计阶段最后一步，由编排器调用。
- 需要排期、分派、识别关键路径。

## Workflow

1. **读取设计**：读 `.sdlc/design.md`（重点「平台无关契约」与模块划分）。
2. **拆任务**：每个模块/契约段 → 1+ 任务，写 ID、描述、模块、估算（S/M/L）、依赖、状态。
3. **映射 AC**：每个任务关联对应 AC 编号，保证覆盖。
4. **标依赖**：画出 T-a → T-b 关系，识别关键路径。
5. **落盘**：写入 `.sdlc/tasks.md`（参考 `../../shared/tasks-template.md`）。
6. **下一步**：多端 → `un-multi-platform-dev`；单端 → `un-code-implement`。

## Rules

- 任务粒度以「一次可完成并可验证」为准，避免过大。
- 每个任务必须能对应到 AC（可验收）。
- 依赖要显式，避免隐式顺序假设。

## Resources

- `../../shared/tasks-template.md` —— 任务清单模板。
- `../../shared/testcase-template.md` —— 下游测试用例的对应形态。
