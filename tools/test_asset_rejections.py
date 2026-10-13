#!/usr/bin/env python3
"""Negative fixtures for CPC source asset limits required by A02."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runtime_assets", ROOT / "tools/build_runtime_assets.py")
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


def reject(label, call, fragment):
    try:
        call()
    except ValueError as exc:
        if fragment not in str(exc):
            raise SystemExit(f"FAIL: {label}: expected {fragment!r}; got {exc}") from exc
    else:
        raise SystemExit(f"FAIL: {label}: invalid input was accepted")


reject("17-entry palette", lambda: assets.validate_palette(bytes(17), "bad-palette", 26), "exactly 16")
reject("out-of-range firmware ink", lambda: assets.validate_palette(bytes([27]) + bytes(15), "bad-ink", 26), "exceeds")
reject("impossible screen dimensions", lambda: assets.validate_screen(bytes(16385), "wide-screen"), "exactly 16384")
reject("truncated tile", lambda: assets.validate_tiles_and_map(bytes(31), bytes(500), "short-tile"), "complete 32-byte")
reject("out-of-range tile index", lambda: assets.validate_tiles_and_map(bytes(32), bytes([1]) * 500, "bad-map"), "references tile")
partial_mask = bytearray(512)
partial_mask[0] = 0x80
reject("incoherent partial mask", lambda: assets.validate_sprite(partial_mask, "partial-mask"), "partial transparency")
overlap_mask = bytearray(512)
overlap_mask[0] = 0xff
overlap_mask[1] = 0xff
reject("mask and pixel overlap", lambda: assets.validate_sprite(overlap_mask, "overlap-mask"), "bits overlap")
reject("truncated sprite frame", lambda: assets.validate_sprite(bytes(510), "short-frame"), "exactly 512")
print("PASS: 8 invalid palette, ink, screen, tile, map and mask/frame fixtures rejected with field-specific errors.")
