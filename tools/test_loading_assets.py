#!/usr/bin/env python3
"""Verify the linked splash payload, decompression and boot memory bounds."""
from pathlib import Path
import re
import subprocess
import tempfile
from check_link_map import check
from check_tape import check as check_tape

ROOT = Path(__file__).resolve().parents[1]


def main():
    report = check(ROOT / 'build/DEVUELTO.map', ROOT / 'cfg/memory.json')
    start, size = report['sections']['LOADING']
    binary = (ROOT / 'build/DEVUELTO.bin').read_bytes()
    assert len(binary) == start + size - 0x100
    with tempfile.TemporaryDirectory() as folder:
        packed, raw = Path(folder) / 'screen.zx0', Path(folder) / 'screen.scr'
        packed.write_bytes(binary[start-0x100:start-0x100+size])
        subprocess.run([str(ROOT / 'tmp/research-tools/ZX0/src/dzx0'),
                        str(packed), str(raw)], check=True)
        assert raw.read_bytes() == (ROOT / 'assets/loading/banterhouse2-loading.scr').read_bytes()
    mapping = (ROOT / 'build/DEVUELTO.map').read_text()
    with tempfile.TemporaryDirectory() as folder:
        bad = Path(folder) / 'invalid.map'
        for symbol, value in [('s__LOADING', '00007FF0'), ('l__LOADING', '00002701')]:
            bad.write_text(re.sub(r'([0-9A-F]{8})(\s+' + symbol + r'\s)',
                                  lambda m: value + m[2], mapping))
            try:
                check(bad, ROOT / 'cfg/memory.json')
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid splash memory placement accepted: ' + symbol)
    address = int(re.search(r'^\s*([0-9A-F]{8})\s+_loading_palette\s', mapping, re.M)[1], 16)
    assert binary[address-0x100:address-0x100+16] == (ROOT / 'assets/loading/banterhouse2-loading.hwpal').read_bytes()
    assert (ROOT / 'build/DEVUELTO.cdt').read_bytes().startswith(b'ZXTape!\x1a')
    check_tape(ROOT / 'build/DEVUELTO.cdt', ROOT / 'build/DEVUELTO.bin', ROOT / 'build/DEVUELTO.map')
    with tempfile.TemporaryDirectory() as folder:
        damaged = Path(folder) / 'damaged.cdt'
        content = bytearray((ROOT / 'build/DEVUELTO.cdt').read_bytes())
        content[60] ^= 1
        damaged.write_bytes(content)
        try:
            check_tape(damaged, ROOT / 'build/DEVUELTO.bin', ROOT / 'build/DEVUELTO.map')
        except AssertionError:
            pass
        else:
            raise AssertionError('Corrupt tape accepted')
    print(f'PASS linked splash: {size} bytes at &{start:04X}, exact 16384-byte decompression and palette; CDT present')
    print('PASS rejection: splash overlapping stack or reaching firmware workspace')
    print('PASS tape payload/addresses/CRCs and rejection of corrupt tape')


if __name__ == '__main__':
    main()
