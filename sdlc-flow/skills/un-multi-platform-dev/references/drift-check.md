# 漂移检查（Drift Check）— 保证规范与代码不脱节

`spec` 会滞后于代码，这是跨端开发的常态。本文件描述 `un-multi-platform-dev` 技能内置的
**确定性漂移检查**流程：它不调用 LLM，只是**扫描代码 + 对比契约/符号**，把"某一端
没跟上"这件事变成可发现、可报告、可放进 CI 的信号。检查出的差异交给人（或技能的
AI 对账步骤）决定——更新规范，还是回退代码。

漂移检查与 `SKILL.md` 里的"Spec 滞后与正确性"章节一一对应，是这个治理思路的落地工具。

## 两种模式

| 模式 | 输入 | 做什么 | 置信度 | 何时用 |
|------|------|--------|--------|--------|
| `checkpoint` | 一份带"检查点"的契约 | 按契约里声明的检查点，逐个去各端代码里 grep 预期符号，产出"功能 × 端"覆盖矩阵 | 高（你定义的检查点 = 真源） | 已经有契约、想持续验证各端没漏做 |
| `symbol` | 仅代码 | 抽取各端路由/页面/公开符号，对比"哪些屏幕在某端没有"，并产出可反向写回契约的检查点草稿 | 低（启发式，需人审） | 没有契约、或想从现有代码反向提炼契约 |

`--mode auto`（默认）：给了可解析的契约就跑 `checkpoint`，否则跑 `symbol`。

## 怎么跑

```bash
# 1) checkpoint 模式：用契约里的检查点核对各端代码
python3 scripts/drift_check.py \
  --platform ios:<ios-root> --platform android:<android-root> \
  --platform flutter:<flutter-root> --platform react_web:<web-root> \
  --contract path/to/feature-contract.md \
  --report drift-report.md          # 可选：写出 markdown 报告
  --json                            # 可选：机器可读，给 CI 用

# 2) symbol 模式：只给代码，自动发现平台并比对路由/页面
python3 scripts/drift_check.py --workspace <workspace> --report drift-report.md

# 3) 混合：显式指定平台 + 用契约
python3 scripts/drift_check.py --platform flutter:<r> --platform react_web:<r> \
  --contract contract.md --json
```

- `--platform NAME:PATH` 可重复；端名取 `ios / android / flutter / react_native /
  react_web / vue_web / h5_web / wechat_mp / uniapp`。
- 不给 `--platform` 时，会用 `detect_platforms.py` 扫描 `--workspace`（默认当前目录）。
- 不确定写 `--json`，CI 里用 `jq` 判断 `absent` 数量决定是否阻断。

## checkpoint 模式详解

### 契约里怎么写检查点

在功能契约里加一个 `## 检查点` 章节，放一个 yaml 围栏块。每个检查点声明一个
`id`、`desc`，以及各端去代码里匹配用的**正则**（`match.<端名>`）。某端没单独给就
退而求其次用 `default_match`，再不行用 `id` 本身当关键字。

```yaml
checkpoints:
  - id: user-login
    desc: 用户登录入口
    match.ios: "LoginManager"
    match.android: "LoginRepository"
    match.flutter: "login"
    match.react_web: "login\("
  - id: logout
    desc: 退出登录
    match.ios: "LogoutManager"
    match.android: "LogoutRepository"
```

> 正则里的括号、点等要转义（`login\(`）。脚本优先用 PyYAML 解析；没有 PyYAML 时
> 也能解析这种"扁平"子集（无需嵌套缩进）。

### 输出

覆盖矩阵示例（✔ = 找到预期符号，✘ = 没找到 → 疑似漂移）：

```
| Checkpoint | Flutter | React (Web) | iOS |
|------------|---------|-------------|-----|
| user-login | ✔       | ✔           | ✔   |
| logout     | ✘       | ✔           | ✘   |
```

✘ 不代表一定错——可能是该端用了不同命名。差异交给人对账：要么在契约里补
Platform Notes 说明"该端确实没有此功能"，要么去补代码。

## symbol 模式详解（启发式）

只比较"路由可比较"的端：`flutter / react_web / react_native / vue_web / h5_web /
wechat_mp / uniapp`（它们的界面以路由/页面字符串表达，可对齐）。iOS / Android 的
原生界面不是字符串路由，不参与此对比。

- 抽取各端源码里的路由/页面字符串（`/profile`、`pages/settings/settings` 等）。
- **按叶节点归一化**：`/settings` 和 `pages/settings/settings` 都归一成 `settings`，
  所以同一屏幕在不同端不同命名也不会误报。
- 某屏幕只存在于部分端 → 列为漂移候选（低置信，需人审）。
- 顺手产出 `suggested` 检查点 YAML（每个屏幕一条，带各端原始 token 的正则），
  可直接粘回契约，把"代码领先"反向沉淀成"契约领先"。

> 注意：symbol 模式是**探查**性质的，会抓到 API 路径、资源路径等噪声，且无法判断
> "功能逻辑是否一致"，只能看"界面/入口是否齐"。它是 checkpoint 模式的前置与补充，
> 不是替代。最终以 checkpoint 模式（契约为真源）为准。

## 接入 CI（让滞后自动暴露）

把漂移检查当门禁，规范就不会悄悄落后：

```yaml
# .github/workflows/drift.yml (示意)
- name: Cross-platform drift check
  run: |
    python3 skills/un-multi-platform-dev/scripts/drift_check.py \
      --workspace . --contract specs/login/contract.md --json > drift.json
    # 统计 absent 数量，>0 则失败（可按需改为仅告警）
    python3 - <<'PY'
    import json,sys
    d=json.load(open('drift.json'))
    miss=sum(1 for r in d.get('matrix',[]) for c in r['cells'].values() if c.get('status')=='absent')
    sys.exit(1 if miss else 0)
    PY
```

`symbol` 模式也可周期性跑（比如每天定时任务 / cron），产出差异报告发给团队，作为
"该对账了"的提醒——这正是 `SKILL.md` 里"AI 辅助对账"的触发信号。

## 与 AI 对账的衔接

1. 漂移检查产出差异（✘ 单元格 / 漂移候选）。
2. 技能的同步/对账步骤**从各端代码重新提炼契约**，与已写规范 diff。
3. 差异交人决定：**更新规范**（代码领先且正确）还是**回退代码**（规范是真源）。
4. 规范是否更新永远是人的决定；工具只暴露差异，不擅自改规范。
