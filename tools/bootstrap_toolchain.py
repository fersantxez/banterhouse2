#!/usr/bin/env python3
"""Build pinned CPC dependencies locally; never install globally or reset a checkout."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'cfg/toolchain.lock.json').read_text())


def run(*args, cwd=ROOT):
    subprocess.run([str(a) for a in args], cwd=cwd, check=True)


def checkout(url, commit, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        run('git', 'clone', '--no-checkout', url, path)
        run('git', 'checkout', '--detach', commit, cwd=path)
    actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain', '--untracked-files=no'], text=True)
    if actual != commit or dirty:
        raise SystemExit(f'Refusing to change an existing checkout with another revision or local edits: {path}')


def main():
    for executable in ('git', 'make', 'sdcc', 'sdasz80', 'sdar', 'cc', 'c++', 'ffmpeg'):
        if not shutil.which(executable):
            raise SystemExit(f'Missing {executable}. See docs/development/GETTING_STARTED.md')
    version = subprocess.check_output(['sdcc', '--version'], text=True)
    if '4.6.0' not in version:
        raise SystemExit('This build is pinned to SDCC 4.6.0; use that version before bootstrapping.')
    sdk = ROOT / 'tmp/cpctelera'
    checkout(LOCK['cpctelera']['repository'], LOCK['cpctelera']['git_commit'], sdk)
    engine = sdk / 'cpctelera'
    run('make', '-j2', 'Z80ASM=' + shutil.which('sdasz80'),
        'Z80LNK=' + shutil.which('sdar'), cwd=engine)
    for tool in ('hex2bin-2.0', 'iDSK-0.13'):
        (engine / 'tools' / tool / 'bin').mkdir(exist_ok=True)
        run('make', '-j2', 'SHELL=/bin/bash', cwd=engine / 'tools' / tool)
    codec = ROOT / 'tmp/research-tools/ZX0'
    checkout(LOCK['background_codec']['repository'], LOCK['background_codec']['git_commit'], codec)
    run('make', 'CC=cc', 'CFLAGS=-O2', 'EXTENSION=', cwd=codec / 'src')
    print('PASS: pinned build dependencies are ready. Next: make doctor && make campaign-disk')


if __name__ == '__main__':
    main()
