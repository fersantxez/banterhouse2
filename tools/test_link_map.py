#!/usr/bin/env python3
"""Negative map fixtures: overflow, stack overlap and invalid bootstrap are rejected."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_link_map import check  # noqa: E402
GLOBALS_START = int(json.loads((ROOT / "cfg/memory.json").read_text())["globals"]["start"], 0)


BASE = """     {code_start} s__CODE
     {code_size} l__CODE
     {data_start} s__DATA
     {data_size} l__DATA
     {init_start} s__INITIALIZED
     {init_size} l__INITIALIZED
     {ctor_start} s__INITIALIZER
     {ctor_size} l__INITIALIZER
"""


def fixture(root, name, code_start="00000100", code_size="00000100", data_start=None,
            data_size="00000020", init_start=None, init_size="00000000",
            ctor_start=None, ctor_size="00000000", bootstrap=None):
    c = json.loads((ROOT / "cfg/memory.json").read_text())
    globals_start = int(c["globals"]["start"], 0)
    globals_start_hex = f"{globals_start:08X}"
    if data_start is None:
        data_start = globals_start_hex
    if init_start is None:
        init_start = f"{globals_start + int(data_size, 16):08X}"
    if ctor_start is None:
        ctor_start = init_start
    m = root / f"{name}.map"
    m.write_text(BASE.format(code_start=code_start, code_size=code_size, data_start=data_start,
                             data_size=data_size, init_start=init_start, init_size=init_size,
                             ctor_start=ctor_start, ctor_size=ctor_size))
    if bootstrap:
        c["bootstrap"]["start"], c["bootstrap"]["end_exclusive"] = bootstrap
    cfg = root / f"{name}.json"
    cfg.write_text(json.dumps(c))
    return m, cfg


def must_reject(m, cfg, expected):
    try:
        check(m, cfg)
    except ValueError as exc:
        if expected not in str(exc):
            raise AssertionError(f"{m.name}: expected {expected!r}, got {exc}") from exc
    else:
        raise AssertionError(f"{m.name}: invalid layout accepted")


with tempfile.TemporaryDirectory(prefix="banterhouse2-map-") as td:
    root = Path(td)
    valid, cfg = fixture(root, "valid")
    check(valid, cfg)
    outside, cfg = fixture(root, "code-outside", code_size="00008000")
    must_reject(outside, cfg, "CODE ends")
    overlap, cfg = fixture(root, "stack-overlap", init_start="00007cf0", init_size="00000004",
                           ctor_start="00007cf4")
    must_reject(overlap, cfg, "escapes globals")
    bad_boot, cfg = fixture(root, "bootstrap-outside", bootstrap=("0x7f00", "0x7f01"))
    must_reject(bad_boot, cfg, "bootstrap lies outside linked code")
    boot_over_data, cfg = fixture(root, "bootstrap-over-data", bootstrap=(f"0x{GLOBALS_START:04x}", f"0x{GLOBALS_START + 1:04x}"))
    must_reject(boot_over_data, cfg, "bootstrap overlaps resident data")
print("PASS: valid map accepted; code overflow, data/stack escape, bootstrap outside CODE, and bootstrap/data overlap rejected.")
