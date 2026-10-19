# 研发全流程 Plugin（SDLC Flow）

把「需求 PRD → 设计 → 开发 → 测试」整条研发链路收进一个 plugin，每个阶段是一个可独立调用、也可被编排器串联的 skill。`un-multi-platform-dev`（多端协同开发）作为开发阶段的核心技能整体纳入。

## 目录结构

```
sdlc-flow/
├── .claude-plugin/
│   └── plugin.json          # Claude Code plugin 清单（同时兼容 Cursor/Codex 的 Agent Skills 标准）
├── plugin.md                # 本说明
├── shared/                  # 跨阶段共享模板（见「共享模板」一节，现共 17 个）
└── skills/                  # ★ 34 个 skill，遵循 Agent Skills 开放标准（name + description frontmatter）
    # —— 阶段技能（需求/设计/开发/测试，17 个，原有）——
    ├── un-sdlc-orchestrator/  un-prd-writer/  un-requirement-clarify/  un-acceptance-criteria/
    ├── un-user-story-map/  un-tech-design/  un-api-design/  un-ui-spec/  un-task-breakdown/
    ├── un-multi-platform-dev/   # 含 scripts/（detect_platforms.py、drift_check.py）与 references/
    ├── un-code-implement/  un-code-review/
    └── un-test-case-gen/  un-unit-test-gen/  un-e2e-test-gen/  un-bug-triage/  un-test-report/
    # —— 方法纪律层（6 个，新增；借鉴 Superpowers 哲学）——
    ├── un-tdd-guard/  un-systematic-debugging/  un-verify-before-done/
    ├── un-git-worktree/  un-parallel-agents/  un-skill-authoring/   # un-skill-authoring 为 meta 技能
    # —— 缺失阶段（11 个，新增）——
    ├── un-tech-spike/        # 需求前：技术探活
    ├── un-threat-modeling/  un-data-model/  un-adr/   # 设计期：安全/数据/架构决策
    ├── un-i18n-plan/  un-a11y-check/       # 设计-UI：国际化/无障碍
    ├── un-doc-gen/           # 开发后：文档生成
    ├── un-release-checklist/  un-cicd/      # 测试后：发版清单 / CI-CD
    ├── un-observability-plan/ # 上线前：可观测性
    └── un-postmortem/        # 运维期：事故复盘
```

> 在 WorkBuddy 中，每个 skill 仍通过软链安装到 `~/.workbuddy/skills/<name>`（源真值在 `skills/<name>`）。
> 新增的 17 个 skill 已软链；`un-skill-authoring` 描述了本 plugin 的 skill 编写规范。

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

编排器在 workspace 的 `.sdlc/` 目录维护各阶段产物，下一阶段自动读取上一阶段输出。新增的
阶段技能与纪律技能穿插在各处（见路由规则），产物示意：

```
.sdlc/
├─ tech-spike.md        (un-tech-spike, 需求前)
├─ PRD.md → AC.md       (需求)
├─ design.md(+contract) ┬ threat-model.md (un-threat-modeling)
│                       ├ data-model.md  (un-data-model)
│                       └ adr/<nnn>.md   (un-adr)
├─ i18n-plan.md / a11y-check.md   (设计-UI, 按需)
├─ tasks.md → 代码      (开发；开发期受 un-tdd-guard 约束)
├─ test-cases.md → 单测/ e2e → report.md   (测试)
├─ docs/               (un-doc-gen, 开发后)
├─ release-checklist.md + cicd.md   (测试后)
├─ observability-plan.md   (上线前)
└─ postmortem/<date>.md     (运维期, 事故后)
```
> 纪律层（un-tdd-guard / un-systematic-debugging / un-verify-before-done）不产出文档，
> 而是对开发/测试/收尾过程的**强制约束**，可随时被任意阶段调用。

## Skill 目录（34 个）

### 阶段技能（原有 17 个）
| 阶段 | skill | 职责 |
|---|---|---|
| 编排 | `un-sdlc-orchestrator` | 总入口，按阶段路由、串联产物，也支持单独调用子 skill |
| 1 需求 | `un-prd-writer` | 从想法/粗需求生成结构化 PRD（支持飞书/腾讯文档） |
| 1 需求 | `un-requirement-clarify` | 需求缺口/歧义识别、主动反问、冲突检测 |
| 1 需求 | `un-acceptance-criteria` | 把需求转成可验证验收标准（Given/When/Then、DoD） |
| 1 需求 | `un-user-story-map` | 史诗/故事地图、优先级排序（大需求） |
| 2 设计 | `un-tech-design` | 架构、模块划分、数据流、关键决策、风险 |
| 2 设计 | `un-api-design` | 接口契约（OpenAPI/GraphQL/Protobuf 草稿） |
| 2 设计 | `un-ui-spec` | UI/交互规范、页面状态、设计令牌（读 MasterGo/Figma） |
| 2 设计 | `un-task-breakdown` | 拆 WBS / 可执行任务、估算、依赖 |
| 3 开发 | `un-multi-platform-dev` | 多端协同开发，以平台无关契约为真源（含 Python 脚本） |
| 3 开发 | `un-code-implement` | 单端/单模块实现（非多端场景） |
| 3 开发 | `un-code-review` | 评审：diff 说明、风险点、改进建议 |
| 4 测试 | `un-test-case-gen` | 从 AC/设计生成功能/边界/异常用例 |
| 4 测试 | `un-unit-test-gen` | 按模块生成单元测试骨架 |
| 4 测试 | `un-e2e-test-gen` | 端到端/集成测试脚本 |
| 4 测试 | `un-bug-triage` | 缺陷复现、定位、根因、修复建议 |
| 4 测试 | `un-test-report` | 覆盖率、用例执行、遗留风险汇总 |

### 方法纪律层（新增 6 个，借鉴 Superpowers 哲学）
| skill | 职责 |
|---|---|
| `un-tdd-guard` | 强制 TDD：红-绿-重构，先写失败测试再写实现，删无测试代码 |
| `un-systematic-debugging` | 四阶段根因调试：复现→定位→根因→修复验证 |
| `un-verify-before-done` | 完成前验证闸门：用证据确认，而非声称 |
| `un-git-worktree` | 用 worktree 隔离并行工作，保持主树干净 |
| `un-parallel-agents` | 把无依赖任务派给独立子代理并行执行 |
| `un-skill-authoring` | meta：按本 plugin 规范新增/修订 skill（含校验） |

### 缺失阶段（新增 11 个）
| 阶段 | skill | 职责 |
|---|---|---|
| 需求前 | `un-tech-spike` | 时间盒技术探活，验证最高风险假设，输出 go/no-go |
| 设计期 | `un-threat-modeling` | 安全威胁建模（STRIDE），输出 threat-model.md |
| 设计期 | `un-data-model` | 数据建模：实体/关系/键/索引/生命周期 |
| 设计期 | `un-adr` | 架构决策记录（ADR），记录决策与权衡 |
| 设计-UI | `un-i18n-plan` | 国际化方案：locale/字符串外置/格式化/RTL |
| 设计-UI | `un-a11y-check` | 无障碍清单：WCAG/键盘/对比度/ARIA/读屏 |
| 开发后 | `un-doc-gen` | 文档生成：README/API/runbook/用户手册 |
| 测试后 | `un-release-checklist` | 发版清单：版本/变更日志/迁移/回滚/健康检查 |
| 测试后 | `un-cicd` | CI/CD 流水线：构建/测试/部署/门禁/密钥 |
| 上线前 | `un-observability-plan` | 可观测性：日志/指标/追踪/告警/看板 |
| 运维期 | `un-postmortem` | 事故复盘（blameless）：时间线/影响/根因/行动项 |

## 路由规则（编排器）

1. **需求前（可选）**：高风险技术假设 → `un-tech-spike`（go/no-go 后再写 PRD）。
2. 收到需求 → 进入 `un-prd-writer` → `un-requirement-clarify`（澄清后修订 PRD）→ `un-acceptance-criteria`。大需求可先 `un-user-story-map`。
3. 有 PRD+AC → 进入 `un-tech-design` → `un-api-design` / `un-ui-spec`（按需）→ `un-task-breakdown`。
   设计期内可并行：`un-threat-modeling`、`un-data-model`、`un-adr`、以及 `un-i18n-plan`/`un-a11y-check`（UI 相关）。
4. 设计产出「平台无关契约」后：
   - 多端 → `un-multi-platform-dev`（contract 直接作为真源）。
   - 单端 → `un-code-implement`。
   - 开发全程受 `un-tdd-guard` 约束；并行开发可用 `un-git-worktree` + `un-parallel-agents`；完成后 `un-code-review`。
   - 调试时走 `un-systematic-debugging`；每项任务收尾走 `un-verify-before-done`。
5. 有代码+AC → `un-test-case-gen` → `un-unit-test-gen` / `un-e2e-test-gen` → `un-bug-triage` → `un-test-report`。
6. **测试后 / 上线前**：`un-doc-gen` 出文档 → `un-release-checklist` + `un-cicd` 准备发版 → `un-observability-plan` 规划可观测性。
7. **运维期**：发生生产事故 → `un-postmortem`（blameless 复盘）。

## 关键衔接：设计契约 ↔ 多端真源

设计阶段的 `design.md` 末尾「平台无关契约」段落，字段对齐 `un-multi-platform-dev` 的
`references/templates/feature-contract.md`。对齐约定见 `shared/contract-bridge.md`。
因此 `un-multi-platform-dev` 可直接消费设计产物，无需重写规范；其 `drift_check.py`
跑出的分歧也能回写设计文档，形成闭环。

## 共享模板

`shared/` 下提供各阶段 Markdown 模板（共 17 个），产物型 skill 通过 `../../shared/<t>.md`
引用（skill 在 `skills/<name>/` 下，需两级回到插件根）：

- 阶段：prd-template、ac-template、design-template、tasks-template、testcase-template、report-template、contract-bridge
- 缺失阶段：tech-spike-template、threat-model-template、data-model-template、adr-template、i18n-template、a11y-template、doc-template、release-checklist-template、observability-template、postmortem-template

> 分发时必须把整个 `sdlc-flow/` 文件夹一起拷贝，否则这些相对引用会断。
