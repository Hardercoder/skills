---
name: un-test-report
description: "汇总测试阶段结果：覆盖率、用例执行（通过/失败/阻塞）、缺陷按严重级分布、遗留风险与发布结论。把 test-cases / unit-test / e2e / un-bug-triage 的产物收敛成一份决策用的测试报告，写入 .sdlc/report.md。属于 sdlc-flow 插件的测试阶段收尾。"
agent_created: true
---

# Test Report（测试报告）

## Overview

全流程的最后一道关。把分散的测试产物（用例、单测、e2e、缺陷）收敛成一份**给决策者的报告**：测得怎么样、还剩什么风险、能不能发。

## When to use

- 测试阶段临近收尾，要出结论。
- 研发全流程测试阶段最后一步，由编排器调用。
- 发布评审需要一份测试结论。

## Workflow

1. **汇总产物**：读 `.sdlc/test-cases.md`、单测/e2e 结果、`un-bug-triage` 输出。
2. **覆盖率**：行/分支/模块覆盖率（工程有则取，无则标注未采集）。
3. **执行统计**：用例总数/通过/失败/阻塞，按模块/优先级交叉。
4. **缺陷分布**：按 P0/P1/P2 统计，列未关闭项。
5. **遗留风险**：未覆盖项、已知问题、需跟进。
6. **结论**：是否达到发布标准，给出条件或阻断项。
7. **落盘**：写入 `.sdlc/report.md`（参考 `../../shared/report-template.md`）。

## Rules

- 结论明确（可发 / 有条件 / 不可发），不模棱两可。
- 数据来自实际执行，不编造覆盖率。
- 遗留风险必须可追溯，不隐藏。

## Resources

- `../../shared/report-template.md` —— 报告模板。
- `../../shared/testcase-template.md` —— 用例统计源。
