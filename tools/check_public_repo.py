#!/usr/bin/env python3
"""Audit the actual Git candidate set without printing matched secret values."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = ('.git/', '.local/', '.tools/', 'tmp/', 'build/', 'dist/', 'site/',
             'artifacts/', 'research/runs/', 'assets/audio/private/', 'assets/references/')
SECRET_PATTERNS = [
    re.compile(r'(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_-]{20,}'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'(?:appgprj_|appgdep_)[a-f0-9]{20,}'),
    re.compile(r'/Users/[A-Za-z0-9_.-]+/'),
]


def candidates(root=ROOT):
    git_root = subprocess.check_output(['git', '-C', str(root), 'rev-parse', '--show-toplevel'], text=True).strip()
    if Path(git_root).resolve() != root.resolve():
        raise ValueError('Run from a dedicated Git checkout, not a subdirectory of another repository.')
    raw = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'])
    return sorted(set(x.decode() for x in raw.split(b'\0') if x))


def audit(root=ROOT):
    names = candidates(root)
    public = set(names)
    problems = []
    total = 0
    link_count = 0
    for name in names:
        path = root / name
        release_disk = name == 'release/Devuelto-CPC6128.dsk'
        if name.startswith(FORBIDDEN) or (path.suffix.lower() in ('.sna', '.rom', '.mid', '.dsk', '.cdt', '.pem', '.key', '.p12', '.pfx', '.pyc', '.pyo') and not release_disk) or path.name.startswith('.env') or path.name in ('.netrc', '.npmrc', 'id_rsa', 'id_ed25519'):
            problems.append(f'{name}: private/generated file in public candidate set')
        if path.is_symlink() or not path.is_file():
            problems.append(f'{name}: missing file, symlink or embedded repository')
            continue
        data = path.read_bytes()
        if release_disk:
            try:
                manifest = json.loads((root / 'release/manifest.json').read_text())
                if hashlib.sha256(data).hexdigest() != manifest['dsk_sha256'] or len(data) != manifest['bytes']:
                    problems.append(f'{name}: release disk does not match its manifest')
            except (OSError, ValueError, KeyError):
                problems.append(f'{name}: missing or invalid release manifest')
        total += len(data)
        if len(data) > 10 * 1024 * 1024:
            problems.append(f'{name}: exceeds the 10 MiB source-file budget')
        if b'\0' in data:
            continue
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                line = text[:match.start()].count('\n') + 1
                problems.append(f'{name}:{line}: private path or credential-like value (value withheld)')
        if path.suffix.lower() != '.md':
            continue
        # Fenced examples are not rendered links. Check inline Markdown links/images.
        markdown = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)
        for target in re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', markdown):
            target = target.strip().split(' "', 1)[0].strip('<>')
            if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', target) or target.startswith('#'):
                continue
            filename = unquote(target.split('#', 1)[0])
            if not filename:
                continue
            resolved = (path.parent / filename).resolve()
            try:
                rel = resolved.relative_to(root.resolve()).as_posix()
            except ValueError:
                problems.append(f'{name}: link escapes repository: {filename}')
                continue
            if rel not in public and not any(x.startswith(rel.rstrip('/') + '/') for x in public):
                problems.append(f'{name}: link target is not public: {filename}')
            link_count += 1
    if not names:
        problems.append('Public candidate set is empty')
    return names, total, link_count, problems


def main():
    try:
        names, size, links, problems = audit()
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    for problem in problems:
        print('FAIL: ' + problem)
    if problems:
        print(f'FAIL: {len(problems)} publication issues')
        return 1
    print(f'PASS: {len(names)} public source files, {size:,} bytes, {links} local Markdown links; no excluded paths or known secret patterns detected.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
