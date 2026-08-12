# 技术方案模板（design-template）

> 由 `un-tech-design` 生成，路径建议 `.sdlc/design.md`。末尾「平台无关契约」段直接喂给 `un-multi-platform-dev`。

## 架构概览
- 总体架构图（文字/Mermaid）、分层、关键组件

## 模块划分
- 模块职责、边界、依赖关系

## 数据流
- 主要流程的数据走向、状态管理

## 关键决策与权衡
- 选型理由、取舍、备选方案

## 风险
- 技术风险、返工风险

## 平台无关契约（真源，喂给 un-multi-platform-dev）
### 行为（Behavior）
- 功能行为描述（不出现平台 SDK 名）

### 数据模型（Data model）
- 实体、字段、类型

### 接口/API 契约
- 端点、请求/响应、错误码（OpenAPI/GraphQL/Protobuf）

### UI 状态（UI states）
- 页面/组件状态、空/加载/错误态

### 边界与异常（Edge cases）
- 异常流、降级策略

### 验收场景（Acceptance）
- 关联 AC 编号

### 检查点（供 drift_check.py）
- CHECKPOINT: <platform-agnostic symbol> — 各端应实现
