#!/usr/bin/env python3
"""Check the bank fixture keeps all code/data/stack outside the paged window."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_link_map import parse_map  # noqa: E402

map_path = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "build/banks/BANKS.map")
cfg = json.loads((ROOT / "cfg/banks-memory.json").read_text())
sections = parse_map(map_path)
errors = []

code_lo = int(cfg["code"]["start"], 0)
code_hi = int(cfg["code"]["end_exclusive"], 0)
code_start, code_len = sections["CODE"]
if code_start != code_lo or code_start + code_len > code_hi or code_hi > 0x4000:
    errors.append("linked code must stay in fixed RAM0 below &4000")

data_lo = int(cfg["globals"]["start"], 0)
data_hi = int(cfg["globals"]["end_exclusive"], 0)
data_sections = ("DATA", "INITIALIZED", "INITIALIZER", "GSINIT", "GSFINAL", "HOME", "DABS", "CABS")
used = []
for name in data_sections:
    if name not in sections:
        continue
    start, size = sections[name]
    if not size:
        continue
    end = start + size
    used.append((start, end, name))
    if start < data_lo or end > data_hi or end > 0x4000:
        errors.append(f"{name} 0x{start:04X}-0x{end:04X} must stay in fixed RAM0 globals")

stack_lo = int(cfg["stack"]["start"], 0)
stack_top = int(cfg["stack"]["top_exclusive"], 0)
guard_lo = int(cfg["stack_guard"]["start"], 0)
guard_hi = int(cfg["stack_guard"]["end_exclusive"], 0)
if not (0x8000 <= stack_lo < guard_hi <= stack_top <= 0xC000):
    errors.append("stack and guard must fit in fixed RAM2 below &C000")
if stack_top - stack_lo != cfg["stack"]["reserved_bytes"]:
    errors.append("stack reservation size mismatch")
if guard_hi - guard_lo != cfg["stack_guard"]["reserved_bytes"]:
    errors.append("stack guard size mismatch")
if stack_lo != guard_lo:
    errors.append("stack guard must occupy the bottom of the reserved stack")
if stack_lo < 0x8000 or stack_top > 0xC000:
    errors.append("stack must remain visible in RAM2 while RAM4–7 are paged")

screen_lo, screen_hi = (int(v, 0) for v in (cfg["visible_screen"]["start"], cfg["visible_screen"]["end_exclusive"]))
if (screen_lo, screen_hi) != (0xC000, 0x10000):
    errors.append("visible screen must remain physical RAM3 at &C000–&FFFF")
boot = cfg["bootstrap"]
boot_lo, boot_hi = int(boot["start"], 0), int(boot["end_exclusive"], 0)
if not code_start <= boot_lo <= boot_hi <= code_start + code_len:
    errors.append("bootstrap must be inside linked code")
if errors:
    raise SystemExit("FAIL: " + "; ".join(errors))
data_end = max((end for _, end, _ in used), default=data_lo)
print(f"PASS: bank fixture code 0x{code_start:04X}-0x{code_start + code_len - 1:04X}; "
      f"globals through 0x{data_end - 1:04X}; stack in fixed RAM2; paged window contains no code/data/stack.")
