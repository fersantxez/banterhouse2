#!/usr/bin/env python3
"""Check the actual game linker map against the CPC 6128 reservations."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_link_map import check  # noqa: E402

mapping = ROOT / "build/DEVUELTO.map"
if not mapping.exists():
    raise SystemExit("FAIL: build/DEVUELTO.map is missing; run `make build` first")
try:
    report = check(mapping, ROOT / "cfg/memory.json")
except (ValueError, KeyError) as exc:
    raise SystemExit(f"FAIL: {exc}") from exc

data = (f"0x{report['data_start']:04X}-0x{report['data_end']-1:04X}"
        if report["data_end"] > report["data_start"] else "empty")
print(f"PASS: game link map: code 0x0100-0x{report['code_end']-1:04X}; "
      f"resident data {data}; reserved stack and video pages do not overlap.")
