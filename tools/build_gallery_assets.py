#!/usr/bin/env python3
"""Prepare one self-contained native-screen CPC gallery profile from frozen assets."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/source/canonical"
SCENES = ("01-copias", "02-produccion", "03-calle", "04-purple")


def emit_data(path, label, data):
    with path.open("w") as out:
        out.write(f".globl _{label}\n_{label}::\n")
        for start in range(0, len(data), 16):
            out.write("  .db " + ",".join(f"0x{value:02x}" for value in data[start:start + 16]) + "\n")


parser = argparse.ArgumentParser()
parser.add_argument("scene", choices=SCENES)
parser.add_argument("--out", required=True, help="build-only output directory")
args = parser.parse_args()
output = (ROOT / args.out).resolve()
output.mkdir(parents=True, exist_ok=True)
screen_path = SOURCE / f"{args.scene}.scr"
palette_path = SOURCE / f"{args.scene}.hwpal"
screen, palette = screen_path.read_bytes(), palette_path.read_bytes()
if len(screen) != 16384:
    raise SystemExit(f"FAIL: {args.scene} raw screen is {len(screen)} B, expected 16384")
if len(palette) != 16 or any(not 0x40 <= ink <= 0x5f for ink in palette):
    raise SystemExit(f"FAIL: {args.scene} CPC palette must contain 16 classic hardware inks")
emit_data(output / "screen.s", "gallery_screen", screen)
emit_data(output / "palette.s", "gallery_palette", bytes(ink & 0x1f for ink in palette))
record = {
    "scene": args.scene,
    "screen_bytes": len(screen),
    "screen_sha256": hashlib.sha256(screen).hexdigest(),
    "palette_bytes": len(palette),
    "palette_sha256": hashlib.sha256(palette).hexdigest(),
    "source_root": "assets/source/canonical",
    "runtime_input": "full raw .scr + classic CPC hardware palette",
}
(output / "gallery.json").write_text(json.dumps(record, indent=2) + "\n")
print(f"PASS: prepared {args.scene}: 16384-byte screen and 16-ink palette")
