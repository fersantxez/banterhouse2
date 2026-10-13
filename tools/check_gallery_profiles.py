#!/usr/bin/env python3
"""Check that each gallery DSK contains the exact CPC screen and palette bytes."""
import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/source/canonical"
IDSK = ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"
SCENES = ("01-copias", "02-produccion", "03-calle", "04-purple")


def symbol(map_path, name):
    match = re.search(rf"^\s*([0-9A-F]{{8}})\s+_{re.escape(name)}\s+", map_path.read_text(), re.M | re.I)
    if not match:
        raise SystemExit(f"FAIL: {name} symbol missing from {map_path}")
    return int(match.group(1), 16)


for index, scene in enumerate(SCENES, 1):
    stem = f"GAL{index:02}"
    out = ROOT / "build/gallery" / scene
    binary, disk, map_path = out / f"{stem}.bin", out / f"{stem}.dsk", out / f"{stem}.map"
    log = out / f"{stem}.bin.log"
    if not all(p.is_file() for p in (binary, disk, map_path, log)):
        raise SystemExit(f"FAIL: incomplete gallery profile for {scene}")
    if "Binary file start = 00000100" not in log.read_text(errors="replace"):
        raise SystemExit(f"FAIL: {scene} binary does not load at &0100")
    screen = (SOURCE / f"{scene}.scr").read_bytes()
    palette = bytes(x & 0x1f for x in (SOURCE / f"{scene}.hwpal").read_bytes())
    raw = binary.read_bytes()
    for name, expected in (("gallery_screen", screen), ("gallery_palette", palette)):
        address = symbol(map_path, name)
        offset = address - 0x0100
        if offset < 0 or raw[offset:offset + len(expected)] != expected:
            raise SystemExit(f"FAIL: {scene} {name} bytes differ from canonical source")
    listing = subprocess.run([str(IDSK), str(disk), "-l"], capture_output=True, text=True)
    if listing.returncode or not re.search(rf"{stem}\s*\.BIN", listing.stdout.upper()):
        raise SystemExit(f"FAIL: {scene} DSK catalog lacks {stem}.BIN")
    print(f"PASS: {scene} raw screen+palette linked byte-exactly; {len(raw)}-byte BIN, DSK readable; "
          f"screen SHA-256 {hashlib.sha256(screen).hexdigest()}")
