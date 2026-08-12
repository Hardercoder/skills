---
name: un-user-story-map
description: "针对较大的需求，把 PRD 组织成用户故事地图：拆史诗与故事、排优先级、识别 MVP 切片与发布路线。帮助在动手前对齐范围与交付节奏。属于 sdlc-flow 插件的需求阶段，可选，通常接在 un-acceptance-criteria 之后、un-tech-design 之前。"
agent_created: true
---

# User Story Map（用户故事地图）

## Overview

大需求直接进设计容易失控。本 skill 用故事地图把需求分层：**骨干活动 → 用户故事 → 优先级切片**，让团队先就「先交付哪一块」达成共识，再进设计。

## When to use

- 需求规模大、涉及多角色多流程。
- 需要决定 MVP 范围或分批发布节奏。
- 研发全流程中需求阶段的可选增强，由编排器按需调用。

## Workflow

1. **读取 PRD**：读 `.sdlc/PRD.md` 与 `.sdlc/AC.md`。
2. **抽骨干活动**：用户完成目标的主干步骤（横向）。
3. **铺用户故事**：每个活动下的故事（纵向，按优先级/细化度）。
4. **切 MVP 与发布线**：划出第一版可交付的切片、后续增量。
5. **产出地图**：以表格/文本层级呈现（活动 → 故事 → 优先级 → 所属切片）。
6. **落盘**：作为 `.sdlc/PRD.md` 的附录或独立 `story-map.md`。
7. **下一步**：把 MVP 切片交给 `un-tech-design` 起设计。

## Rules

- 不新增功能，只重组与排序已有需求。
- MVP 切片必须端到端可验证（能对应一组 AC）。
- 优先级标注依据业务价值与依赖，不臆测。

## Resources

- `../../shared/prd-template.md` —— 需求源。
- `../plugin.md` —— 全流程与路由说明。
