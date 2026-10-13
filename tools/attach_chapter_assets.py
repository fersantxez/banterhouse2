#!/usr/bin/env python3
"""Add generated AMSDOS chapter images to a game DSK."""
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDSK = ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"

parser = argparse.ArgumentParser()
parser.add_argument("disk", type=Path)
args = parser.parse_args()
disk = args.disk.resolve()
for chapter in range(1, 5):
    path = ROOT / f"build/chapter-assets/CH{chapter:02d}.BIN"
    if not path.is_file() or not path.stat().st_size:
        raise SystemExit(f"FAIL: missing chapter image {path}")
    result = subprocess.run([str(IDSK), str(disk), "-i", str(path), "-t", "1", "-f"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        details = (result.stderr + result.stdout).decode("mac_roman", errors="replace")
        raise SystemExit(f"FAIL: cannot add {path.name}: {details}")
    print(f"PASS: attached {path.name} ({path.stat().st_size} compressed bytes)")
