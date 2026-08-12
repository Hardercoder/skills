---
name: un-acceptance-criteria
description: "把 PRD 的功能需求转成可验证的验收标准（Given/When/Then），并给出完成定义（DoD）与非功能验收口径。每条 AC 可自动化、可追溯回 FR 编号，直接作为测试阶段 un-test-case-gen 的输入。属于 sdlc-flow 插件的需求阶段，接在 un-requirement-clarify 之后。"
agent_created: true
---

# Acceptance Criteria（验收标准生成）

## Overview

验收标准是需求与测试之间的契约。本 skill 把 PRD 的 FR 逐条翻译成 **Given/When/Then** 形式的可验证条件，并补上 DoD，让「做完没做完」不再靠感觉。

## When to use

- PRD 定稿后，要落到「怎么算通过」。
- 研发全流程需求阶段收尾，由 `un-sdlc-orchestrator` 调用。
- 测试阶段写用例前需要明确验收口径。

## Workflow

1. **读取 PRD**：读 `.sdlc/PRD.md`，定位功能需求 FR 与非功能需求。
2. **逐条转 AC**：每个 FR → 1+ 条 AC，格式 Given/When/Then，标优先级与关联 FR。
3. **补 DoD**：列出功能/测试/评审/文档的完成门槛。
4. **非功能验收**：把性能/兼容/安全转成可测量口径。
5. **落盘**：写入 `.sdlc/AC.md`（参考 `../../shared/ac-template.md`）。
6. **下一步**：交给 `un-tech-design`；测试阶段 `un-test-case-gen` 会直接消费本文件。

## Rules

- 每条 AC 必须可验证、可自动化；拒绝「体验良好」这类不可测描述。
- AC 与 FR 双向可追溯（编号关联）。
- 不新增需求范围，只把已有需求变得可验证。

## Resources

- `../../shared/ac-template.md` —— AC / DoD 模板。
- `../../shared/testcase-template.md` —— 下游 un-test-case-gen 的产物形态（保持一致）。
