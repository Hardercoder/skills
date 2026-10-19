# Workflows & Per-Platform Guidance

Detailed steps for the two modes defined in SKILL.md, plus concrete tips for
implementing and verifying each platform from a shared contract.

## Writing a good feature contract

The contract is the single source of truth. Keep it platform-agnostic.

- **Behavior first**: "As a <role>, I want <capability> so that <value>." Focus
  on user-visible behavior, not classes or widgets.
- **Data model**: entities, fields, types, constraints, validation rules. Name
  things neutrally (e.g. `Session`, not `UserDefaults`/`SharedPreferences`).
- **Interface / API contract**: operations, inputs, outputs, error cases —
  described in platform-neutral terms (e.g. "refresh token", not
  `URLSession`/`OkHttp`).
- **UI states**: screens/states, loading/empty/error states, navigation intent.
- **Edge cases & non-goals**: explicitly list what is out of scope to prevent
  scope creep across platforms.
- **Acceptance scenarios**: Given/When/Then that every platform must satisfy.
- **Platform Notes**: filled in during implementation — platform-specific
  deviations, library choices, limitations. Never put these in the body above.

Use `references/templates/feature-contract.md`.

## Mode A — Simultaneous development (多端同步开发)

1. Resolve targets and 真源 (spec-first).
2. Author the contract from the requirement; review it with the user.
3. For each target platform, in parallel:
   - Read the platform project at its detected root.
   - Implement from the contract; record platform notes.
   - Verify the platform builds/runs; capture the result.
   - Re-check behavior against the acceptance scenarios.
4. Reconcile: if two platforms diverge on a behavior, decide which is correct,
   update the contract, and propagate to the others.
5. Emit the sync report.

## Mode B — Sync / port from a source platform (从一端同步到多端)

1. Resolve targets and 真源 (the designated source platform).
2. Read the source platform's implementation of the feature.
3. **Lift to contract**: extract behavior, data model, edge cases; normalize
   platform quirks into shared behavior. This step is the most important — do
   not copy source-platform code into other platforms.
4. For each target platform:
   - Implement from the contract; record platform notes and any divergence.
   - Verify build/run; capture result.
5. If a target cannot match behavior exactly, record the divergence in the
   contract's Platform Notes and in the sync report; do not silently change the
   真源. Optionally reflect a by-design divergence back into the source platform.
6. Emit the sync report.

## Mode C — 真源迁移 / Re-baseline（source-of-truth migration）

当某个端（记为 B）后来领先于契约、成为事实上的新真源时，需要把"B 领先的部分"
正式提升（promote）进契约，并让其它端（A/C/D）追上，从而恢复"所有功能以契约为
最新真源"的状态。这也是"一开始 A 是真源、后来 B 是真源"场景的标准收口流程。

> **预防优于补救**：理想情况下不应长期以某个端为永久真源（见契约模板
> `feature-contract.md` 的"真源与溯源"原则）。Mode C 是已经陷入"端是真源"时的
> 回正流程；更优的做法是冷启动后尽快让契约接管，从此只维护契约。

步骤：
1. **确认新领先端 B**：与用户确认当前最新的端（B），并重申"契约永久真源"目标。
2. **抽取 B 的当前行为**：用 `drift_check.py --source B --axis <routes|api|model|i18n>`
   提取 B 已实现的屏幕 / 接口 / 模型 / 文案 key（见 `references/drift-check.md`）。
3. **与现有契约 diff**：对比 B 的实现与契约，识别 B 相对契约的净新增 / 变更。
4. **promote 进契约**：把 B 的变更写回 Behavior / Data Model / API / UI States /
   检查点；把该功能的 `source` 字段改为 `B`、`since` 设为今天；契约 `version` +1。
5. **生成各端追赶清单**：对 A/C/D 各端分别跑
   `drift_check.py --source B --axis ...`，得到"每端相对 B 还差什么"的清单。
6. **冲突裁决**：若 B 与某端对同一行为各自改了且不同，由人决定哪个是真，更新契约。
7. **执行追赶**：各端按新契约实现，并在 Platform Notes 记 `已实现版本`（如 `iOS: v2`）。
8. **漂移验证**：重跑 checkpoint 模式，矩阵里 A/C/D 不应再标 ✘ / 落后。
9. **同步报告**：记录迁移原因、promote 了什么、各端追赶项与结果。

## Per-platform implementation & verification tips

### iOS (Swift / SwiftUI)
- Patterns: SwiftUI views + ObservableObject/@Observable; Coordinators for
  navigation; async/await for I/O.
- Verification: `xcodebuild -scheme <Scheme> build` (or `xcodebuild test`).
- Notes: respect main-thread UI updates; use `Task`/`async let`; handle
  background/foreground lifecycle.

### Android (Kotlin)
- Patterns: Jetpack Compose or ViewBinding; ViewModel + StateFlow; Coroutines.
- Verification: `./gradlew assembleDebug` (or `./gradlew testDebugUnitTest`).
- Notes: lifecycle-aware observers; permission model; resource qualifiers.

### Flutter (Dart)
- Patterns: Stateless/Stateful widgets; Provider/Riverpod/Bloc for state;
  `Future`/`async-await`.
- Verification: `flutter analyze` then `flutter test`; `flutter build` for the
  target (apk/ipa/web).
- Notes: single codebase already covers iOS+Android+Web — implement once, then
  verify each target build.

### React (Web)
- Patterns: function components + hooks; context or a store (Redux/Zustand);
  TypeScript.
- Verification: `npm run build` / `npm test` (or `vite build`).
- Notes: routing (react-router); keep behavior in hooks/services, not in JSX.

### React Native
- Patterns: same React model; native modules only when required.
- Verification: `npx react-native run-ios` / `run-android`; `jest` for units.
- Notes: platform-specific files via `.ios.tsx` / `.android.tsx` only when needed.

### H5 / vanilla web
- Patterns: vanilla JS/TS or a light framework; Web Components where reusable.
- Verification: serve + smoke test; `vite build`.
- Notes: broad browser support; feature-detect rather than assume.

### WeChat Mini Program
- Patterns: `app.json` routes; `Page({})` + WXML/WXSS; `wx.*` APIs.
- Verification: WeChat DevTools build/preview; unit tests via miniprogram-simulate.
- Notes:受限 APIs (login, payment) require the WeChat runtime.

### Uni-app
- Patterns: Vue SFCs (`*.vue`) compiled to multiple platforms via
  `pages.json`; conditionals via `process.env.UNI_PLATFORM`.
- Verification: `npm run dev:%PLATFORM%` / `build:%PLATFORM%`.
- Notes: one codebase → many targets; verify each platform build separately.

## Reconciliation checklist

- [ ] Every acceptance scenario passes on every targeted platform.
- [ ] Divergences are recorded in the contract's Platform Notes and the report.
- [ ] No platform introduced behavior outside the contract's scope.
- [ ] Build/run verification captured per platform.
- [ ] Sync report written (`references/templates/sync-report.md`).
