#!/usr/bin/env python3
"""Validate the CPC renderer fixture DSK catalog and load address."""
import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("dsk", nargs="?", default="build/render-cpc/RENDER.dsk")
args = parser.parse_args()
dsk = ROOT / args.dsk
base = dsk.parent
stem = dsk.stem
binary, log = base / f"{stem}.bin", base / f"{stem}.bin.log"
idsk = ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"
if not all(path.is_file() for path in (dsk, binary, log)):
    raise SystemExit("FAIL: incomplete renderer test DSK/BIN/log")
if "Binary file start = 00000100" not in log.read_text(errors="replace"):
    raise SystemExit("FAIL: renderer test binary must load at &0100")
catalog = subprocess.run([str(idsk), str(dsk), "-l"], capture_output=True, text=True)
if catalog.returncode or not re.search(re.escape(stem.upper()) + r"\s*\.BIN", catalog.stdout.upper()):
    raise SystemExit(f"FAIL: renderer DSK catalog is unreadable or missing {stem}.BIN")
print(f"PASS: renderer test disk catalog/load address; {binary.stat().st_size} bytes")
