---
name: un-code-review
description: "对实现代码做评审：给出 diff 说明、风险点（正确性/安全/性能/可维护性）、改进建议与必须修改项，输出评审意见清单。不修改代码本身，只产出可执行的 review 结果。属于 sdlc-flow 插件的开发阶段，接在 un-code-implement / un-multi-platform-dev 之后、测试阶段之前。"
agent_created: true
---

# Code Review（代码评审）

## Overview

在测试前做一次人工视角的评审：不只是「能不能跑」，而是「该不该这么写」。产出结构化评审意见，标出必须改（blocker）与建议改（nit）。

## When to use

- 一个任务/PR 实现完成，进测试前。
- 研发全流程开发阶段收尾，由编排器调用。

## Workflow

1. **读取改动**：diff / 变更文件；同时读 `.sdlc/design.md` 与 `.sdlc/AC.md` 作对照。
2. **四维度检查**：
   - 正确性：边界、并发、空值、异常路径。
   - 安全：注入、越权、敏感信息、依赖风险。
   - 性能：复杂度、N+1、内存。
   - 可维护性：命名、重复、契约一致性。
3. **对照契约**：多端改动检查是否偏离 `un-multi-platform-dev` 契约；偏离需回写。
4. **产出意见**：每条含 位置 / 问题 / 严重度（blocker/suggest） / 建议。
5. **落盘**：评审意见写入 `.sdlc/review.md`（或贴入 PR）。
6. **下一步**：必须改项回到实现；通过后进入 `un-test-case-gen`。

## Rules

- 不自动改代码，只给意见（改代码是对实现的尊重边界）。
- blocker 必须解决才能进测试；suggest 可协商。
- 评审依据设计契约与 AC，不凭个人偏好。

## Resources

- `../../shared/design-template.md` / `ac-template.md` —— 评审对照基准。
- `../un-multi-platform-dev/references/cross-platform-consistency.md` —— 多端一致性检查点。
