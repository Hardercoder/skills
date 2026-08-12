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
