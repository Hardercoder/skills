# 保证多端一致的多种方式（不止 OpenSpec / SpecKit）

OpenSpec 与 SpecKit 只是"规范驱动开发"这一类工具中的两个例子。要保证 iOS /
Android / Flutter / React / React Native / H5 / 微信小程序 / Uni-app 之间行为、
视觉、接口一致，应根据工程现状选择不同"杠杆"。本文件是选型字典，供
`un-multi-platform-dev` 技能在"工具检查"环节按需查阅。

## 一、杠杆分层总览

| 层级 | 思路 | 代表手段 | 适用场景 |
|------|------|----------|----------|
| 源头消除 | 一份源码生成多端，结构上不可能漂移 | Flutter / RN / Taro / uni-app / KMP；代码生成 | 能统一代码库时首选 |
| 共享契约 | 用"契约"对齐各端，而非逐端手写 | 设计令牌、API Schema、组件目录 | 多独立代码库、需要视觉/接口一致 |
| 验证兜底 | 不强制统一，用测试发现分歧 | 契约测试、可视化回归、架构治理 | 无法统一源码、需持续防回归 |
| 漂移治理 | 规范滞后时仍能发现并修复 | SpecGov / drift / oasdiff + AI 对账 | 规范容易跟不上代码 |

## 二、杠杆一：单源码 → 多端生成（从源头消除分歧）

能走通单代码库，就优先走单代码库——这是唯一"结构上不可能漂移"的方案。

- **Flutter**：一套 Dart 同时出 iOS / Android / Web / 桌面。
- **React Native + Expo + react-native-web**：一套 React 出 iOS / Android / Web。
- **Taro / uni-app / Kbone**：一套代码出 微信/支付宝/百度小程序 + H5 + 部分原生。
- **Kotlin Multiplatform (KMP)**：共享业务逻辑层，UI 各端原生。
- **API / 类型代码生成**：OpenAPI Generator、openapi-typescript、GraphQL Code
  Generator、Protobuf + buf、tRPC / zod 类型共享——让"接口与类型"成为单一事实来源，
  各端从同一份 schema 生成 client，避免手写不一致。
- **设计令牌代码生成**：Style Dictionary、Tokens Studio、Supernova、Specify——
  一份 token 源（YAML/JSON）生成 CSS 变量 / Swift / Kotlin dimens / WXML，
  保证颜色、间距、字号跨端一致。

## 三、杠杆二：共享契约 / 规范层（对齐而非生成）

当代码库无法统一时，把"契约"作为真源：

- **设计令牌即单一事实来源**：颜色、间距、字体、阴影定义一次，各端消费。
- **API 契约**：OpenAPI / GraphQL schema / Protobuf 是机器可读的接口真源。
- **组件契约**：Storybook 作为跨端组件目录与可视化基线；Rive / Lottie 共享动效。
- 这一层与 OpenSpec / SpecKit 的"feature spec"互补：spec 描述功能行为，
  token/schema 描述视觉与接口，二者共同构成跨端真源。

## 四、杠杆三：契约测试与漂移测试（用验证兜底）

规范可能滞后，但**测试不会**。用自动化测试在 CI 中持续发现分歧：

- **消费者驱动契约（CDC）**：Pact（支持 12+ 语言，Pact Broker + can-i-deploy
  作为部署门禁）、Spring Cloud Contract、Specmatic（把 OpenAPI 变成可执行契约
  / mock / 测试）、Dredd。消费者定义期望，提供者验证兼容，任意一方破坏契约
  则 CI 失败。
- **Schema 校验与破坏性变更检测**：oasdiff（OpenAPI 破坏性变更 diff）、
  Spectral（规范 lint / 治理规则）、GraphQL Inspector、buf（Protobuf 兼容检查）。
- **属性 / 模糊测试**：Schemathesis 从 schema 生成异常输入，抓边界行为漂移。
- **可视化回归**：Chromatic（Storybook）、Percy、Argos、Applitools 抓跨端 UI
  漂移；Flutter golden tests、jest-expo 快照做原生像素基线。

## 五、规范即测试 / 可执行规范

- **BDD**：Cucumber / Gherkin（Given-When-Then 可执行）、SpecFlow——把验收场景
  直接变成可跑的测试，规范与实现始终一致。
- **架构治理**：ArchUnit（JVM）、dependency-cruiser（JS）、ArchGuard（跨仓依赖
  分析）、Structurizr（C4 模型即代码）——约束模块边界，防止各端悄悄偏离架构。
- **测试作为真源**：从测试反向生成规范；doc-test 保证文档里的代码片段可执行。

## 六、Spec 滞后与正确性（Drift）

规范不可能永远与代码同步——关键是**让滞后可被及时发现并修复**。

1. **设计优先（spec leads）预防漂移**：规范先于实现更新，代码不会"跑在规范前面"。
2. **确定性检查器（CI 门禁，不依赖 LLM）**：
   - **SpecGov**：声明哪些工件（spec/ADR/设计文档）与哪些代码关联；代码改动绕过
     对应规范时告警（advisory）→ 高置信后转 strict 阻断 PR。无 API Key、可复现。
   - **drift（Fiberplane）**：用 tree-sitter + git provenance 把 markdown 规范
     "锚定"到具体代码符号；绑定代码变更即标记规范过期，在 CI 抓 stale。
   - oasdiff / Spectral / Pact / 可视化回归：分别从接口、规范、契约、视觉维度发现漂移。
3. **活规范实践**：规范随代码同一次提交更新；OpenSpec 的 archive 让规范随变更
   沉淀为永久真源；当代码领先于规范时做**反向同步**（从代码提炼契约并回写规范）。
4. **自修复 / AI 辅助对账**：Optic 等工具在观察到代码与规范不符时**提议修补规范**；
   本技能在 sync 模式的"提升为契约"步骤本质就是一次对账——周期性地**从各端代码
   重新提炼契约并与已写规范 diff**，把差异交给人决定：更新规范，还是回退代码。
   注意：规范是否更新永远是人的决定，工具只负责暴露差异。

## 七、单仓 / 共享包（结构上减少漂移）

- **Nx / Turborepo / Bazel**：单仓 + 共享内部包 + 统一 lint/配置，物理上降低漂移。
- **共享内部包**：跨端共享类型与业务逻辑（TS 包、KMP 模块）。
- **Renovate / Dependabot**：依赖版本一致性。

## 八、选型建议（什么时候用哪个）

- **能单源码就优先单源码**：Flutter / RN(+Expo) / Taro / uni-app 直接消除问题。
- **多独立代码库**：规范驱动（OpenSpec / SpecKit / Kiro 任选）+ 契约测试兜底。
- **视觉一致**：设计令牌（Style Dictionary 等）+ 可视化回归（Chromatic/Percy）。
- **接口一致**：OpenAPI / GraphQL + oasdiff / Spectral / Pact。
- **规范会滞后（几乎必然）**：上 SpecGov / drift 这类确定性检查 + AI 对账，
  并坚持"规范随代码同提交"。

> 本技能默认推荐顺序：**先看能否单源码 → 否则建平台无关契约为真源 → 再用契约
> 测试/可视化回归兜底 → 最后用确定性检查 + AI 对账治理规范滞后。** OpenSpec 与
> SpecKit 仅是规范驱动这一类里最轻量的两个候选，不是唯一答案。
