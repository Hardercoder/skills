---
name: un-tech-design
description: "根据 PRD 与验收标准产出技术方案：架构概览、模块划分、数据流、关键决策与权衡、风险，并在文档末尾写出『平台无关契约』（行为/数据模型/边界与异常/验收场景/检查点）。该契约段直接作为 un-multi-platform-dev 的真源，字段对齐 shared/contract-bridge.md。属于 sdlc-flow 插件的设计阶段，接在 un-acceptance-criteria 之后。"
agent_created: true
---

# Tech Design（技术方案设计）

## Overview

把需求翻译成可实现的技术方案。重点是**架构与模块边界**，并把「平台无关契约」作为文档核心产出——这一段不绑定任何端，下游 `un-multi-platform-dev`（多端）或 `un-code-implement`（单端）直接消费。

## When to use

- PRD+AC 就绪，要进入实现前的设计。
- 研发全流程设计阶段第一步，由 `un-sdlc-orchestrator` 调用。
- 需要决定模块边界、技术选型、风险。

## Workflow

1. **读取前置**：读 `.sdlc/PRD.md` 与 `.sdlc/AC.md`。
2. **架构概览**：分层、关键组件、用文字/Mermaid 表达（不涉及具体端实现）。
3. **模块划分**：职责、边界、依赖。
4. **数据流**：主流程数据走向。
5. **关键决策**：选型理由、取舍、备选。
6. **写平台无关契约**（关键，参考 `../../shared/design-template.md` 末尾段）：
   - 行为 Behavior / 数据模型 / 边界与异常 / 验收场景（关联 AC）/ 检查点（供 drift_check）。
   - 不得出现 `UIViewController`/`Activity`/`Widget`/`useState`/`Page` 等平台专属符号。
7. **落盘**：写入 `.sdlc/design.md`。
8. **按需分支**：接口复杂交给 `un-api-design`；有界面交给 `un-ui-spec`；最后 `un-task-breakdown`。

## Rules

- 契约正文平台无关；平台差异只在各端实现或 Platform Notes 体现。
- 决策要写理由，不只是结论。
- 不实现代码，只设计；明确哪些留给开发阶段。

## Resources

- `../../shared/design-template.md` —— 含平台无关契约段落模板。
- `../../shared/contract-bridge.md` —— 契约字段与 un-multi-platform-dev 的对齐约定。
- `../un-multi-platform-dev/references/templates/feature-contract.md` —— 真源契约模板。
