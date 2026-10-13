#!/usr/bin/env python3
"""Check the independent platform diagnostic profile and map."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
disk = ROOT / "build/platform/PLATFORM.dsk"
binary = ROOT / "build/platform/PLATFORM.bin"
log = ROOT / "build/platform/PLATFORM.bin.log"
checker = ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"
if not all(path.is_file() for path in (disk, binary, log)):
    raise SystemExit("FAIL: incomplete platform diagnostic build")
if "Binary file start = 00000100" not in log.read_text(errors="replace"):
    raise SystemExit("FAIL: platform diagnostic must load at &0100")
catalog = subprocess.run([str(checker), str(disk), "-l"], capture_output=True, text=True)
if catalog.returncode or not re.search(r"PLATFORM\s*\.BIN", catalog.stdout.upper()):
    raise SystemExit("FAIL: platform diagnostic DSK catalog is unreadable")
print(f"PASS: platform diagnostic DSK/BIN build at &0100 ({len(binary.read_bytes())} bytes)")
