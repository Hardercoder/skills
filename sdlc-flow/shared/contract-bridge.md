# 设计契约 ↔ 多端真源 对齐约定（contract-bridge）

`un-multi-platform-dev` 以 `references/templates/feature-contract.md`（平台无关契约）为真源。
设计阶段（`un-tech-design` / `un-api-design` / `un-ui-spec`）产出的平台无关契约应与该模板字段对齐，
使编排器能把 `design.md` 直接作为 contract 喂给 `un-multi-platform-dev`，无需重写。

## 字段映射

| feature-contract.md 段落 | 由哪个设计 skill 产出 | 说明 |
|---|---|---|
| 行为（Behavior） | `un-tech-design` | 功能行为描述，平台无关 |
| 数据模型（Data model） | `un-tech-design` / `un-api-design` | 实体、字段、类型；接口用 OpenAPI/GraphQL/Protobuf |
| 接口/API 契约 | `un-api-design` | 端点、请求/响应、错误码 |
| UI 状态（UI states） | `un-ui-spec` | 页面/组件状态、空/加载/错误态 |
| 边界与异常（Edge cases） | `un-tech-design` + `un-acceptance-criteria` | 异常流、降级 |
| 验收场景（Acceptance） | `un-acceptance-criteria` | 对应 AC 编号 |
| 检查点（## 检查点） | 编排器/开发阶段 | 供 `drift_check.py` 的 checkpoint 模式消费 |

## 使用方式
1. 设计阶段把上述字段写进 `design.md` 末尾的「平台无关契约」段落。
2. 编排器进入开发阶段时，若目标为多端，把该段落作为 `un-multi-platform-dev` 的 contract。
3. `un-multi-platform-dev` 跑完 `drift_check.py` 后，分歧回写 `design.md`，保持规范与代码对齐。

## 红线
- 契约正文不得出现 `UIViewController` / `Activity` / `Widget` / `useState` / `Page` 等平台专属符号。
- 平台差异只在 Platform Notes / 各端实现里体现。
