---
name: un-requirement-clarify
description: "对已有 PRD 做需求澄清：识别缺口、歧义、冲突与不可测试项，产出可执行的反问清单，并修订 PRD。区分『事实缺口（需补信息）』与『产品决策（需人拍板）』，不替用户做业务决策。属于 sdlc-flow 插件的需求阶段，通常接在 un-prd-writer 之后、un-acceptance-criteria 之前。"
agent_created: true
---

# Requirement Clarify（需求澄清）

## Overview

PRD 草稿往往有歧义、冲突或漏点。本 skill 做一轮「体检」：找出哪里说不清、哪里自相矛盾、哪里没法验证，给出一份**具体、可回答的反问清单**，并把能立刻修订的地方直接改掉。

## When to use

- PRD 写完后想先过一遍再做设计。
- 用户说「需求有点模糊，帮我理一下」。
- 研发全流程中 `un-prd-writer` 之后由编排器调用。

## Workflow

1. **读取 PRD**：读 `.sdlc/PRD.md`（没有则提示先跑 `un-prd-writer`）。
2. **四类扫描**：
   - 缺口：声称的功能但缺前置/触发/边界。
   - 歧义：一个描述多种理解。
   - 冲突：范围/优先级/非功能间互相矛盾。
   - 不可测：写不出 AC 的模糊表述。
3. **产出反问清单**：每条给「为什么问 + 建议选项」，区分需补信息 vs 需人决策。
4. **就地修订**：对无争议的澄清项直接改 PRD，并标记改动。
5. **落盘**：更新 `.sdlc/PRD.md`，输出澄清问题给用户确认。
6. **下一步**：澄清确认后交给 `un-acceptance-criteria`。

## Rules

- 不替用户拍板产品方向；决策类问题只列选项。
- 反问要具体、可回答，避免「这个需求明确吗」式废话。
- 修订 PRD 时保留可追溯（标注哪条澄清导致改动）。

## Resources

- `../../shared/prd-template.md` —— 检查章节完整性的依据。
- `../plugin.md` —— 全流程与路由说明。
