#!/usr/bin/env python3
"""Validate linked CPC sections against cfg/memory.json; never infers runtime use."""
import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_map(path):
    text = Path(path).read_text(errors="replace")
    # These symbols are the authoritative linked-area start/length pairs.
    symbols = {}
    for value, prefix, name in re.findall(r"^\s*([0-9A-Fa-f]{8})\s+(s__|l__)([A-Za-z0-9_.$]+)\s*$", text, re.M):
        symbols[(prefix, name)] = int(value, 16)
    sections = {}
    for name in {n for (_, n) in symbols}:
        if ("s__", name) in symbols and ("l__", name) in symbols:
            sections[name] = (symbols[("s__", name)], symbols[("l__", name)])
    if "CODE" not in sections:
        raise ValueError("link map is missing s__CODE/l__CODE symbols")
    return sections


def bounds(spec):
    return int(spec["start"], 0), int(spec["end_exclusive"], 0)


def check(path, config_path):
    memory = json.loads(Path(config_path).read_text())
    sections = parse_map(path)
    errors = []
    code_start, code_len = sections["CODE"]
    code_lo, code_hi = bounds(memory["code"])
    if code_start != code_lo:
        errors.append(f"CODE starts at 0x{code_start:04X}, expected 0x{code_lo:04X}")
    if code_start + code_len > code_hi:
        errors.append(f"CODE ends at 0x{code_start + code_len:04X}, past 0x{code_hi:04X}")

    data_lo, data_hi = bounds(memory["globals"])
    resident = ("DATA", "INITIALIZED", "INITIALIZER", "GSINIT", "GSFINAL", "HOME", "DABS", "CABS")
    used_data = []
    for name in resident:
        if name not in sections:
            continue
        start, size = sections[name]
        end = start + size
        if size and (start < data_lo or end > data_hi):
            errors.append(f"{name} 0x{start:04X}-0x{end:04X} escapes globals 0x{data_lo:04X}-0x{data_hi:04X}")
        if size:
            used_data.append((start, end, name))
    stack_lo = int(memory["stack"]["start"], 0)
    stack_top = int(memory["stack"]["top_exclusive"], 0)
    if data_hi > stack_lo:
        errors.append(f"globals reservation ends at 0x{data_hi:04X}, overlaps stack at 0x{stack_lo:04X}")
    guard_lo, guard_hi = bounds(memory["stack_guard"])
    if not (stack_lo == guard_lo < guard_hi <= stack_top):
        errors.append("stack guard must start at stack low and fit inside the stack reservation")
    if guard_hi - guard_lo != int(memory["stack_guard"]["reserved_bytes"]):
        errors.append("stack guard size does not match its reserved_bytes value")
    for start, end, name in used_data:
        if start < stack_top and end > stack_lo:
            errors.append(f"{name} overlaps stack reservation")

    for name in ("clean_background", "visible_screen"):
        lo, hi = bounds(memory[name])
        if lo < 0x4000 or hi > 0x10000 or hi <= lo:
            errors.append(f"{name} is outside CPC fixed-address RAM")
    bg_lo, bg_hi = bounds(memory["clean_background"])
    if "disk_io_buffer" in memory:
        io_lo, io_hi = bounds(memory["disk_io_buffer"])
        if not (bg_lo <= io_lo < io_hi <= bg_hi):
            errors.append("disk I/O buffer must fit inside the clean-background page")
        if io_hi - io_lo != int(memory["disk_io_buffer"]["reserved_bytes"]):
            errors.append("disk I/O buffer reservation size mismatch")
        if io_lo < 0x9000:
            errors.append("disk I/O buffer must start after the compressed chapter payload and outside firmware workspace")
    if "LOADING" in sections:
        start, size = sections["LOADING"]
        if start != bg_lo or not 0 < size <= 0x2700:
            errors.append("LOADING must fit &8000-&A6FF before background reuse")
    screen_lo, screen_hi = bounds(memory["visible_screen"])
    if bg_hi != screen_lo or bg_hi - bg_lo != 0x4000 or screen_hi - screen_lo != 0x4000:
        errors.append("background/screen regions must be adjacent 16 KiB pages")
    boot = memory["bootstrap"]
    boot_start, boot_end = int(boot["start"], 0), int(boot["end_exclusive"], 0)
    if not code_start <= boot_start <= boot_end <= code_start + code_len:
        if boot_start < data_hi and boot_end > data_lo:
            errors.append("bootstrap overlaps resident data")
        else:
            errors.append("bootstrap lies outside linked code")
    if errors:
        raise ValueError("; ".join(errors))
    return {"sections": sections, "code_end": code_start + code_len,
            "data_start": data_lo, "data_end": max((end for _, end, _ in used_data), default=data_lo)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("map", nargs="?", default="build/smoke/SMOKE.map")
    parser.add_argument("--regions", default="cfg/memory.json")
    args = parser.parse_args()
    report = check(ROOT / args.map, ROOT / args.regions)
    data = f"through 0x{report['data_end']-1:04X}" if report["data_end"] > report["data_start"] else "empty"
    print(f"PASS: linked code 0x0100-0x{report['code_end']-1:04X}; resident data {data}; reserved stack and video pages do not overlap.")


if __name__ == "__main__":
    main()
