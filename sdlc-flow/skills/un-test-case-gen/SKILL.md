---
name: un-test-case-gen
description: "从验收标准（AC.md）与技术方案生成测试用例：覆盖功能、边界、异常三类，每条用例关联 AC 编号、标优先级与期望结果，产出可直接交给 un-unit-test-gen / un-e2e-test-gen 的用例清单。属于 sdlc-flow 插件的测试阶段第一步，接在开发之后。"
agent_created: true
---

# Test Case Gen（测试用例生成）

## Overview

把「怎么算通过」变成「具体测什么」。从 AC 出发，系统生成功能/边界/异常三类用例，保证验收口径被用例完整覆盖，不再靠拍脑袋补测试。

## When to use

- 代码实现完成，要系统写测试。
- 研发全流程测试阶段起点，由 `un-sdlc-orchestrator` 调用。
- 需要一份可追溯到 AC 的用例基线。

## Workflow

1. **读取输入**：读 `.sdlc/AC.md` 与 `.sdlc/design.md`（边界/异常段）。
2. **三类展开**：
   - 功能：AC 的正常路径。
   - 边界：极值、空、超长、临界。
   - 异常：错误输入、网络/依赖失败、降级。
3. **关联与分级**：每条用例标 关联 AC、类型、优先级 P0/P1/P2、期望结果。
4. **覆盖核对**：确认每个 AC 至少一条用例，缺口回提 `un-acceptance-criteria`。
5. **落盘**：写入 `.sdlc/test-cases.md`（参考 `../../shared/testcase-template.md`）。
6. **下一步**：按类型交给 `un-unit-test-gen`（单测）/ `un-e2e-test-gen`（端到端）。

## Rules

- 用例必须可独立执行、结果确定。
- 与 AC 双向可追溯。
- 不写实现代码，只定义「测什么」。

## Resources

- `../../shared/testcase-template.md` —— 用例清单模板。
- `../../shared/ac-template.md` —— 用例来源。
