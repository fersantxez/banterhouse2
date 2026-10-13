#!/usr/bin/env python3
"""Check that the autonomous edge-fall CPC fixture produced a loadable DSK."""
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
disk=ROOT/'build/physics/PHYSICS.dsk'
binary=ROOT/'build/physics/PHYSICS.bin'
log=ROOT/'build/physics/PHYSICS.bin.log'
checker=ROOT/'tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK'
if not all(p.is_file() for p in (disk,binary,log)):
    raise SystemExit('FAIL: falta el DSK/BIN/log del fixture de física')
if 'Binary file start = 00000100' not in log.read_text(errors='replace'):
    raise SystemExit('FAIL: el fixture de física debe cargar en &0100')
catalog=subprocess.run([str(checker),str(disk),'-l'],capture_output=True,text=True)
if catalog.returncode or not re.search(r'PHYSICS\s*\.BIN',catalog.stdout.upper()):
    raise SystemExit('FAIL: el DSK del fixture no es legible')
print(f'PASS DSK de física cargable en &0100 ({len(binary.read_bytes())} bytes); el resultado PASS/FAIL se calcula en Z80 al arrancar')
