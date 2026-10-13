#!/usr/bin/env python3
"""Build a tiny CPC disk that exercises CAS IN OPEN/DIRECT on CH01.BIN."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/disk-loader-cpc"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "src/platform").mkdir(parents=True, exist_ok=True)
(OUT / "src/main.c").write_bytes((ROOT / "tests/cpc/disk_loader/src/main.c").read_bytes())
(OUT / "src/platform/disk_assets.s").write_bytes((ROOT / "src/platform/disk_assets.s").read_bytes())
(OUT / "src/platform/zx0.s").write_bytes((ROOT / "src/platform/zx0.s").read_bytes())
(OUT / "src/platform/audio_ay.s").write_bytes((ROOT / "src/platform/audio_ay.s").read_bytes())
(OUT / "src/platform/music.s").write_bytes((ROOT / "src/platform/music.s").read_bytes())
cmd = ["make", "-f", "project.mk", "all", f"SRCDIR={OUT}/src", f"OBJDIR={OUT}/obj",
       f"BINFILE={OUT}/LOADER.bin", f"IHXFILE={OUT}/LOADER.ihx", f"CDT={OUT}/LOADER.cdt",
       f"DSK={OUT}/LOADER.dsk", f"TARGET={OUT}/LOADER.dsk", "PROJNAME=DISK_LOADER"]
subprocess.run(cmd, cwd=ROOT, check=True)
subprocess.run([str(ROOT / "tmp/cpctelera/cpctelera/tools/iDSK-0.13/bin/iDSK"),
                str(OUT / "LOADER.dsk"), "-i", str(ROOT / "build/chapter-assets/CH01.BIN"),
                "-t", "1"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f"PASS: isolated loader disk built at {OUT / 'LOADER.dsk'}")
