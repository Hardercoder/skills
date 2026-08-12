---
name: un-prd-writer
description: "从一句话需求、想法、会议纪要或粗糙描述生成结构化 PRD。覆盖背景目标、范围边界、用户与角色、用户故事、功能需求、非功能需求、里程碑与验收概览、风险与开放问题。产出平台无关、可直接交给 un-requirement-clarify 与后续设计阶段的结构化文档，写入 .sdlc/PRD.md。PRD 来源也支持飞书文档、腾讯文档等在线文档——若用户给出文档链接或粘贴内容，先读取再整理。属于 sdlc-flow 插件的需求阶段。"
agent_created: true
---

# PRD Writer（需求文档生成）

## Overview

把零散的需求输入（一句话、想法、会议记录、客户原话）整理成一份**结构化、可评审、平台无关**的 PRD。目标是让下游设计/开发拿到一份边界清晰、成功标准可量化的文档。

## When to use

- 「帮我把这个想法写成 PRD」
- 「整理一下这次的需求文档」
- 研发全流程进入需求阶段、尚无 PRD 时（由 `un-sdlc-orchestrator` 调用）

## PRD 来源（飞书 / 腾讯文档等在线文档）

PRD 很少从零写起，常来自协作文档：

- **飞书文档 / 腾讯文档**：若用户给出链接或粘贴内容，先读取原文再整理。腾讯文档可用 `tencent-docs` 能力读取；飞书文档同理（粘贴正文或导出 Markdown）。
- **会议纪要 / 客户原话**：直接作为原始输入。
- 读取后归并到 `../../shared/prd-template.md` 结构；文档里缺失的章节标注为待澄清，交给 `un-requirement-clarify`。

## Workflow

1. **收集输入**：先判断是否来自在线文档（见「PRD 来源」）——若是，读取链接/粘贴内容作为原始需求；信息不足时先列 2-3 个最关键缺口（不要卡住，先出草稿）。
2. **套模板**：按 `../../shared/prd-template.md` 组织章节。
3. **写清范围**：In scope / Out of scope 必须明确，避免范围蔓延。
4. **量化成功标准**：能测的指标写进「背景与目标」。
5. **功能需求编号**：FR-1/FR-2…，标优先级 P0/P1/P2。
6. **落盘**：写入 `.sdlc/PRD.md`（目录不存在则创建）。
7. **给出下一步**：提示用 `un-requirement-clarify` 补齐歧义、用 `un-acceptance-criteria` 转验收标准。

## Rules

- 平台无关：不出现 `UIViewController`/`Activity`/`React`/`Flutter` 等具体技术词，留给设计阶段。
- 不替用户做产品决策；开放问题写进「风险与开放问题」。
- 保持可评审：每条 FR 可对应后续 AC。

## Resources

- `../../shared/prd-template.md` —— PRD 章节模板。
- `../plugin.md` —— 全流程与路由说明。
