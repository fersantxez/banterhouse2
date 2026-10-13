#!/usr/bin/env python3
"""Check the cadence/pause Z80 fixture can be loaded from its DSK."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "build/cadence"
disk = BASE / "CADENCE.dsk"
binary = BASE / "CADENCE.bin"
log = BASE / "CADENCE.bin.log"
checker = ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"
if not all(path.is_file() for path in (disk, binary, log)):
    raise SystemExit("FAIL: falta el DSK/BIN/log del replay CPC de cadencia")
if "Binary file start = 00000100" not in log.read_text(errors="replace"):
    raise SystemExit("FAIL: el replay de cadencia debe cargar en &0100")
catalog = subprocess.run([str(checker), str(disk), "-l"], capture_output=True, text=True)
if catalog.returncode or not re.search(r"CADENCE\s*\.BIN", catalog.stdout.upper()):
    raise SystemExit("FAIL: el DSK de cadencia no se puede catalogar")
print(f"PASS DSK de cadencia cargable en &0100 ({len(binary.read_bytes())} bytes)")
