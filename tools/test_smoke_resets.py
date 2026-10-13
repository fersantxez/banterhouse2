#!/usr/bin/env python3
"""Process-liveness probe only; does not verify CPC boot or program execution."""
import argparse
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument("--count", type=int, default=10)
parser.add_argument("--boot-seconds", type=float, default=1.5)
args = parser.parse_args()
if args.count < 1 or args.boot_seconds < 0.5:
    parser.error("--count must be positive and --boot-seconds at least 0.5")

emulator = ROOT / ".tools/cap32"
config = ROOT / ".tools/cap32.cfg"
disk = ROOT / "build/smoke/SMOKE.dsk"
for path in (emulator, config, disk):
    if not path.exists():
        raise SystemExit(f"FAIL: missing test input {path}; run `make smoke-boot` first")

for number in range(1, args.count + 1):
    proc = subprocess.Popen(
        [str(emulator), "-c", str(config), "-a", 'run"SMOKE.BIN"', str(disk)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(args.boot_seconds)
    if proc.poll() is not None:
        raise SystemExit(f"FAIL: Caprice exited during cold boot {number}/{args.count} (code {proc.returncode})")
    proc.terminate()
    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            raise SystemExit(f"FAIL: could not clean up Caprice after cold boot {number}/{args.count}")
    print(f"PROCESS ONLY {number}/{args.count}: Caprice live {args.boot_seconds:.1f}s; CPC boot NOT verified")
