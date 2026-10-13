#!/usr/bin/env python3
"""Ensure the CPC renderer fixture remains callable while RAM4/RAM6 are paged."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_link_map import parse_map  # noqa: E402

map_path = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "build/render-cpc/RENDER.map")
cfg = json.loads((ROOT / "cfg/render-memory.json").read_text())
sections = parse_map(map_path)
errors = []

code_lo = int(cfg["code"]["start"], 0)
code_hi = int(cfg["code"]["end_exclusive"], 0)
code_start, code_len = sections["CODE"]
if code_start != code_lo or code_start + code_len > code_hi or code_hi > 0x4000:
    errors.append("renderer code and generated poses must stay in fixed RAM0 below &4000")

data_lo = int(cfg["globals"]["start"], 0)
data_hi = int(cfg["globals"]["end_exclusive"], 0)
for name in ("DATA", "INITIALIZED", "INITIALIZER", "GSINIT", "GSFINAL", "HOME", "DABS", "CABS"):
    if name not in sections:
        continue
    start, size = sections[name]
    if size and (start < data_lo or start + size > data_hi):
        errors.append(f"{name} 0x{start:04X}-0x{start + size:04X} escapes fixed RAM0 globals")

stack = cfg["stack"]
stack_lo, stack_top = int(stack["start"], 0), int(stack["top_exclusive"], 0)
if not (data_hi <= stack_lo < stack_top <= 0x4000 and
        stack_top - stack_lo == stack["reserved_bytes"]):
    errors.append("renderer stack must stay in fixed RAM0 after globals and below &4000")
guard = cfg["stack_guard"]
guard_lo, guard_hi = int(guard["start"], 0), int(guard["end_exclusive"], 0)
if not (stack_lo == guard_lo < guard_hi <= stack_top and
        guard_hi - guard_lo == guard["reserved_bytes"]):
    errors.append("renderer stack guard must occupy the bottom of the RAM0 stack reservation")
back = cfg["back_buffer"]
if (int(back["start"], 0), int(back["end_exclusive"], 0)) != (0x8000, 0xC000):
    errors.append("renderer backbuffer must occupy the complete RAM2 page at &8000-&BFFF")
if errors:
    raise SystemExit("FAIL: " + "; ".join(errors))
data_end = max((start + size for name, (start, size) in sections.items()
                if name in ("DATA", "INITIALIZED", "INITIALIZER", "GSINIT", "GSFINAL", "HOME", "DABS", "CABS") and size),
               default=data_lo)
print(f"PASS: renderer fixture code 0x{code_start:04X}-0x{code_start + code_len - 1:04X}; "
      f"globals through 0x{data_end - 1:04X}; guarded stack in fixed RAM0; full RAM2 backbuffer; paged window excluded.")
