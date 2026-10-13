#!/usr/bin/env python3
"""Check build dependencies; emulator checks are explicit and never certify audio."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emulator', action='store_true', help='also check the local Caprice32 setup')
    args = parser.parse_args()
    lock = json.loads((ROOT / 'cfg/toolchain.lock.json').read_text())
    failed = False
    for name in ('python3', 'make', 'cc', 'c++', 'git', 'sdcc', 'sdasz80', 'sdar', 'ffmpeg'):
        path = shutil.which(name)
        print(f'{"PASS" if path else "MISS"} {name}: {path or "not in PATH"}')
        failed |= not bool(path)
    if shutil.which('sdcc'):
        version = subprocess.check_output(['sdcc', '--version'], text=True).splitlines()[0]
        ok = '4.6.0' in version
        print(f'{"PASS" if ok else "FAIL"} expected SDCC 4.6.0: {version}')
        failed |= not ok
    files = [lock['cpctelera']['path'] + '/cpctelera.lib',
             lock['background_codec']['host_encoder'],
             lock['background_codec']['host_encoder'].replace('/zx0', '/dzx0'),
             lock['disk_tools']['hex2bin'], lock['disk_tools']['iDSK']]
    if args.emulator:
        files += ['.tools/cap32', '.tools/cap32.cfg', '.tools/rom/cpc6128.rom']
    for name in files:
        ok = (ROOT / name).is_file()
        print(f'{"PASS" if ok else "MISS"} {name}')
        failed |= not ok
    for label, path, commit in (
        ('CPCTelera', ROOT / 'tmp/cpctelera', lock['cpctelera']['git_commit']),
        ('ZX0', ROOT / 'tmp/research-tools/ZX0', lock['background_codec']['git_commit'])):
        if path.is_dir():
            result = subprocess.run(['git', '-C', str(path), 'rev-parse', 'HEAD'], capture_output=True, text=True)
            ok = result.returncode == 0 and result.stdout.strip() == commit
            print(f'{"PASS" if ok else "FAIL"} {label} pinned revision')
            failed |= not ok
    library = ROOT / lock['cpctelera']['path'] / 'cpctelera.lib'
    if library.is_file():
        digest = hashlib.sha256(library.read_bytes()).hexdigest()
        print('INFO CPCTelera library SHA-256: ' + digest)
    print('Checks cover tool availability and versions, not gameplay, audio output or physical hardware.')
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
