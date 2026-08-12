---
name: un-ui-spec
description: "把界面需求落成 UI/交互规范：页面与组件清单、各页面状态（空/加载/错误/成功）、关键交互流程、以及设计令牌（颜色/间距/字号/圆角）作为多端样式真源。设计令牌可被 Style Dictionary 等工具生成各端样式，配合 un-multi-platform-dev 保证多端视觉一致。UI 设计稿通常来自 MasterGo 或 Figma，若用户提供链接或导出（设计令牌/标注/组件树），优先从中提取规范再补全。属于 sdlc-flow 插件的设计阶段，接在 un-tech-design 之后。"
agent_created: true
---

# UI Spec（界面规范设计）

## Overview

把「长什么样、怎么交互」变成**可跨端复用的规范**。核心是设计令牌（design tokens）——它和接口契约一样，是 `un-multi-platform-dev` 用来保证多端视觉一致的真源（Style Dictionary 生成各端样式，Chromatic/Percy 做可视化回归）。

## When to use

- 需求包含界面/交互。
- 多端产品需要统一视觉与状态。
- 研发全流程设计阶段的可选增强。

## UI 设计稿来源（MasterGo / Figma）

界面规范通常基于设计工具产出，而非凭空设计：

- **MasterGo / Figma**：若用户提供链接或导出（设计令牌、标注、组件树、页面截图），优先从中提取页面清单、各页面状态、间距字号、颜色与动效时长，落为设计令牌。
- 导出的 token（如 Figma Variables / MasterGo 令牌）直接作为 `.sdlc/` 下的 `tokens.json`，供 `un-multi-platform-dev` 用 Style Dictionary 生成各端样式。
- 设计稿未覆盖的交互/异常态，再据需求补全，不要臆造视觉。

## Workflow

1. **读取来源**：优先用「UI 设计稿来源」里的 MasterGo/Figma 导出；同时读 `.sdlc/design.md` 的「行为 / UI 状态」相关段落。
2. **页面与组件**：清单 + 每个页面的状态（empty/loading/error/success）。
3. **交互流程**：关键路径的步骤与反馈。
4. **设计令牌**：颜色、间距、字号、圆角、阴影、动效时长，用 token 名而非裸值。
5. **落盘**：作为 `.sdlc/design.md` 的「UI 状态」段落，令牌单独 `tokens.json`/字典。
6. **衔接多端**：提示 `un-multi-platform-dev` 会用令牌生成各端样式。

## Rules

- 用 token 名（如 `color-primary`），不写死十六进制在各端实现里。
- 状态齐全：每个页面至少覆盖空/加载/错误/成功。
- 不写平台专属布局代码，只描述规范。

## Resources

- `../../shared/design-template.md` —— UI 状态段落位置。
- `../un-multi-platform-dev/references/cross-platform-consistency.md` —— 设计令牌与可视化回归手段。
