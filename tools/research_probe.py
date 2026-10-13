#!/usr/bin/env python3
"""Auditoría host de recursos; no mide ciclos ni ejecuta un CPC."""
import argparse
import hashlib
import json
import platform
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(args):
    return subprocess.check_output([str(a) for a in args], stderr=subprocess.STDOUT, text=True)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, default=(ROOT.parent / 'banterhouse'))
    parser.add_argument('--compress', action='store_true')
    args = parser.parse_args()
    original = args.original.resolve()
    if ROOT == original or original in ROOT.parents:
        raise SystemExit('La salida debe estar fuera del proyecto original')
    out = ROOT / 'research/results'
    temp = ROOT / 'tmp/research-probe'
    out.mkdir(parents=True, exist_ok=True)
    temp.mkdir(parents=True, exist_ok=True)
    report = {'kind': 'host_only_no_CPC_timing', 'consulted': '2026-10-10',
              'host': platform.platform(), 'python': platform.python_version(),
              'original_head': run(['git', '-C', original, 'rev-parse', 'HEAD']).strip(),
              'inputs': {}, 'sprites': [], 'compression': []}
    def read(rel):
        data = (original / rel).read_bytes()
        report['inputs'][rel] = {'bytes': len(data), 'sha256': digest(data)}
        return data

    # Sólo las cuatro matrices fuente usadas en gameplay. No se extraen los
    # frames de salto ni los espejos históricos dentro de #if 0.
    source = read('src/graphics.c').decode()
    source = re.sub(r'#if 0\b.*?#endif', '', source, flags=re.S)
    corpus = {}
    sprites = bytearray()
    for name in ['g_pitu', 'g_pitu_walk', 'g_alberto', 'g_alberto_walk']:
        match = re.search(r'const unsigned char\s+' + name + r'\[512\]\s*=\s*\{(.*?)\}', source, re.S)
        if not match:
            raise ValueError('Matriz no encontrada: ' + name)
        data = bytes(int(n, 16) for n in re.findall(r'0x([0-9a-fA-F]{2})', match[1]))
        assert len(data) == 512
        masks, pixels = data[0::2], data[1::2]
        assert set(masks) <= {0, 0x55, 0xAA, 0xFF}
        assert all((m & p) == 0 for m, p in zip(masks, pixels))
        counts = {'transparent': masks.count(255), 'opaque': masks.count(0),
                  'partial': sum(m not in (0, 255) for m in masks)}
        # Verifica la transformación byte a byte sobre TODOS los fondos.
        for m, p in zip(masks, pixels):
            for background in range(256):
                generic = (background & m) | p
                specialized = background if m == 255 else p if m == 0 else (background & m) | p
                assert generic == specialized
        report['sprites'].append({'name': name, 'bytes_masked': len(data),
                                  'sha256': digest(data), **counts,
                                  'specialization_equivalence_cases': 256 * 256})
        sprites.extend(data)
    corpus['sprites_originales'] = bytes(sprites)
    corpus['pantalla_carga'] = read('dsk_files/LOADING.SCR')
    corpus['fixture_lab_paper'] = read('generated/resources/lab-paper.scr')
    room_files = sorted((original / 'generated/rooms').glob('*.bin'))
    assert room_files, 'Faltan las salas generadas de referencia'
    corpus['salas_lab_concatenadas'] = b''.join(read(str(p.relative_to(original))) for p in room_files)
    for rel in ['src/game_render.c', 'src/game.c', 'src/audio.c', 'src/main.c',
                'src/resource_manager.c', 'src/storage_fdc_lab.s', 'tools/expanded_kernel.s',
                'cfg/build_config.mk', 'docs/IMPLEMENTATION_STATUS.md']:
        read(rel)
    if args.compress:
        toolroot = ROOT / 'tmp/research-tools'
        zx0 = toolroot / 'ZX0/src/zx0'
        dzx0 = toolroot / 'ZX0/src/dzx0'
        lzsa = toolroot / 'lzsa/lzsa'
        report['tool_commits'] = {name: run(['git', '-C', toolroot / name, 'rev-parse', 'HEAD']).strip()
                                  for name in ['ZX0', 'lzsa']}
        report['compiler'] = run(['clang', '--version']).splitlines()[0]
        for name, data in corpus.items():
            inp = temp / (name + '.bin')
            inp.write_bytes(data)
            for fmt in ['zx0', 'lzsa1', 'lzsa2']:
                packed = temp / (name + '.' + fmt)
                decoded = temp / (name + '.' + fmt + '.decoded')
                # Sobrescribe sólo los resultados temporales de esta prueba.
                packed.unlink(missing_ok=True)
                decoded.unlink(missing_ok=True)
                if fmt == 'zx0':
                    cmd = [zx0, inp, packed]
                    decode = [dzx0, packed, decoded]
                else:
                    version = fmt[-1]
                    cmd = [lzsa, '-r', '-f', version, inp, packed]
                    decode = [lzsa, '-d', '-r', '-f', version, packed, decoded]
                log = run(cmd)
                run(decode)
                assert decoded.read_bytes() == data, (name, fmt)
                report['compression'].append({'corpus': name, 'format': fmt,
                    'input_bytes': len(data), 'input_sha256': digest(data),
                    'packed_bytes': packed.stat().st_size,
                    'packed_sha256': digest(packed.read_bytes()),
                    'roundtrip_host': True, 'command': [str(a) for a in cmd],
                    'stdout': log.strip(), 'CPC_depack_ms': None})
    report['arithmetic'] = {
        'screen_visible_bytes': 80 * 200,
        'screen_reserved_bytes': 16384,
        'masked_actor_8poses_2directions_2alignments_bytes': 8 * 2 * (8 + 9) * 32 * 2,
        'save_under_4actors_max_width_bytes': 4 * 9 * 32,
        'data_disk_gross_bytes': 40 * 9 * 512,
        'data_disk_after_directory_bytes': 40 * 9 * 512 - 2048,
        'ideal_ldir_16KiB_tstates': 21 * 16384 - 5,
        'ideal_ldir_16KiB_ms_at_4MHz': (21 * 16384 - 5) / 4000,
    }
    target = out / ('host-probe.json' if args.compress else 'asset-probe.json')
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(target)
    for s in report['sprites']:
        print(s['name'], {k:s[k] for k in ['transparent','opaque','partial']})
    for c in report['compression']:
        print(c['corpus'], c['format'], c['input_bytes'], '->', c['packed_bytes'], 'roundtrip OK')


if __name__ == '__main__':
    main()
