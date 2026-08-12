---
name: un-unit-test-gen
description: "依据测试用例清单（test-cases.md）中适合单测的条目，为指定模块生成单元测试骨架与断言，对齐项目测试框架（如 XCTest / JUnit / JUnit5 / pytest / Jest）。产出可运行、可补充的测试代码，并标注仍需人工补全的桩。属于 sdlc-flow 插件的测试阶段，接在 un-test-case-gen 之后。"
agent_created: true
---

# Unit Test Gen（单元测试生成）

## Overview

把用例清单里「单元级」的部分落成测试代码骨架。目标是覆盖函数/类级别的行为，尤其边界与异常，让开发者在骨架上补具体断言而不是从零写。

## When to use

- 有 `.sdlc/test-cases.md`，要落地单测。
- 研发全流程测试阶段，由编排器调用。
- 需要快速铺开模块测试覆盖。

## Workflow

1. **读取用例**：读 `.sdlc/test-cases.md`，筛出适合单测的条目（功能/边界/异常中单元级）。
2. **探测框架**：识别工程测试框架（参考 `../un-multi-platform-dev/scripts/detect_platforms.py` 思路，或按用户指定）。
3. **生成测试**：每个目标函数/类生成测试文件/方法，含 arrange-act-assert 与关键断言。
4. **标桩**：未决输入/外部依赖用 mock/桩，并注明需人工补。
5. **落盘**：写入工程测试目录；报告生成了哪些、哪些待补。
6. **下一步**：集成/端到端交给 `un-e2e-test-gen`；发现缺陷走 `un-bug-triage`。

## Rules

- 生成的测试必须能编译/运行（桩合法），不抛未定义。
- 不篡改被测逻辑，只写测试。
- 明确标注 AI 生成的断言，便于人工复核。

## Resources

- `../../shared/testcase-template.md` —— 用例来源。
- `../un-multi-platform-dev/scripts/detect_platforms.py` —— 工程/框架探测思路。
