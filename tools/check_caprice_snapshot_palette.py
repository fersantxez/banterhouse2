#!/usr/bin/env python3
"""Compare the Gate Array ink state saved by Caprice32 with one canonical palette."""
import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENES = ("01-copias", "02-produccion", "03-calle", "04-purple")
SNA_HEADER_BYTES = 256
GA_INK_OFFSET = 47  # t_SNA_header: packed; ga_pen follows 46 bytes of CPU state.
INK_COUNT = 16


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", choices=SCENES)
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()

    check_palette(args.scene, args.snapshot)


def check_palette(scene, snapshot):
    data = Path(snapshot).read_bytes()
    if len(data) < SNA_HEADER_BYTES or data[:8] != b"MV - SNA":
        raise SystemExit("FAIL: file is not a Caprice32/Arnold SNA snapshot")
    if data[16] != 3 or len(data) != SNA_HEADER_BYTES + 128 * 1024:
        raise SystemExit("FAIL: unsupported snapshot version or RAM image size")

    actual = data[GA_INK_OFFSET:GA_INK_OFFSET + INK_COUNT]
    palette_file = ROOT / "assets/source/canonical" / f"{scene}.hwpal"
    raw_expected = palette_file.read_bytes()
    if len(raw_expected) != INK_COUNT:
        raise SystemExit(f"FAIL: canonical palette has {len(raw_expected)} bytes")
    expected = bytes(value & 0x1F for value in raw_expected)
    if actual != expected:
        raise SystemExit(
            f"FAIL: {scene} Gate Array inks differ: "
            f"expected={expected.hex()} actual={actual.hex()}"
        )
    print(
        f"PASS: Caprice32 snapshot Gate Array inks match {scene}; "
        f"inks={actual.hex()} snapshot_sha256={hashlib.sha256(data).hexdigest()}"
    )


if __name__ == "__main__":
    main()
