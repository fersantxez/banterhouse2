#!/usr/bin/env python3
"""Validate the isolated fixed-memory bank test disk and its load address."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
base = ROOT / "build/banks"
dsk = base / "BANKS.dsk"
binary = base / "BANKS.bin"
log = base / "BANKS.bin.log"
idsk = ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"
if not all(path.is_file() for path in (dsk, binary, log)):
    raise SystemExit("FAIL: incomplete bank test DSK/BIN/log")
if "Binary file start = 00000100" not in log.read_text(errors="replace"):
    raise SystemExit("FAIL: bank test binary must load at &0100")
catalog = subprocess.run([str(idsk), str(dsk), "-l"], capture_output=True,
                         text=True)
if catalog.returncode or not re.search(r"BANKS\s*\.BIN", catalog.stdout.upper()):
    raise SystemExit("FAIL: bank test DSK catalog is unreadable or missing BANKS.BIN")
print(f"PASS: isolated bank test disk catalog/load address; {binary.stat().st_size} bytes")
