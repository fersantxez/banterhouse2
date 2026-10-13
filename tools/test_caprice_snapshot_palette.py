#!/usr/bin/env python3
"""Ensure a one-ink corruption in a real Caprice SNA is rejected."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "research/runs/20261012T234446Z-T03-snapshot-palette/caprice/01-copias.sna"
data = bytearray(source.read_bytes())
data[47] ^= 1
with tempfile.TemporaryDirectory(prefix="palette-negative-") as directory:
    corrupt = Path(directory) / "corrupt.sna"
    corrupt.write_bytes(data)
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/check_caprice_snapshot_palette.py"),
         "01-copias", str(corrupt)], capture_output=True, text=True
    )
if result.returncode == 0 or "Gate Array inks differ" not in result.stderr:
    raise SystemExit("FAIL: corrupted Gate Array ink value was not rejected")
print("PASS: corrupted Caprice snapshot ink is rejected with a direct palette mismatch")
