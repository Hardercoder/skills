---
name: un-api-design
description: "为技术方案补充接口契约：以 OpenAPI / GraphQL / Protobuf 描述端点、请求响应、错误码与数据模型，作为多端共享的接口真源（配合 un-multi-platform-dev 的契约一致性手段）。属于 sdlc-flow 插件的设计阶段，通常接在 un-tech-design 之后、un-task-breakdown 之前。"
agent_created: true
---

# API Design（接口契约设计）

## Overview

把 `un-tech-design` 里的数据模型与交互落成**机器可读的接口契约**。契约是前后端、多端之间最强的「真源」之一——`un-multi-platform-dev` 会用 OpenAPI/GraphQL + oasdiff/Spectral/Pact 来保证各端一致。

## When to use

- 设计涉及服务端接口或跨端数据交换。
- 需要一份可生成代码、可契约测试的稳定接口定义。
- 研发全流程设计阶段的可选增强。

## Workflow

1. **读取设计**：读 `.sdlc/design.md` 的「数据模型 / 行为」段落。
2. **选型**：REST→OpenAPI，查询密集→GraphQL，高性能和多语言→Protobuf。
3. **写契约**：端点、方法、参数、响应 schema、错误码；标版本。
4. **一致性提示**：说明将用 oasdiff/Spectral/Pact 做契约测试（见 `../un-multi-platform-dev` 的 consistency 字典）。
5. **落盘**：作为 `.sdlc/design.md` 的「接口/API 契约」段落，或独立 `api-spec.yaml`。
6. **下一步**：交给 `un-task-breakdown` 拆任务。

## Rules

- 接口契约平台/语言无关；只描述「是什么」，不描述「怎么调」。
- 错误码与业务语义对齐 PRD 的非功能需求。
- 版本化，避免破坏性变更无痕。

## Resources

- `../../shared/design-template.md` —— 契约在 design.md 中的位置。
- `../un-multi-platform-dev/references/cross-platform-consistency.md` —— 契约测试与一致性手段字典。
