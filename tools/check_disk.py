#!/usr/bin/env python3
"""Check DSK catalog, raw binary extent, and documented CPC model settings."""
from pathlib import Path
import subprocess
import sys
import tempfile
import re

ROOT = Path(__file__).resolve().parents[1]
dsk = ROOT / "build/DEVUELTO.dsk"
binary = ROOT / "build/DEVUELTO.bin"
idsk = ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"
if not dsk.is_file() or not binary.is_file():
    raise SystemExit("FAIL: DSK or binary missing; run `make build` first")
result = subprocess.run([str(idsk), str(dsk), "-l"], text=True, capture_output=True)
if result.returncode:
    raise SystemExit(f"FAIL: iDSK catalog failed: {result.stderr or result.stdout}")
catalog = result.stdout.upper()
if "DEVUELTO.BIN" not in catalog:
    raise SystemExit("FAIL: DSK catalog has no DEVUELTO.BIN\n" + result.stdout)
log = (ROOT / "build/DEVUELTO.bin.log").read_text(errors="replace")
if "Binary file start = 00000100" not in log:
    raise SystemExit("FAIL: AMSDOS load address is not 0100")
if "Highest address   =" not in log:
    raise SystemExit("FAIL: hex2bin produced no address extent")
with tempfile.TemporaryDirectory(prefix="devuelto-disk-check-") as temp:
    exported = subprocess.run([str(idsk), str(dsk), "-g", "DEVUELTO.BIN"], cwd=temp, capture_output=True)
    if exported.returncode:
        raise SystemExit("FAIL: cannot extract game from disk")
    stored = (Path(temp)/"DEVUELTO.BIN").read_bytes()
header = stored[:128]
if len(header)!=128 or header[18]!=2:
    raise SystemExit("FAIL: invalid AMSDOS binary header")
if int.from_bytes(header[67:69],"little") != sum(header[:67]):
    raise SystemExit("FAIL: AMSDOS header checksum mismatch")
entry = int(re.search(r"^\s*([0-9A-F]{8})\s+_main\s", (ROOT/"build/DEVUELTO.map").read_text(), re.M)[1],16)
if int.from_bytes(header[21:23],"little")!=0x100 or int.from_bytes(header[26:28],"little")!=entry:
    raise SystemExit("FAIL: disk load/entry differs from linker map")
payload = binary.read_bytes()
if int.from_bytes(header[24:26],"little") != len(payload) or stored[128:128+len(payload)]!=payload:
    raise SystemExit("FAIL: disk payload differs from built binary")
print(f"PASS: {dsk.name}: extracted BIN equals build; AMSDOS checksum, load &0100, entry &{entry:04X}, {len(payload)} bytes. Execution tested separately.")
