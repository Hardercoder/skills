# Platform Detection Reference

This document defines how to recognize each supported client platform from a
workspace, and how to resolve ambiguous cases. The `scripts/detect_platforms.py`
script encodes these rules; this file is the human/agent-readable spec used when
the script is unavailable or its output needs interpretation.

## Supported platforms & markers

| Platform | Primary marker(s) | Confidence |
|----------|-------------------|------------|
| **iOS** | `*.xcodeproj` or `*.xcworkspace` (dir), `Podfile`, `Package.swift`, `Cartfile` | high |
| **Android** | `settings.gradle` / `settings.gradle.kts`, `build.gradle` / `build.gradle.kts` at project root, `AndroidManifest.xml`, `gradlew` | high |
| **Flutter** | `pubspec.yaml` containing a `flutter:` dependency | high |
| **React Native** | `package.json` with `react-native` in `dependencies`/`devDependencies` | high |
| **React Web** | `package.json` with `react` (and **not** `react-native`) plus a web bundler (`vite`/`webpack`/`next`) or `src/` | medium-high |
| **Vue Web** | `package.json` with `vue` (and not `react-native`) | medium-high |
| **H5 / vanilla web** | `index.html` at root, `vite.config.ts`/`vite.config.js`, or a plain HTML/JS project with no framework | medium |
| **WeChat Mini Program** | `app.json` (+ `project.config.json`) | high |
| **Uni-app** | `pages.json` + `manifest.json`, or `package.json` with `@dcloudio/uni-app` | high |
| **HarmonyOS / 鸿蒙** | `oh-package.json5` at root, `build-profile.json5`, `module.json5`, or any `*.ets` source (ArkTS) | high |

## Conflict resolution

- **React Native vs React Web vs Vue**: a `package.json` may match several. Check
  in this priority order — `react-native` → `vue` → `react` (web). Do not label a
  React Native project as React Web just because `react` is present.
- **H5 vs framework web**: if both `index.html` and a framework marker exist,
  prefer the framework label but still note the web root; treat "Web" as the
  umbrella and record the framework subtype.
- **Monorepos**: a single repository can host several platforms (e.g. `apps/ios`,
  `apps/android`, `packages/ui`). Report each platform root separately; do not
  assume one root = one platform.
- **Multiple build systems**: an Android project may also contain a `package.json`
  for JS tooling. Report Android as the platform and ignore the incidental web
  marker unless the user wants web too.

## Directories to ignore while scanning

Skip these to avoid false positives and slow scans: `node_modules`, `.git`,
`Pods`, `build`, `dist`, `.next`, `.gradle`, `.idea`, `vendor`, `DerivedData`,
`*.xcassets` (inside an iOS project, not a root marker), `oh_modules` (HarmonyOS
dependency cache), `.hvigor` (HarmonyOS build cache).

## Using the detector

```bash
python3 scripts/detect_platforms.py /path/to/workspace
python3 scripts/detect_platforms.py /path/to/workspace --json
```

Human-readable output prints a table of detected platforms, their root
directory, confidence, and the markers matched. `--json` emits the same as
machine-readable JSON for programmatic use.

After detection, always **confirm the target set with the user** — auto-detection
may find platforms they do not want to touch in this change.
