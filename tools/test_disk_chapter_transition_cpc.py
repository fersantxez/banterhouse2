#!/usr/bin/env python3
"""Build an isolated CPC regression disk for two AMSDOS chapter loads."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/disk-chapter-transition-cpc"
SRC = OUT / "src"
OUT_REL = OUT.relative_to(ROOT)
(SRC / "platform").mkdir(parents=True, exist_ok=True)
shutil.copyfile(ROOT / "tests/cpc/disk_loader/src/transition.c", SRC / "main.c")
for name in ("disk_assets.s", "zx0.s"):
    source = (ROOT / "src/platform" / name).read_text()
    if name == "disk_assets.s":
        def ga_mark(hwc: int, preserve_bc: bool = False) -> str:
            prefix = "    push bc\n" if preserve_bc else ""
            suffix = "    pop bc\n" if preserve_bc else ""
            return (prefix + "    ld bc, #0x7f00\n    ld a, #0x10\n"
                    "    out (c), a\n" + f"    ld a, #{hwc}\n" +
                    "    out (c), a\n" + suffix)
        source = source.replace("call #0xbcce               ; KL INIT BACK",
                                "call #0xbcce               ; KL INIT BACK\n" + ga_mark("0x12"))
        source = source.replace("call #0xbcd4               ; KL FIND COMMAND: HL=name -> HL=proc, C=ROM cfg",
                                "call #0xbcd4               ; KL FIND COMMAND: HL=name -> HL=proc, C=ROM cfg\n" + ga_mark("0x0c", True))
        source = source.replace("call #0x001b               ; KL FAR PCHL (HL=proc, C=ROM cfg)",
                                "call #0x001b               ; KL FAR PCHL (HL=proc, C=ROM cfg)\n" + ga_mark("0x13"))
        if "ld bc, #0x7f00" not in source:
            raise SystemExit("FAIL: firmware call probes were not inserted")
    (SRC / "platform" / name).write_text(source)

subprocess.run([
    "make", "-f", "project.mk", "all", f"SRCDIR={SRC}", f"OBJDIR={OUT / 'obj'}",
    f"BINFILE={OUT_REL}/TRANSITI.bin", f"IHXFILE={OUT_REL}/TRANSITI.ihx",
    f"CDT={OUT_REL}/TRANSITI.cdt", f"DSK={OUT_REL}/TRANSITION.dsk",
    f"TARGET={OUT_REL}/TRANSITION.dsk", "PROJNAME=DISK_TRANSITI",
], cwd=ROOT, check=True)

subprocess.run([
    "python3", str(ROOT / "tools/attach_chapter_assets.py"), str(OUT / "TRANSITION.dsk")
], cwd=ROOT, check=True)
print(f"PASS: isolated CH01 → background overwrite → CH02 → ZX0 disk built at {OUT / 'TRANSITION.dsk'}")
