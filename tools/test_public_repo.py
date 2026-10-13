#!/usr/bin/env python3
"""Negative fixtures for source publication boundaries; no real secrets are used."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
from check_public_repo import audit


def git(root, *args):
    subprocess.run(['git', '-C', str(root), *args], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def fixture(files, ignored='', force=None):
    with tempfile.TemporaryDirectory(prefix='bh2-public-audit-') as directory:
        root = Path(directory)
        git(root, 'init', '-q')
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        if ignored:
            (root / '.gitignore').write_text(ignored)
        if force:
            git(root, 'add', '-f', force)
        return audit(root)[3]


def main():
    assert not fixture({'README.md': '[Guide](docs/guide.md)', 'docs/guide.md': '# Guide'})
    assert fixture({'README.md': '[Missing](docs/missing.md)'})
    assert fixture({'README.md': '[Escape](../outside.md)'})
    assert fixture({'README.md': '# Source', 'site/private.txt': 'configuration'}, 'site/\n', 'site/private.txt')
    assert not fixture({'README.md': '# Source', 'site/private.txt': 'configuration'}, 'site/\n')
    fake = 'ghp_' + ('X' * 30)
    issues = fixture({'README.md': fake})
    assert issues and all(fake not in issue for issue in issues)
    assert fixture({'README.md': '[Ignored](build/result.md)', 'build/result.md': '# Generated'}, 'build/\n')
    disk = 'synthetic disk fixture'
    manifest = json.dumps({'bytes': len(disk), 'dsk_sha256': hashlib.sha256(disk.encode()).hexdigest()})
    assert not fixture({'release/Devuelto-CPC6128.dsk': disk, 'release/manifest.json': manifest})
    assert fixture({'release/Devuelto-CPC6128.dsk': disk + 'modified', 'release/manifest.json': manifest})
    assert fixture({'release/Devuelto-CPC6128.dsk': disk})
    assert fixture({'release/other.dsk': disk, 'release/manifest.json': manifest})
    print('PASS: publication audit rejects private files, invalid links, fake credentials and unverified disks; clean/ignored fixtures and manifest-matched disk pass.')


if __name__ == '__main__':
    main()
