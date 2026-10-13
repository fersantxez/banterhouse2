#!/usr/bin/env python3
"""Check the deterministic campaign replay CPC disk is loadable at &0100."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
disk = ROOT / "build/physics-campaign/CAMPAIGN.dsk"
binary = ROOT / "build/physics-campaign/CAMPAIGN.bin"
log = ROOT / "build/physics-campaign/CAMPAIGN.bin.log"
checker = ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"
if not all(path.is_file() for path in (disk, binary, log)):
    raise SystemExit("FAIL: falta el DSK/BIN/log de la regresión de campaña CPC")
if "Binary file start = 00000100" not in log.read_text(errors="replace"):
    raise SystemExit("FAIL: la regresión de campaña debe cargar en &0100")
catalog = subprocess.run([str(checker), str(disk), "-l"], capture_output=True, text=True)
if catalog.returncode or not re.search(r"CAMPAIGN\s*\.BIN", catalog.stdout.upper()):
    raise SystemExit("FAIL: el DSK de campaña no se puede catalogar")
print(f"PASS DSK de campaña cargable en &0100 ({len(binary.read_bytes())} bytes); "
      "el hash host esperado está fijado en el fixture Z80")
