---
name: un-code-implement
description: "单端或单模块的代码实现（非多端场景）。依据 tasks.md 与 design.md 的平台无关契约，在一个指定工程里落地功能，保证每个任务可对应 AC 验收。多端场景请用 un-multi-platform-dev 而非本 skill。属于 sdlc-flow 插件的开发阶段，接在 un-task-breakdown 之后。"
agent_created: true
---

# Code Implement（单端代码实现）

## Overview

当目标是单一端（或纯后端/脚本）时，本 skill 按任务清单把设计落成代码。多端协同请用 `un-multi-platform-dev`——它才处理跨端一致性与契约真源。

## When to use

- 目标只有一端，无需多端协调。
- 按 `tasks.md` 逐任务实现并验证。
- 研发全流程开发阶段（单端分支），由编排器调用。

## Workflow

1. **读取上下文**：读 `.sdlc/tasks.md`、`.sdlc/design.md`、`.sdlc/AC.md`。
2. **确认工程**：定位/确认目标工程目录（用 `un-multi-platform-dev` 的 `scripts/detect_platforms.py` 思路探测，或直接按用户指定）。
3. **逐任务实现**：按依赖顺序落地，每完成一个任务跑该端构建/测试。
4. **对照 AC**：实现过程中核对对应 AC，记录未覆盖项。
5. **落盘与报告**：代码写入工程；向用户报告完成度、构建/测试结果、遗留项。
6. **下一步**：跑 `un-code-review`；之后进入测试阶段 `un-test-case-gen`。

## Rules

- 严格按 design.md 的契约实现，不擅自改需求范围。
- 偏离设计必须显式说明并回写 design.md。
- 单端内保证可构建、关键路径可运行。

## Resources

- `../../shared/tasks-template.md` / `design-template.md` / `ac-template.md` —— 输入源。
- `../un-multi-platform-dev/` —— 多端场景改用此技能。
