#!/usr/bin/env python3
"""Verify a Caprice CPC6128 snapshot against the renderer's independent VRAM oracle."""
import argparse
import hashlib
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--binary", type=Path, default=Path("build/render-cpc/RENDER.bin"))
    parser.add_argument("--expected", type=Path,
                        default=Path("build/render-cpc/render-final-vram.bin"))
    args = parser.parse_args()

    snapshot = args.snapshot.read_bytes()
    binary = args.binary.read_bytes()
    expected = args.expected.read_bytes()
    if len(snapshot) != 256 + 8 * 0x4000:
        raise SystemExit(f"FAIL: unexpected SNA size {len(snapshot)}")
    if len(expected) != 0x4000:
        raise SystemExit(f"FAIL: expected image must be one 16 KiB CPC screen, got {len(expected)}")

    pc = int.from_bytes(snapshot[35:37], "little")
    sp = int.from_bytes(snapshot[33:35], "little")
    crtc_r12 = snapshot[79]
    ram0 = snapshot[256:256 + 0x4000]
    if ram0[0x100:0x120] != binary[:0x20]:
        raise SystemExit("FAIL: snapshot is not running this renderer fixture")
    if ram0[0x3C60] != 0x55:
        raise SystemExit(f"FAIL: fixture did not reach PASS stage (stage={ram0[0x3C60]:02X})")
    if not 0x3C68 <= sp <= 0x3F68:
        raise SystemExit(f"FAIL: stack pointer escaped reserved RAM0 stack (SP={sp:04X})")
    guard = ram0[0x3C68:0x3D68]
    if any(value != 0xA5 for value in guard):
        bad = next(i for i, value in enumerate(guard) if value != 0xA5)
        raise SystemExit(f"FAIL: stack guard changed at {0x3C68 + bad:04X}")

    # R12=20h selects &8000 (physical RAM2); R12=30h selects &C000 (RAM3).
    page = (crtc_r12 & 0x30) >> 4
    if page not in (2, 3):
        raise SystemExit(f"FAIL: CRTC is not showing a fixture page (R12={crtc_r12:02X})")
    actual = snapshot[256 + page * 0x4000:256 + (page + 1) * 0x4000]
    if actual != expected:
        first = next(i for i, pair in enumerate(zip(actual, expected)) if pair[0] != pair[1])
        raise SystemExit(f"FAIL: visible RAM{page} differs at {first:04X}: {actual[first]:02X}!={expected[first]:02X}")
    print(f"PASS: {args.snapshot}; PC={pc:04X}, SP={sp:04X}, CRTC R12={crtc_r12:02X}, "
          f"stage=55, RAM{page} exact 16,384-byte match, 256-byte stack guard intact; "
          f"SHA-256={hashlib.sha256(actual).hexdigest()}")


if __name__ == "__main__":
    main()
