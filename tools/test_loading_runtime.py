#!/usr/bin/env python3
"""Cold boot the real DSK/CDT; capture splash, menu and gameplay in Caprice."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from run_game import caprice_media_commands

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--medium', choices=['disk', 'tape'], required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--speed', type=int, choices=[4, 8], default=4, help='4 normal, 8 host playback at twice speed')
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    captures = out / 'captures'
    captures.mkdir()
    source = ROOT / ('build/DEVUELTO.dsk' if args.medium == 'disk' else 'build/DEVUELTO.cdt')
    medium = out / source.name
    medium.write_bytes(source.read_bytes())
    for name in ('DEVUELTO.bin', 'DEVUELTO.map'):
        (out / name).write_bytes((ROOT / 'build' / name).read_bytes())
    config = (ROOT / '.tools/cap32.cfg').read_text()
    for key, value in [('snap_path', str(captures)), ('sdump_dir', str(captures)), ('scr_fps', '0'), ('speed', str(args.speed))]:
        config = re.sub(r'^' + key + r'=.*$', key + '=' + value, config, flags=re.M)
    template = out / 'cap32.cfg'
    template.write_text(config)
    # This installed Caprice predates the textual SNAPSHOT alias. Its existing
    # StringToEvents protocol maps form-feed + command 13 to Shift-F3.
    shot = '\f\rCAP32_SCRNSHOT'
    delay = 'CAP32_DELAY'
    if args.medium == 'disk':
        commands = caprice_media_commands(medium)
        timeline = (delay * 2 + shot) * 10
        timeout = 60
    else:
        commands = ['|tape', 'run""' + delay, delay + 'CAP32_TAPEPLAY' + delay + ' ']
        # Retain early load evidence, then sample around the last blocks.
        timeline = delay * 6 + shot + delay * 265 + (delay + shot) * 70
        timeout = 400
    timeline += ' ' + delay * 2 + shot + delay + 'CAP32_EXIT'
    command = ['python3', str(ROOT / 'tools/run_session.py'), '--run-dir', str(out / 'session'),
               '--timeout', str(timeout), '--config-template', str(template), '--',
               str(ROOT / '.tools/cap32'), '-v', '-c', '{config}']
    for line in commands + [timeline]:
        command += ['-a', line]
    command.append(str(medium))
    (out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
    assert commands == caprice_media_commands(medium)
    deadline = time.monotonic() + 180
    while True:
        code = subprocess.call(command, cwd=ROOT)
        if code != 73 or time.monotonic() >= deadline:
            break
        time.sleep(3)
    if code != 0:
        (out / 'result.json').write_text(json.dumps({'passed': False, 'supervisor_exit': code}) + '\n')
        return code
    expected = (ROOT / 'assets/loading/banterhouse2-loading.scr').read_bytes()
    palette = bytes(v & 31 for v in (ROOT / 'assets/loading/banterhouse2-loading.hwpal').read_bytes())
    # Resolve private mode symbol from the assembler output, plus DATA base.
    symbols = (ROOT / 'build/m1/obj/main.sym').read_text()
    mapping = (out / 'DEVUELTO.map').read_text()
    data_base = int(re.search(r'^\s*([0-9A-F]{8})\s+s__DATA\s', mapping, re.M)[1], 16)
    mode_addr = data_base + int(re.search(r'_mode\s+([0-9A-F]{8})\s+R', symbols)[1], 16)
    sdk = min(int(v, 16) for v in re.findall(r'^\s*([0-9A-F]{8})\s+_cpct_\w+\s', mapping, re.M))
    binary = (out / 'DEVUELTO.bin').read_bytes()
    observations = []
    seen_splash = False
    for path in sorted(captures.glob('*.sna')):
        data = path.read_bytes()
        ram = data[256:]
        exact_code = ram[0x100:sdk] == binary[:sdk-0x100]
        splash = ram[0xc000:0x10000] == expected and data[47:63] == palette and data[64] & 3 == 0
        seen_splash |= splash
        state = 'splash' if splash else ('menu' if ram[mode_addr] == 0 else 'game' if ram[mode_addr] == 1 else 'other') if exact_code and seen_splash else 'loading'
        observations.append({'file': path.name, 'state': state, 'exact_game_code': exact_code,
                             'sha256': hashlib.sha256(data).hexdigest()})
    states = [x['state'] for x in observations]
    cleanup = json.loads((out / 'session/result.json').read_text())['cleanup']
    passed = code == 0 and 'splash' in states and 'menu' in states[states.index('splash')+1:] and 'game' in states and cleanup['process_group_absent']
    result = {'passed': passed, 'medium': args.medium, 'medium_sha256': hashlib.sha256(medium.read_bytes()).hexdigest(),
              'observations': observations, 'cleanup': cleanup, 'hardware_verified': False}
    (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
