#!/usr/bin/env python3
"""Inventario y copia íntegra, de alcance acotado, del candidato CPC existente."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
INCLUDE_DIRS = ('src', 'cfg', 'tools', 'assets/cpc-studies')
INCLUDE_FILES = ('Makefile', 'project.mk', '.gitignore', 'README.md',
                 'docs/PLAYTEST.md', 'docs/implementation/FINAL_CANDIDATE.md',
                 'build/DEVUELTO.bin', 'build/DEVUELTO.dsk',
                 'build/DEVUELTO.map', 'build/DEVUELTO.noi',
                 'dist/Devuelto-CPC6128.dsk', 'dist/SHA256SUMS.json')
SKIP_DIR_NAMES = {'.git', '__pycache__'}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def candidates():
    found = set()
    for rel in INCLUDE_FILES:
        p = ROOT / rel
        if p.is_file():
            found.add(p)
    for dirname in INCLUDE_DIRS:
        base = ROOT / dirname
        if base.is_dir():
            for p in base.rglob('*'):
                if not any(part in SKIP_DIR_NAMES for part in p.parts) and p.is_file():
                    found.add(p)
    return sorted(found)


def make_targets():
    files = [ROOT / n for n in ('Makefile', 'project.mk') if (ROOT / n).exists()]
    report = []
    for path in files:
        content = path.read_text(errors='replace')
        for line_no, line in enumerate(content.splitlines(), 1):
            if ':' not in line or line.lstrip().startswith('#') or line[:1].isspace():
                continue
            lhs = line.split(':', 1)[0].strip()
            if not lhs or any(c in lhs for c in '$%'):
                continue
            report.append({'file': str(path.relative_to(ROOT)), 'line': line_no,
                           'target': lhs, 'recipe_declared': True,
                           'recipe_lines': []})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='directorio nuevo dentro de research/runs')
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = args.out or ROOT / 'research/runs' / f'{stamp}-O00-audit'
    out = out.expanduser().resolve()
    runs = (ROOT / 'research/runs').resolve()
    if out == runs or runs not in out.parents or out.exists():
        raise SystemExit('FAIL: --out debe ser un directorio NUEVO bajo research/runs')
    paths = candidates()
    records = []
    for source in paths:
        rel = source.relative_to(ROOT)
        before_hash, before_size = digest(source), source.stat().st_size
        destination = out / 'snapshot' / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        after_hash = digest(source)
        copy_hash = digest(destination)
        records.append({'path': str(rel), 'bytes': before_size,
                        'sha256': before_hash, 'snapshot_sha256': copy_hash,
                        'source_unchanged_during_copy': before_hash == after_hash,
                        'snapshot_exact': before_hash == copy_hash,
                        'classification': 'unverified-existing' if str(rel).startswith(('build/', 'dist/')) else 'source-or-tool'})
    if any(not r['source_unchanged_during_copy'] or not r['snapshot_exact'] for r in records):
        raise SystemExit('FAIL: fuente cambió o la copia difiere; conservar run y repetir en carpeta nueva')
    makefiles = [ROOT / 'Makefile', ROOT / 'project.mk']
    referenced_scripts = []
    for makefile in makefiles:
        if not makefile.exists():
            continue
        for line_no, line in enumerate(makefile.read_text(errors='replace').splitlines(), 1):
            if 'python' not in line:
                continue
            import re
            match = re.search(r'python\S*\s+([^\s]+\.py)', line)
            if match:
                candidate = (makefile.parent / match.group(1)).resolve()
                referenced_scripts.append({'makefile': str(makefile.relative_to(ROOT)), 'line': line_no,
                    'script': str(candidate.relative_to(ROOT)) if ROOT in candidate.parents else str(candidate),
                    'exists': candidate.is_file(), 'status': 'verified-path-only' if candidate.is_file() else 'missing_dependency'})
    report = {'task': 'O00', 'created_utc': stamp, 'scope': 'file inventory and exact snapshot; no game or emulator execution',
              'root': str(ROOT), 'snapshot': str(out / 'snapshot'), 'files': records,
              'make_targets': make_targets(), 'python_scripts_referenced_by_make': referenced_scripts}
    out.mkdir(parents=True, exist_ok=True)
    (out / 'inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'run': str(out), 'files_snapshotted': len(records),
                      'snapshot_exact': all(x['snapshot_exact'] for x in records),
                      'missing_make_scripts': [x['script'] for x in referenced_scripts if not x['exists']]},
                      ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
