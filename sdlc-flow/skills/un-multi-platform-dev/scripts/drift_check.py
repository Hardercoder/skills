#!/usr/bin/env python3
"""drift_check.py - detect cross-platform drift against a feature contract.

This is the deterministic half of the un-multi-platform-dev skill's "spec drift"
story. It never calls an LLM; it greps code and compares tokens so that drift
shows up in CI or on demand, and it produces a report the AI reconciliation
step can consume to reverse-sync the contract when code leads.

Two modes:

  checkpoint  (contract-driven, recommended)
      Reads structured "checkpoints" from a contract markdown file and greps
      each platform's code for the expected symbols. Produces a
      feature x platform coverage matrix (present / absent per platform).

  symbol      (code-driven, heuristic, low-confidence)
      Extracts route / screen / public-symbol tokens from each platform and
      reports tokens present in some but not all comparable platforms - a
      best-effort drift signal - and emits a "suggested checkpoints" YAML
      block you can paste into the contract to bootstrap ongoing checks.

Mode `auto` (default) picks checkpoint when a parseable contract is given,
otherwise symbol.

Usage:
    python3 drift_check.py --workspace <ws> [--platform NAME:PATH ...]
                           [--contract <md>] [--mode auto|checkpoint|symbol]
                           [--report <md>] [--json]

Platform names: ios, android, flutter, react_native, react_web, vue_web,
h5_web, wechat_mp, uniapp.
"""
import argparse
import json
import os
import re
import sys

# --- reuse platform detection from the sibling script ----------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import detect_platforms as _det
    DISPLAY = _det.DISPLAY
    _scan = _det.scan
    _CONF = _det.CONFIDENCE
except Exception:  # pragma: no cover - fallback if detect script missing
    DISPLAY = {
        'ios': 'iOS', 'android': 'Android', 'flutter': 'Flutter',
        'react_native': 'React Native', 'react_web': 'React (Web)',
        'vue_web': 'Vue (Web)', 'h5_web': 'H5 / Web',
        'wechat_mp': 'WeChat Mini Program', 'uniapp': 'Uni-app',
    }
    _CONF = {k: 'medium' for k in DISPLAY}
    _scan = None

PLATFORM_KEYS = set(DISPLAY.keys())

IGNORE_DIRS = {
    '.git', 'node_modules', 'Pods', 'build', 'dist', '.next', '.gradle',
    '.idea', 'vendor', 'DerivedData', '.venv', 'venv', '__pycache__',
    'Carthage', '.build', 'Pods', '.dart_tool', 'coverage', '.cache',
}

TEXT_EXT = {
    '.swift', '.m', '.mm', '.h', '.java', '.kt', '.kts', '.dart', '.js',
    '.jsx', '.ts', '.tsx', '.vue', '.py', '.rb', '.go', '.rs', '.c', '.cpp',
    '.cs', '.html', '.wxml', '.wxss', '.css', '.scss', '.json', '.yaml',
    '.yml', '.xml', '.gradle', '.md', '.toml',
}

# Platforms whose "surface" is route / screen string tokens (comparable).
ROUTE_PLATFORMS = {
    'flutter', 'react_web', 'react_native', 'vue_web', 'h5_web',
    'wechat_mp', 'uniapp',
}

# Per-platform public-symbol extractors (best-effort, for the symbol inventory).
SYMBOL_PATTERNS = {
    'ios': [r'\bfunc\s+([A-Za-z_]\w*)', r'\bclass\s+([A-Za-z_]\w*)',
            r'\bstruct\s+([A-Za-z_]\w*)', r'@interface\s+([A-Za-z_]\w*)'],
    'android': [r'\bfun\s+([A-Za-z_]\w*)', r'\bclass\s+([A-Za-z_]\w*)',
                r'\binterface\s+([A-Za-z_]\w*)', r'\bobject\s+([A-Za-z_]\w*)'],
    'flutter': [r'\bclass\s+([A-Za-z_]\w*)', r'\bmixin\s+([A-Za-z_]\w*)',
                r'\benum\s+([A-Za-z_]\w*)', r'\bextension\s+([A-Za-z_]\w*)'],
    'react_web': [r'\bexport\s+(?:default\s+)?(?:function|const|class)\s+([A-Za-z_]\w*)',
                  r'\bfunction\s+([A-Za-z_]\w*)', r'<([A-Z][A-Za-z_]\w*)\b'],
    'react_native': [r'\bexport\s+(?:default\s+)?(?:function|const|class)\s+([A-Za-z_]\w*)',
                     r'\bfunction\s+([A-Za-z_]\w*)', r'<([A-Z][A-Za-z_]\w*)\b'],
    'vue_web': [r'\bname:\s*[\'"]([A-Za-z_]\w*)[\'"]'],
    'h5_web': [r'\bfunction\s+([A-Za-z_]\w*)', r'\bconst\s+([A-Za-z_]\w*)\s*=',
               r'<([A-Z][A-Za-z_]\w*)\b'],
    'wechat_mp': [r'\b(\w+):\s*function\b'],
    'uniapp': [r'\bname:\s*[\'"]([A-Za-z_]\w*)[\'"]'],
}


# --------------------------------------------------------------------------
# Platform resolution
# --------------------------------------------------------------------------
def resolve_platforms(args):
    """Return dict name -> list of root paths."""
    explicit = {}
    for spec in args.platform or []:
        if ':' not in spec:
            sys.stderr.write(f'--platform must be NAME:PATH, got: {spec}\n')
            sys.exit(2)
        name, path = spec.split(':', 1)
        name = name.strip()
        path = os.path.abspath(path.strip())
        if name not in PLATFORM_KEYS:
            sys.stderr.write(f'Unknown platform "{name}". '
                             f'Known: {", ".join(sorted(PLATFORM_KEYS))}\n')
            sys.exit(2)
        if not os.path.isdir(path):
            sys.stderr.write(f'Not a directory: {path}\n')
            sys.exit(2)
        explicit.setdefault(name, []).append(path)

    if explicit:
        return explicit

    ws = os.path.abspath(args.workspace or '.')
    if not os.path.isdir(ws):
        sys.stderr.write(f'Not a directory: {ws}\n')
        sys.exit(2)
    if _scan is None:
        sys.stderr.write('No --platform given and detection unavailable.\n')
        sys.exit(2)
    raw = _scan(ws)
    result = {}
    for plat, info in raw.items():
        result[plat] = sorted(set(info['roots']), key=lambda p: (p.count(os.sep), p))
    return result


# --------------------------------------------------------------------------
# Grep helper
# --------------------------------------------------------------------------
def _is_textish(path):
    return os.path.splitext(path)[1].lower() in TEXT_EXT


def grep_root(root, pattern, cap_hits=50):
    """Return (found, sample) where sample is (relpath, lineno) or None."""
    try:
        rx = re.compile(pattern)
    except re.error as e:
        return (False, ('BAD_REGEX', str(e)))
    hits = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for fn in files:
            p = os.path.join(dirpath, fn)
            if not _is_textish(p):
                continue
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                    for i, line in enumerate(fh):
                        if rx.search(line):
                            hits.append((os.path.relpath(p, root), i + 1))
                            break
            except OSError:
                continue
            if len(hits) >= cap_hits:
                break
        if len(hits) >= cap_hits:
            break
    if not hits:
        return (False, None)
    return (True, hits[0])


def extract_tokens(root, patterns):
    """Return a set of symbols matched by the given regex list across root."""
    found = set()
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for fn in files:
            p = os.path.join(dirpath, fn)
            if not _is_textish(p):
                continue
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                    text = fh.read()
            except OSError:
                continue
            for pat in patterns:
                for m in re.finditer(pat, text):
                    tok = m.group(1)
                    if tok:
                        found.add(tok)
    return found


# --------------------------------------------------------------------------
# Checkpoint parsing
# --------------------------------------------------------------------------
def _find_checkpoint_block(md_text):
    """Locate the fenced ```yaml block under a Checkpoints heading (or first
    yaml block). Returns the yaml source string, or None."""
    lines = md_text.splitlines()
    target = None
    for i, ln in enumerate(lines):
        if re.match(r'^#{1,6}\s*.*(检查点|Checkpoint|checkpoint).*$', ln):
            target = i
            break
    if target is None:
        target = 0
    in_block = False
    buf = []
    for ln in lines[target:]:
        if ln.strip().startswith('```'):
            if not in_block:
                # opening fence; only capture yaml/yml/unknown-language blocks
                lang = ln.strip()[3:].strip().lower()
                in_block = lang in ('yaml', 'yml', '')
                continue
            # closing fence of the captured block
            return '\n'.join(buf) if buf else None
        if in_block:
            buf.append(ln)
    return None


def _strip_quotes(v):
    v = v.strip()
    if len(v) >= 2 and v[0] in '"\'' and v[-1] == v[0]:
        return v[1:-1]
    return v


def parse_checkpoints(md_text):
    """Parse the checkpoint block. Returns (checkpoints, default_match, errors).

    Supported (flat) YAML subset - no nesting required:
        default_match: "login"
        checkpoints:
          - id: user-login
            desc: 用户登录入口
            match.ios: "LoginManager"
            match.android: "LoginRepository"
    Uses PyYAML when available; otherwise a minimal line parser for this subset.
    """
    block = _find_checkpoint_block(md_text)
    if not block:
        return ([], None, ['No checkpoint yaml block found under a '
                           '"检查点/Checkpoint" heading.'])

    # Prefer PyYAML.
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(block)
        if not isinstance(data, dict):
            raise ValueError('top-level must be a mapping')
        default_match = data.get('default_match')
        raw_list = data.get('checkpoints') or []
        cps = []
        for item in raw_list:
            if not isinstance(item, dict):
                continue
            cps.append({
                'id': str(item.get('id', '')),
                'desc': str(item.get('desc', '')),
                'match': {k: str(v) for k, v in (item.get('match') or {}).items()},
            })
        return (cps, default_match, [])
    except Exception:
        pass  # fall back to minimal parser

    # Minimal parser for the documented flat subset.
    checkpoints = []
    default_match = None
    current = None
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        m = re.match(r'^\s*-\s*id:\s*(.+)$', line)
        if m:
            current = {'id': _strip_quotes(m.group(1)), 'desc': '', 'match': {}}
            checkpoints.append(current)
            continue
        km = re.match(r'^([\w.]+):\s?(.*)$', line.strip())
        if not km:
            continue
        key, val = km.group(1), km.group(2)
        if key == 'default_match':
            default_match = _strip_quotes(val)
        elif key == 'checkpoints':
            continue
        elif current is not None:
            if key == 'desc':
                current['desc'] = _strip_quotes(val)
            elif key.startswith('match.'):
                plat = key[len('match.'):]
                current['match'][plat] = _strip_quotes(val)
    return (checkpoints, default_match, [])


# --------------------------------------------------------------------------
# Modes
# --------------------------------------------------------------------------
def run_checkpoint(platforms, contract_text):
    checkpoints, default_match, errors = parse_checkpoints(contract_text)
    if errors:
        return {'mode': 'checkpoint', 'errors': errors, 'matrix': []}
    matrix = []
    for cp in checkpoints:
        if not cp['id']:
            continue
        row = {'id': cp['id'], 'desc': cp['desc'], 'cells': {}}
        for name, roots in platforms.items():
            pat = (cp['match'].get(name)
                   or cp['match'].get('*')
                   or default_match
                   or cp['id'])
            found_any = False
            sample = None
            bad = None
            for r in roots:
                ok, smp = grep_root(r, pat)
                if ok is False and isinstance(smp, tuple) and smp[0] == 'BAD_REGEX':
                    bad = smp[1]
                    continue
                if ok:
                    found_any = True
                    sample = smp
                    break
            if bad:
                row['cells'][name] = {'status': 'error', 'pattern': pat,
                                      'detail': bad}
            else:
                row['cells'][name] = {
                    'status': 'present' if found_any else 'absent',
                    'pattern': pat,
                    'sample': sample,
                }
        matrix.append(row)
    return {'mode': 'checkpoint', 'errors': errors, 'matrix': matrix,
            'default_match': default_match}


def _route_tokens(root):
    """Collect route / screen string tokens from a platform root."""
    toks = set()
    rx = re.compile(r'["\'`]([/A-Za-z0-9_\-]+)["\'`]')
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for fn in files:
            p = os.path.join(dirpath, fn)
            if not _is_textish(p):
                continue
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                    text = fh.read()
            except OSError:
                continue
            for m in rx.finditer(text):
                t = m.group(1)
                if not t.startswith('/') and '/' not in t:
                    continue
                if '.' in t:  # skip asset/extension paths
                    continue
                segs = [s for s in t.strip('/').split('/') if s]
                if len(segs) < 1:
                    continue
                if any(s.lower() in ('assets', 'images', 'img', 'fonts',
                                     'static', 'css', 'js', 'dist', 'node_modules',
                                     'lib', 'build') for s in segs):
                    continue
                toks.add(t)
    return toks


def run_symbol(platforms):
    """Route/screen parity across comparable platforms + suggested checkpoints.

    Screens are compared on their LEAF segment (e.g. `/settings` and
    `pages/settings/settings` both collapse to `settings`) so the same screen
    is recognized across platforms that name routes differently.
    """
    comparable = {n: rs for n, rs in platforms.items() if n in ROUTE_PLATFORMS}
    if not comparable:
        return {'mode': 'symbol',
                'note': 'No route-comparable platforms detected '
                        '(web/Flutter/RN/WeChat/Uni-app). Symbol mode needs at '
                        'least two of those.',
                'leaf_map': {}, 'drift': [], 'suggested': []}
    # leaf -> platform -> set(raw tokens)
    leaf_map = {}
    for name, roots in comparable.items():
        raw = set()
        for r in roots:
            raw |= _route_tokens(r)
        for t in raw:
            leaf = t.strip('/').split('/')[-1]
            leaf_map.setdefault(leaf, {}).setdefault(name, set()).add(t)

    names = list(comparable.keys())
    drift = []
    for leaf, by_plat in leaf_map.items():
        present = set(by_plat.keys())
        missing = set(names) - present
        if missing:
            drift.append({
                'leaf': leaf,
                'present_in': sorted(present),
                'missing_in': sorted(missing),
                'tokens': {p: sorted(v) for p, v in by_plat.items()},
            })
    drift.sort(key=lambda d: (len(d['missing_in']), d['leaf']), reverse=True)

    # Suggested checkpoints (reverse-sync aid): one per screen, with the
    # per-platform regex alternation of the raw tokens that represent it.
    suggested = []
    for leaf, by_plat in leaf_map.items():
        match = {p: '|'.join(re.escape(t) for t in sorted(toks))
                 for p, toks in by_plat.items()}
        suggested.append({
            'id': re.sub(r'[^a-z0-9]+', '-', leaf.lower()).strip('-') or 'route',
            'desc': f'路由/页面: {leaf}',
            'match': match,
        })
    return {'mode': 'symbol', 'leaf_map': {k: {p: sorted(v) for p, v in pl.items()}
                                           for k, pl in leaf_map.items()},
            'drift': drift, 'suggested': suggested, 'platforms': names}


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
def render_console(result, platforms):
    lines = []
    if result.get('mode') == 'checkpoint':
        if result.get('errors'):
            lines.append('ERRORS:')
            for e in result['errors']:
                lines.append(f'  - {e}')
            return '\n'.join(lines)
        names = sorted(platforms.keys(), key=lambda p: DISPLAY.get(p, p))
        header = 'checkpoint'.ljust(22) + ''.join(DISPLAY.get(n, n)[:6].ljust(8) for n in names)
        lines.append(header)
        lines.append('-' * len(header))
        for row in result['matrix']:
            cells = ''.join(
                ('OK  ' if row['cells'].get(n, {}).get('status') == 'present'
                 else 'MISS' if row['cells'].get(n, {}).get('status') == 'absent'
                 else 'ERR ').ljust(8) for n in names)
            lines.append(row['id'][:22].ljust(22) + cells)
        n_miss = sum(1 for row in result['matrix']
                     for n in names if row['cells'].get(n, {}).get('status') == 'absent')
        lines.append(f'\n{len(result["matrix"])} checkpoints x {len(names)} platforms; '
                     f'{n_miss} absent (drift) cells.')
    else:
        note = result.get('note')
        if note:
            lines.append(note)
            return '\n'.join(lines)
        lines.append(f'Symbol mode (route parity) across: {", ".join(result.get("platforms", []))}')
        if result.get('drift'):
            lines.append(f'\nDrift candidates ({len(result["drift"])}): screen present in some, missing in others')
            for d in result['drift'][:30]:
                lines.append(f'  {d["leaf"]}  missing in: {", ".join(DISPLAY.get(x, x) for x in d["missing_in"])}')
        else:
            lines.append('\nNo screen drift detected across comparable platforms.')
        lines.append(f'\nSuggested checkpoints for reverse-sync: {len(result.get("suggested", []))} (see report/JSON).')
    return '\n'.join(lines)


def render_markdown(result, platforms):
    out = ['# Drift Check Report', '']
    mode = result.get('mode')
    if mode == 'checkpoint':
        if result.get('errors'):
            out.append('## Errors')
            for e in result['errors']:
                out.append(f'- {e}')
            return '\n'.join(out)
        names = sorted(platforms.keys(), key=lambda p: DISPLAY.get(p, p))
        out.append(f'Mode: **checkpoint** (contract-driven). '
                   f'{len(result["matrix"])} checkpoints x {len(names)} platforms.')
        out.append('')
        out.append('| Checkpoint | ' + ' | '.join(DISPLAY.get(n, n) for n in names) + ' |')
        out.append('|' + '---|' * (len(names) + 1))
        for row in result['matrix']:
            cells = []
            for n in names:
                c = row['cells'].get(n, {})
                if c.get('status') == 'present':
                    smp = c.get('sample')
                    cells.append('✔' + (f' `{smp[0]}:{smp[1]}`' if smp else ''))
                elif c.get('status') == 'absent':
                    cells.append('✘ (absent)')
                else:
                    cells.append('⚠ err')
            out.append(f'| {row["id"]} | ' + ' | '.join(cells) + ' |')
        out.append('')
        out.append('> ✘ = expected symbol not found in that platform -> likely drift. '
                   'Update the contract or the code, then re-run.')
    else:
        out.append(f'Mode: **symbol** (code-driven, low-confidence heuristic).')
        note = result.get('note')
        if note:
            out.append('')
            out.append(f'_{note}_')
            return '\n'.join(out)
        out.append('')
        out.append(f'Comparable platforms: {", ".join(result.get("platforms", []))}')
        out.append('')
        out.append('## Drift candidates')
        out.append('Screens present in some platforms but missing in others '
                   '(normalized to the leaf screen segment):')
        out.append('')
        if result.get('drift'):
            out.append('| Screen | Present in | Missing in | Example tokens |')
            out.append('|--------|-----------|-----------|----------------|')
            for d in result['drift']:
                ex = '; '.join(f'{DISPLAY.get(p, p)}: ' + '/'.join(t[:40] for t in toks)
                               for p, toks in d['tokens'].items())
                out.append(f'| `{d["leaf"]}` | '
                           + ', '.join(DISPLAY.get(x, x) for x in d['present_in']) + ' | '
                           + ', '.join(DISPLAY.get(x, x) for x in d['missing_in']) + ' | '
                           + ex + ' |')
        else:
            out.append('_No screen drift detected across comparable platforms._')
        out.append('')
        out.append('## Suggested checkpoints (reverse-sync aid)')
        out.append('Paste into the contract under `## 检查点` to bootstrap ongoing checks:')
        out.append('')
        out.append('```yaml')
        out.append('checkpoints:')
        for s in result.get('suggested', []):
            out.append(f'  - id: {s["id"]}')
            out.append(f'    desc: {s["desc"]}')
            for n, pat in s['match'].items():
                out.append(f'    match.{n}: "{pat}"')
        out.append('```')
    return '\n'.join(out)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description='Detect cross-platform drift vs a contract.')
    ap.add_argument('--workspace', default='.', help='Workspace to scan for platforms')
    ap.add_argument('--platform', action='append',
                    help='NAME:PATH explicit platform root (repeatable)')
    ap.add_argument('--contract', help='Path to the feature contract markdown')
    ap.add_argument('--mode', choices=['auto', 'checkpoint', 'symbol'], default='auto')
    ap.add_argument('--report', help='Write the markdown report to this path')
    ap.add_argument('--json', action='store_true', help='Emit JSON')
    args = ap.parse_args()

    platforms = resolve_platforms(args)
    if not platforms:
        sys.stderr.write('No platforms resolved. Provide --platform or a scannable --workspace.\n')
        sys.exit(2)

    mode = args.mode
    contract_text = None
    if args.contract:
        try:
            with open(args.contract, encoding='utf-8') as fh:
                contract_text = fh.read()
        except OSError as e:
            sys.stderr.write(f'Cannot read contract: {e}\n')
            sys.exit(2)

    if mode == 'auto':
        mode = 'checkpoint' if (contract_text and parse_checkpoints(contract_text)[0]) else 'symbol'

    if mode == 'checkpoint':
        if not contract_text:
            sys.stderr.write('checkpoint mode requires --contract.\n')
            sys.exit(2)
        result = run_checkpoint(platforms, contract_text)
    else:
        result = run_symbol(platforms)

    result['platforms'] = {n: roots for n, roots in platforms.items()}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_console(result, platforms))

    if args.report:
        with open(args.report, 'w', encoding='utf-8') as fh:
            fh.write(render_markdown(result, platforms))
        sys.stderr.write(f'\nReport written to: {args.report}\n')


if __name__ == '__main__':
    main()
