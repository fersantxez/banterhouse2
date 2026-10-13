#!/usr/bin/env python3
"""Verify AMSDOS game and four streamable chapter files in a campaign DSK."""
import argparse
import hashlib
import re
import subprocess
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDSK = ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"
sys.path.insert(0, str(ROOT / "tools"))
from check_link_map import check as check_memory  # noqa: E402
parser = argparse.ArgumentParser()
parser.add_argument("disk", type=Path)
parser.add_argument("binary", type=Path)
parser.add_argument("map", type=Path)
args = parser.parse_args()
disk, binary, mapping = (p.resolve() for p in (args.disk, args.binary, args.map))
listing = subprocess.run([str(IDSK), str(disk), "-l"], capture_output=True, check=True).stdout.decode("mac_roman", errors="replace").upper()
normalized_listing = re.sub(r"\s+", "", listing)
required = ["DEVUELTO.BIN", *(f"CH{i:02d}.BIN" for i in range(1, 5))]
missing = [name for name in required if name not in normalized_listing]
if missing:
    raise SystemExit(f"FAIL: campaign DSK missing {missing}\n{listing}")
with tempfile.TemporaryDirectory(prefix="campaign-dsk-check-") as tmp:
    for name in required:
        subprocess.run([str(IDSK), str(disk), "-g", name], cwd=tmp, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    game = (Path(tmp) / "DEVUELTO.BIN").read_bytes()
    chapter_files = [(Path(tmp) / f"CH{i:02d}.BIN").read_bytes() for i in range(1, 5)]
if game[18] != 2 or int.from_bytes(game[21:23], "little") != 0x0100:
    raise SystemExit("FAIL: game file is not an AMSDOS binary loaded at &0100")
if int.from_bytes(game[67:69], "little") != sum(game[:67]):
    raise SystemExit("FAIL: game AMSDOS header checksum")
payload = binary.read_bytes()
if int.from_bytes(game[24:26], "little") != len(payload) or game[128:128+len(payload)] != payload:
    raise SystemExit("FAIL: DSK program bytes differ from linker BIN")
memory_report = check_memory(mapping, ROOT / "cfg/memory.json")
code_end = memory_report["code_end"]
for chapter, content in enumerate(chapter_files, 1):
    source = (ROOT / f"build/chapter-assets/CH{chapter:02d}.BIN").read_bytes()
    if content[18] != 2 or int.from_bytes(content[67:69], "little") != sum(content[:67]):
        raise SystemExit(f"FAIL: CH{chapter:02d}.BIN AMSDOS header")
    if content[128:128+len(source)] != source:
        raise SystemExit(f"FAIL: CH{chapter:02d}.BIN content mismatch")
    if len(source) > 0x1000:
        raise SystemExit(f"FAIL: CH{chapter:02d}.BIN compressed payload does not fit &8000-&8FFF before the disk I/O buffer")
print(f"PASS: 24-arena campaign DSK contains exact game ({len(payload)} B) and four AMSDOS chapter assets; code ends &{code_end-1:04X}; disk SHA-256 {hashlib.sha256(disk.read_bytes()).hexdigest()}")
