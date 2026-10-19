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
      Also reads each checkpoint's `source` / `since` provenance fields and
      surfaces them so you can see which platform is the current truth for
      each feature.

  symbol      (code-driven, heuristic, low-confidence)
      Extracts tokens from each platform along a chosen AXIS and reports
      tokens present in some but not all comparable platforms - a
      best-effort drift signal - and emits a "suggested checkpoints" YAML
      block you can paste into the contract to bootstrap ongoing checks.

      Axis (--axis):
        routes  screen / route strings (default; only web/Flutter/RN/WeChat/
                Uni-app are comparable - native iOS/Android UI is not strings)
        api     API endpoint path tokens (all platforms comparable)
        model   data-model / entity / field names (all platforms comparable)
        i18n    internationalization string keys (all platforms comparable)

Mode `auto` (default) picks checkpoint when a parseable contract is given,
otherwise symbol.

`--source PLATFORM` (symbol mode): treat the named platform as the temporary
truth and report how far every other platform lags it (the source-of-truth
migration / catch-up view). Combine with --axis to focus the comparison.

Usage:
    python3 drift_check.py --workspace <ws> [--platform NAME:PATH ...]
                           [--contract <md>] [--mode auto|checkpoint|symbol]
                           [--axis routes|api|model|i18n]
                           [--source <platform>]
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
        version = data.get('version')
        raw_list = data.get('checkpoints') or []
        cps = []
        for item in raw_list:
            if not isinstance(item, dict):
                continue
            cps.append({
                'id': str(item.get('id', '')),
                'desc': str(item.get('desc', '')),
                'source': str(item['source']) if item.get('source') else '',
                'since': str(item.get('since', '')),
                'match': {k: str(v) for k, v in (item.get('match') or {}).items()},
            })
        return (cps, default_match, [], version)
    except Exception:
        pass  # fall back to minimal parser

    # Minimal parser for the documented flat subset.
    checkpoints = []
    default_match = None
    version = None
    current = None
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        m = re.match(r'^\s*-\s*id:\s*(.+)$', line)
        if m:
            current = {'id': _strip_quotes(m.group(1)), 'desc': '',
                       'source': '', 'since': '', 'match': {}}
            checkpoints.append(current)
            continue
        km = re.match(r'^([\w.]+):\s?(.*)$', line.strip())
        if not km:
            continue
        key, val = km.group(1), km.group(2)
        if key == 'default_match':
            default_match = _strip_quotes(val)
        elif key == 'version':
            version = _strip_quotes(val)
        elif key == 'checkpoints':
            continue
        elif current is not None:
            if key == 'desc':
                current['desc'] = _strip_quotes(val)
            elif key == 'source':
                current['source'] = _strip_quotes(val)
            elif key == 'since':
                current['since'] = _strip_quotes(val)
            elif key.startswith('match.'):
                plat = key[len('match.'):]
                current['match'][plat] = _strip_quotes(val)
    return (checkpoints, default_match, [], version)


# --------------------------------------------------------------------------
# Modes
# --------------------------------------------------------------------------
def run_checkpoint(platforms, contract_text):
    checkpoints, default_match, errors, version = parse_checkpoints(contract_text)
    if errors:
        return {'mode': 'checkpoint', 'errors': errors, 'matrix': [],
                'version': None}
    matrix = []
    for cp in checkpoints:
        if not cp['id']:
            continue
        row = {'id': cp['id'], 'desc': cp['desc'],
               'source': cp.get('source', ''), 'since': cp.get('since', ''),
               'cells': {}}
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
            'default_match': default_match, 'version': version}


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


def _api_tokens(root):
    """API endpoint path tokens: quoted paths that look like REST endpoints
    (>=2 segments, exclude asset dirs and file paths)."""
    toks = set()
    rx = re.compile(r'["\'`](/[A-Za-z0-9_/:.\-{}]+)["\'`]')
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
                if '.' in t:  # skip file paths like /foo/bar.png
                    continue
                segs = [s for s in t.strip('/').split('/') if s]
                if len(segs) < 2:
                    continue
                if any(s.lower() in ('assets', 'images', 'img', 'fonts',
                                     'static', 'css', 'js', 'dist', 'node_modules',
                                     'lib', 'build') for s in segs):
                    continue
                toks.add(t)
    return toks


def _model_tokens(root):
    """Best-effort entity / field names from class/struct/data-class defs."""
    toks = set()
    pats = [
        r'\b(?:class|struct|data class|interface|enum|typealias|protocol)\s+([A-Za-z_]\w*)',
        r'(?:var|val|let)\s+([A-Za-z_]\w*)',
        r'@property\s+(?:\([^)]*\)\s*)?(?:weak\s+|strong\s+)?(?:IBOutlet\s+)?([A-Za-z_]\w*)',
    ]
    rxs = [re.compile(p) for p in pats]
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
            for rx in rxs:
                for m in rx.finditer(text):
                    toks.add(m.group(1))
    return toks


def _i18n_tokens(root):
    """Best-effort i18n string keys from t()/NSLocalizedString/R.string/arb/json."""
    toks = set()
    pats = [
        r'\b(?:t|trans|i18n\.t|useTranslation|translate)\s*\(\s*[\'"]([A-Za-z0-9_.\-]+)[\'"]',
        r'NSLocalizedString\s*\(\s*@?[\'"]?([A-Za-z0-9_.\-]+)[\'"]?',
        r'\bR\.(?:string|plurals)\.([A-Za-z0-9_.\-]+)',
        r'\bLocalizedString\s*\(\s*[\'"]([A-Za-z0-9_.\-]+)[\'"]',
    ]
    rxs = [re.compile(p) for p in pats]
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
            for rx in rxs:
                for m in rx.finditer(text):
                    toks.add(m.group(1))
            low = fn.lower()
            if low.endswith(('.json', '.arb', '.strings')):
                for km in re.finditer(r'^\s*["\']?([A-Za-z0-9_.\-]+)["\']?\s*[:=]', text, re.M):
                    toks.add(km.group(1))
    return toks


def extract_axis(root, axis):
    """Dispatch token extraction by axis (routes | api | model | i18n)."""
    if axis == 'api':
        return _api_tokens(root)
    if axis == 'model':
        return _model_tokens(root)
    if axis == 'i18n':
        return _i18n_tokens(root)
    return _route_tokens(root)  # default routes


def run_symbol(platforms, axis='routes', source=None):
    """Token parity across comparable platforms (axis) + optional lag vs source.

    For axis=api/model/i18n every platform is comparable (native iOS/Android
    APIs/models/strings count). For axis=routes only web/Flutter/RN/WeChat/Uni-app
    are comparable. Screens/paths are normalized to the LEAF segment so the same
    screen is recognized across platforms that name routes differently.
    """
    comparable = {n: rs for n, rs in platforms.items() if n in ROUTE_PLATFORMS}
    if axis in ('api', 'model', 'i18n'):
        comparable = dict(platforms)  # all platforms comparable on these axes
    if not comparable:
        return {'mode': 'symbol',
                'note': f'No comparable platforms detected for axis={axis}.',
                'axis': axis, 'leaf_map': {}, 'drift': [], 'suggested': [],
                'lag': {}}
    leaf_map = {}
    for name, roots in comparable.items():
        raw = set()
        for r in roots:
            raw |= extract_axis(r, axis)
        for t in raw:
            leaf = t.strip('/').split('/')[-1] if axis in ('routes', 'api') else t
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

    # Suggested checkpoints (reverse-sync aid): one per token, with the
    # per-platform regex alternation of the raw tokens that represent it.
    suggested = []
    for leaf, by_plat in leaf_map.items():
        match = {p: '|'.join(re.escape(t) for t in sorted(toks))
                 for p, toks in by_plat.items()}
        suggested.append({
            'id': re.sub(r'[^a-z0-9]+', '-', leaf.lower()).strip('-') or 'item',
            'desc': f'{axis} 项: {leaf}',
            'match': match,
        })

    # Lag vs a designated source platform (source-of-truth migration view).
    lag = {}
    if source:
        if source not in names:
            return {'mode': 'symbol',
                    'note': f'--source {source} not among detected platforms '
                            f'({", ".join(names)}).',
                    'axis': axis,
                    'leaf_map': {k: {p: sorted(v) for p, v in pl.items()}
                                 for k, pl in leaf_map.items()},
                    'drift': drift, 'suggested': suggested, 'lag': {},
                    'platforms': names}
        src_leaves = {leaf for leaf, by_plat in leaf_map.items()
                      if source in by_plat}
        for name in names:
            if name == source:
                continue
            tgt_leaves = {leaf for leaf, by_plat in leaf_map.items()
                          if name in by_plat}
            lag[name] = sorted(src_leaves - tgt_leaves)

    return {'mode': 'symbol', 'axis': axis, 'source': source,
            'leaf_map': {k: {p: sorted(v) for p, v in pl.items()}
                         for k, pl in leaf_map.items()},
            'drift': drift, 'suggested': suggested, 'lag': lag,
            'platforms': names}


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
        if result.get('version') is not None:
            lines.append(f'契约版本: v{result["version"]}')
        for row in result['matrix']:
            if row.get('source'):
                when = f' @ {row["since"]}' if row.get('since') else ''
                lines.append(f'  - {row["id"]}: 当前真源 = {row["source"]}{when}')
    else:
        note = result.get('note')
        if note:
            lines.append(note)
            return '\n'.join(lines)
        axis = result.get('axis', 'routes')
        lines.append(f'Symbol mode (axis={axis}) across: {", ".join(result.get("platforms", []))}')
        if result.get('drift'):
            what = 'screen' if axis == 'routes' else axis + ' item'
            lines.append(f'\nDrift candidates ({len(result["drift"])}): {what} present in some, missing in others')
            for d in result['drift'][:30]:
                lines.append(f'  {d["leaf"]}  missing in: {", ".join(DISPLAY.get(x, x) for x in d["missing_in"])}')
        else:
            lines.append(f'\nNo {axis} drift detected across comparable platforms.')
        if result.get('lag'):
            src = result.get('source')
            lines.append(f'\n相对指定真源 {src} 的落后 (--source):')
            for plat, items in result['lag'].items():
                lines.append(f'  {DISPLAY.get(plat, plat)} 落后 {len(items)} 项: '
                             + ', '.join(items[:20]))
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
        if result.get('version') is not None:
            out.append('')
            out.append(f'**契约版本:** v{result["version"]}')
        prov = [(r['id'], r.get('source', ''), r.get('since', ''))
                for r in result['matrix'] if r.get('source')]
        if prov:
            out.append('')
            out.append('## 真源与溯源 (Source of Truth)')
            out.append('')
            out.append('| Checkpoint | 当前真源端 | 设定日期 |')
            out.append('|------------|-----------|----------|')
            for cid, src, since in prov:
                out.append(f'| {cid} | {src} | {since or "-"} |')
            out.append('')
            out.append('> 真源端记录的是"最后设定/领先该检查点的一端"。真源迁移（Mode C）'
                       '后这里会更新为新的领先端，契约 version 同时 +1。')
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
        out.append(f'**Axis:** `{result.get("axis", "routes")}` '
                   f'(routes 只看叶节点归一化；api/model/i18n 全平台可比)')
        out.append('')
        out.append('## Drift candidates')
        axis_noun = ('Screen' if result.get('axis', 'routes') == 'routes'
                     else result.get('axis', 'routes').capitalize() + ' item')
        out.append(f'{axis_noun}s present in some platforms but missing in others '
                   '(normalized to the leaf segment for routes/api):')
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
        if result.get('lag'):
            out.append('')
            out.append(f'## 相对指定真源 {result.get("source")} 的落后 (--source)')
            out.append('')
            out.append('| Platform | 落后项数 | 缺失项（叶节点） |')
            out.append('|----------|----------|----------------|')
            for plat, items in result['lag'].items():
                out.append(f'| {DISPLAY.get(plat, plat)} | {len(items)} | '
                           + ', '.join(f'`{i}`' for i in items[:15]) + ' |')
            out.append('')
            out.append('> 这是真源迁移 / 追赶视图：以指定端为临时真源，其它端相对它'
                       '还差哪些项。逐项补齐后即追平。')
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
    ap.add_argument('--axis', choices=['routes', 'api', 'model', 'i18n'], default='routes',
                    help='symbol-mode comparison axis (default routes)')
    ap.add_argument('--source', help='platform name to treat as temporary truth (symbol mode)')
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

    if args.source and args.source not in PLATFORM_KEYS:
        sys.stderr.write(f'--source must be a known platform, got: {args.source}\n'
                         f'Known: {", ".join(sorted(PLATFORM_KEYS))}\n')
        sys.exit(2)

    if mode == 'checkpoint':
        if not contract_text:
            sys.stderr.write('checkpoint mode requires --contract.\n')
            sys.exit(2)
        result = run_checkpoint(platforms, contract_text)
    else:
        result = run_symbol(platforms, args.axis, args.source)

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
