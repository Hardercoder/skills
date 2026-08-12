# 研发全流程 Plugin（SDLC Flow）

把「需求 PRD → 设计 → 开发 → 测试」整条研发链路收进一个 plugin，每个阶段是一个可独立调用、也可被编排器串联的 skill。`un-multi-platform-dev`（多端协同开发）作为开发阶段的核心技能整体纳入。

## 目录结构

```
sdlc-flow/
├── .claude-plugin/
│   └── plugin.json          # Claude Code plugin 清单（同时兼容 Cursor/Codex 的 Agent Skills 标准）
├── plugin.md                # 本说明
├── shared/                  # 跨阶段共享模板（prd/ac/design/tasks/testcase/report/contract-bridge）
└── skills/                  # ★ 17 个 skill，遵循 Agent Skills 开放标准（name + description frontmatter）
    ├── un-sdlc-orchestrator/
    ├── un-prd-writer/  un-requirement-clarify/  un-acceptance-criteria/  un-user-story-map/
    ├── un-tech-design/  un-api-design/  un-ui-spec/  un-task-breakdown/
    ├── un-multi-platform-dev/   # 含 scripts/（detect_platforms.py、drift_check.py）与 references/
    ├── un-code-implement/  un-code-review/
    └── un-test-case-gen/  un-unit-test-gen/  un-e2e-test-gen/  un-bug-triage/  un-test-report/
```

> 在 WorkBuddy 中，每个 skill 仍通过软链安装到 `~/.workbuddy/skills/<name>`（源真值在 `skills/<name>`）。

## 跨工具安装（格式兼容性）

本 plugin 的 skill 遵循 Anthropic 开源的 **Agent Skills 标准**（agentskills.io），Cursor / Codex / Claude Code 均原生识别 `SKILL.md`（`name` + `description` frontmatter），因此同一套可跨工具安装。

| 工具 | 安装方式 | 调用形式 |
|---|---|---|
| **Cursor** | 把整个 `sdlc-flow/` 放进 `.cursor/skills/`（或 `~/.cursor/skills/`，递归扫描） | `/un-prd-writer` 或按 description 自动触发 |
| **Codex** | 放进 `~/.codex/skills/` 或仓库 `.agents/skills/` | `$un-prd-writer` 或自动触发 |
| **Claude Code（standalone）** | 放进 `.claude/skills/` | `/un-prd-writer` |
| **Claude Code（plugin）** | `claude --plugin-dir ./sdlc-flow` 或 `/plugin install /path/to/sdlc-flow` | `/sdlc-flow:un-prd-writer`（带插件命名空间） |

注意事项：
- `shared/` 模板通过 `../../shared/...` 相对引用，需把**整个 `sdlc-flow` 文件夹**一起使用（不要只拷单个 skill 文件夹）。
- 编排器 `un-sdlc-orchestrator` 的跨 skill 调用写的是「指令文本」：WorkBuddy 用 Skill 工具硬调用子 skill；Cursor/Codex/Claude 由 agent 按 description 自动匹配对应 skill（功能等价，非自动 RPC）。
- `un-multi-platform-dev` 的 Python 脚本（`scripts/`）三工具均可直接执行。
- `agent_created: true` 是 WorkBuddy 私有 frontmatter 字段，其它工具忽略，无影响。

## 适用场景

- 有一句话需求，想一路跑到可交付（PRD → 设计 → 多端代码 → 测试）。
- 只想用其中某一步（例如单独写 PRD、单独生成测试用例）。
- 多端产品：设计阶段产出的「平台无关契约」直接喂给 `un-multi-platform-dev` 当真源。

## 常见输入来源

- PRD 常来自**飞书文档 / 腾讯文档**等在线协作文档；`un-prd-writer` 会先读取链接或粘贴内容再整理（腾讯文档可用 `tencent-docs` 能力读取）。
- UI 设计稿通常来自 **MasterGo / Figma**；`un-ui-spec` 优先从中提取页面、状态与设计令牌，而非凭空设计。
- 也支持纯文本/一句话需求、会议纪要、客户原话作为起点。

## Pipeline（产物串联）

编排器在 workspace 的 `.sdlc/` 目录维护各阶段产物，下一阶段自动读取上一阶段输出：

```
.sdlc/PRD.md → AC.md → design.md(+contract) → tasks.md → 代码 → test-cases.md → report.md
```

## Skill 目录

| 阶段 | skill | 职责 |
|---|---|---|
| 编排 | `un-sdlc-orchestrator` | 总入口，按阶段路由、串联产物，也支持单独调用子 skill |
| 1 需求 | `un-prd-writer` | 从想法/粗需求生成结构化 PRD |
| 1 需求 | `un-requirement-clarify` | 需求缺口/歧义识别、主动反问、冲突检测 |
| 1 需求 | `un-acceptance-criteria` | 把需求转成可验证验收标准（Given/When/Then、DoD） |
| 1 需求 | `un-user-story-map` | 史诗/故事地图、优先级排序（大需求） |
| 2 设计 | `un-tech-design` | 架构、模块划分、数据流、关键决策、风险 |
| 2 设计 | `un-api-design` | 接口契约（OpenAPI/GraphQL/Protobuf 草稿） |
| 2 设计 | `un-ui-spec` | UI/交互规范、页面状态、设计令牌 |
| 2 设计 | `un-task-breakdown` | 拆 WBS / 可执行任务、估算、依赖 |
| 3 开发 | `un-multi-platform-dev` | 多端协同开发，以平台无关契约为真源（整体移入 plugin） |
| 3 开发 | `un-code-implement` | 单端/单模块实现（非多端场景） |
| 3 开发 | `un-code-review` | 评审：diff 说明、风险点、改进建议 |
| 4 测试 | `un-test-case-gen` | 从 AC/设计生成功能/边界/异常用例 |
| 4 测试 | `un-unit-test-gen` | 按模块生成单元测试骨架 |
| 4 测试 | `un-e2e-test-gen` | 端到端/集成测试脚本 |
| 4 测试 | `un-bug-triage` | 缺陷复现、定位、根因、修复建议 |
| 4 测试 | `un-test-report` | 覆盖率、用例执行、遗留风险汇总 |

## 路由规则（编排器）

1. 收到需求 → 进入 `un-prd-writer` → `un-requirement-clarify`（澄清后修订 PRD）→ `un-acceptance-criteria`。
2. 有 PRD+AC → 进入 `un-tech-design` → `un-api-design` / `un-ui-spec`（按需）→ `un-task-breakdown`。
3. 设计产出「平台无关契约」后：
   - 多端 → `un-multi-platform-dev`（contract 直接作为真源）。
   - 单端 → `un-code-implement`。
   - 之后可跑 `un-code-review`。
4. 有代码+AC → `un-test-case-gen` → `un-unit-test-gen` / `un-e2e-test-gen` → `un-bug-triage` → `un-test-report`。

## 关键衔接：设计契约 ↔ 多端真源

设计阶段的 `design.md` 末尾「平台无关契约」段落，字段对齐 `un-multi-platform-dev` 的
`references/templates/feature-contract.md`。对齐约定见 `shared/contract-bridge.md`。
因此 `un-multi-platform-dev` 可直接消费设计产物，无需重写规范；其 `drift_check.py`
跑出的分歧也能回写设计文档，形成闭环。

## 共享模板

`shared/` 下提供各阶段 Markdown 模板：prd-template、ac-template、design-template、
tasks-template、testcase-template、report-template、contract-bridge。各 skill 直接引用。
