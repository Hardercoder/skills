---
name: un-e2e-test-gen
description: "从用例清单与技术方案生成端到端/集成测试脚本（如 UI 自动化、接口集成、关键用户旅程），覆盖跨模块与跨端主流程。产出可挂 CI 的测试脚本，并说明环境依赖与需人工维护的部分。属于 sdlc-flow 插件的测试阶段，接在 un-test-case-gen 之后、可选。"
agent_created: true
---

# E2E Test Gen（端到端测试生成）

## Overview

单元测保证「零件对」，端到端测保证「整机跑得通」。本 skill 针对关键用户旅程与跨模块/跨端主流程生成可挂 CI 的 e2e 脚本。

## When to use

- 有关键旅程或跨端一致性需要守护。
- 多端产品用 `un-multi-platform-dev` 时可配合可视化回归（Chromatic/Percy）。
- 研发全流程测试阶段可选增强。

## Workflow

1. **读取用例**：读 `.sdlc/test-cases.md` 中端到端级条目 + `.sdlc/design.md` 主流程。
2. **选工具**：Web→Playwright/Cypress；移动→Maestro/Detox；接口→Postman/RestAssured。
3. **写脚本**：关键旅程步骤化，含前置/断言/清理；多端注意共享契约一致性。
4. **环境说明**：列出 base URL、账号、数据准备、需人工维护的选择器/令牌。
5. **落盘**：写入工程 e2e 目录；报告覆盖的旅程与缺口。
6. **下一步**：运行结果交给 `un-bug-triage`；汇总交 `un-test-report`。

## Rules

- e2e 只覆盖关键路径，避免把单测能测的搬上来（慢且脆）。
- 不硬编码密钥；环境通过配置注入。
- 多端脚本要核对同一契约，避免各端各写各的。

## Resources

- `../../shared/testcase-template.md` —— 用例来源。
- `../un-multi-platform-dev/references/cross-platform-consistency.md` —— 多端可视化回归手段。
