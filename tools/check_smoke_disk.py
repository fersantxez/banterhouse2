#!/usr/bin/env python3
"""Verify the isolated smoke DSK catalog and AMSDOS load extent."""
from pathlib import Path
import subprocess
import re

ROOT = Path(__file__).resolve().parents[1]
dsk = ROOT / "build/smoke/SMOKE.dsk"
binary = ROOT / "build/smoke/SMOKE.bin"
log = ROOT / "build/smoke/SMOKE.bin.log"
idsk = ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"
if not all(path.is_file() for path in (dsk, binary, log)):
    raise SystemExit("FAIL: smoke DSK, binary or address log missing")
result = subprocess.run([str(idsk), str(dsk), "-l"], text=True, capture_output=True)
if result.returncode or not re.search(r"SMOKE\s*\.BIN", result.stdout.upper()):
    raise SystemExit("FAIL: smoke DSK catalog is unreadable or lacks SMOKE.BIN\n" + result.stdout + result.stderr)
if "Binary file start = 00000100" not in log.read_text(errors="replace"):
    raise SystemExit("FAIL: smoke binary is not loaded at 0x0100")
print(f"PASS: isolated smoke DSK catalog and &0100 load address; {binary.stat().st_size} binary bytes.")
