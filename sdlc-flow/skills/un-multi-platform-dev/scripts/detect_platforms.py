#!/usr/bin/env python3
"""detect_platforms.py - discover client platforms in a workspace.

Scans <workspace> for project markers and reports which platforms (iOS,
Android, Flutter, React Native, React Web, Vue Web, H5/Web, WeChat Mini
Program, Uni-app) are present, their root directory, confidence, and the
markers that matched. Used by the un-multi-platform-dev skill to resolve target
platforms without guessing.

Usage:
    python3 detect_platforms.py <workspace> [--json]
"""
import argparse
import json
import os
import re
import sys

IGNORE_DIRS = {
    '.git', 'node_modules', 'Pods', 'build', 'dist', '.next', '.gradle',
    '.idea', 'vendor', 'DerivedData', '.venv', 'venv', '__pycache__',
    'Carthage', '.build',
}
MAX_DEPTH = 8

DISPLAY = {
    'ios': 'iOS',
    'android': 'Android',
    'flutter': 'Flutter',
    'react_native': 'React Native',
    'react_web': 'React (Web)',
    'vue_web': 'Vue (Web)',
    'h5_web': 'H5 / Web',
    'wechat_mp': 'WeChat Mini Program',
    'uniapp': 'Uni-app',
}
CONFIDENCE = {
    'ios': 'high', 'android': 'high', 'flutter': 'high',
    'react_native': 'high', 'wechat_mp': 'high', 'uniapp': 'high',
    'react_web': 'medium-high', 'vue_web': 'medium-high', 'h5_web': 'medium',
}

FLUTTER_RE = re.compile(r'^\s*flutter:\s*(sdk|\n|$)', re.M)


def _package_json_platform(path):
    """Return a platform key based on package.json dependencies, or None."""
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception:
        return None
    deps = {}
    for key in ('dependencies', 'devDependencies', 'peerDependencies'):
        deps.update(data.get(key, {}))
    if 'react-native' in deps:
        return 'react_native'
    if '@dcloudio/uni-app' in deps:
        return 'uniapp'
    if 'vue' in deps:
        return 'vue_web'
    if 'react' in deps:
        return 'react_web'
    return None


def detect_dir(dirpath):
    """Return dict platform_key -> list of marker strings found in dirpath."""
    found = {}
    try:
        entries = os.listdir(dirpath)
    except OSError:
        return found

    # iOS
    ios_markers = [e for e in entries
                   if e.endswith('.xcodeproj') or e.endswith('.xcworkspace')]
    for f in ('Podfile', 'Package.swift', 'Cartfile'):
        if f in entries:
            ios_markers.append(f)
    if ios_markers:
        found['ios'] = ios_markers

    # Android
    android_markers = [f for f in ('settings.gradle', 'settings.gradle.kts',
                                   'build.gradle', 'build.gradle.kts',
                                   'AndroidManifest.xml', 'gradlew') if f in entries]
    if android_markers:
        found['android'] = android_markers

    # Flutter
    if 'pubspec.yaml' in entries:
        try:
            with open(os.path.join(dirpath, 'pubspec.yaml'), encoding='utf-8') as fh:
                txt = fh.read()
            if FLUTTER_RE.search(txt):
                found['flutter'] = ['pubspec.yaml']
        except OSError:
            pass

    # package.json based
    pj_platform = None
    if 'package.json' in entries:
        pj_platform = _package_json_platform(os.path.join(dirpath, 'package.json'))
    if pj_platform == 'react_native':
        found['react_native'] = ['package.json (react-native)']
    elif pj_platform == 'vue_web':
        found['vue_web'] = ['package.json (vue)']
    elif pj_platform == 'react_web':
        found['react_web'] = ['package.json (react)']

    # Uni-app via package.json or pages.json + manifest.json
    if pj_platform == 'uniapp':
        found['uniapp'] = found.get('uniapp', []) + ['package.json (@dcloudio/uni-app)']
    if 'pages.json' in entries and 'manifest.json' in entries:
        found['uniapp'] = found.get('uniapp', []) + ['pages.json + manifest.json']

    # WeChat Mini Program
    if 'app.json' in entries:
        markers = ['app.json']
        if 'project.config.json' in entries:
            markers.append('project.config.json')
        found['wechat_mp'] = markers

    # H5 / vanilla web (only when not already a framework web project)
    if ('index.html' in entries or 'vite.config.ts' in entries
            or 'vite.config.js' in entries):
        if not any(k in found for k in ('react_web', 'vue_web', 'react_native')):
            h5 = []
            if 'index.html' in entries:
                h5.append('index.html')
            if 'vite.config.ts' in entries:
                h5.append('vite.config.ts')
            if 'vite.config.js' in entries:
                h5.append('vite.config.js')
            found['h5_web'] = h5

    return found


def scan(workspace):
    results = {}  # platform_key -> {'roots': [dirs], 'markers': set}
    for root, dirs, _files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        depth = root[len(workspace):].count(os.sep)
        if depth > MAX_DEPTH:
            dirs[:] = []
            continue
        for plat, markers in detect_dir(root).items():
            entry = results.setdefault(plat, {'roots': [], 'markers': set()})
            entry['roots'].append(root)
            entry['markers'].update(markers)
    return results


def main():
    ap = argparse.ArgumentParser(description='Detect client platforms in a workspace.')
    ap.add_argument('workspace', nargs='?', default='.', help='Workspace path to scan')
    ap.add_argument('--json', action='store_true', help='Emit JSON instead of a table')
    args = ap.parse_args()

    ws = os.path.abspath(args.workspace)
    if not os.path.isdir(ws):
        sys.stderr.write(f'Not a directory: {ws}\n')
        sys.exit(2)

    raw = scan(ws)
    platforms = {}
    for plat, info in raw.items():
        roots = sorted(set(info['roots']), key=lambda p: (p.count(os.sep), p))
        platforms[plat] = {
            'display': DISPLAY.get(plat, plat),
            'root': roots[0],
            'all_roots': roots,
            'confidence': CONFIDENCE.get(plat, 'medium'),
            'markers': sorted(info['markers']),
        }

    if args.json:
        print(json.dumps({'workspace': ws, 'platforms': platforms},
                         ensure_ascii=False, indent=2))
        return

    if not platforms:
        print(f'No recognized client platforms found in:\n  {ws}')
        print('Scanned for: iOS, Android, Flutter, React Native, React/Vue Web, '
              'H5, WeChat Mini Program, Uni-app.')
        return

    print(f'Detected platforms in:\n  {ws}\n')
    header = f'{"Platform":<22} {"Confidence":<12} {"Root":<42} Markers'
    print(header)
    print('-' * len(header))
    for plat in sorted(platforms, key=lambda p: DISPLAY.get(p, p)):
        rec = platforms[plat]
        extra = f' (+{len(rec["all_roots"]) - 1} more)' if len(rec['all_roots']) > 1 else ''
        root = rec['root'] + extra
        print(f'{rec["display"]:<22} {rec["confidence"]:<12} {root:<42} {", ".join(rec["markers"])}')
    print('\nNote: auto-detection may include platforms not relevant to this change. '
          'Confirm the target set with the user.')


if __name__ == '__main__':
    main()
