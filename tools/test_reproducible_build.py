#!/usr/bin/env python3
"""Build the isolated CPC boot profile in two empty trees and compare outputs."""
import hashlib
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(name, root):
    out = root / name
    obj = out / "obj"
    values = {
        "SRCDIR": "tests/cpc/smoke/src",
        "OBJDIR": str(obj.relative_to(ROOT)),
        "BINFILE": str((out / "SMOKE.bin").relative_to(ROOT)),
        "IHXFILE": str((out / "SMOKE.ihx").relative_to(ROOT)),
        "CDT": str((out / "SMOKE.cdt").relative_to(ROOT)),
        "DSK": str((out / "SMOKE.dsk").relative_to(ROOT)),
        "TARGET": str((out / "SMOKE.dsk").relative_to(ROOT)),
        "PROJNAME": "SMOKE-" + name,
    }
    args = ["/usr/bin/make", "-f", "project.mk", "all"] + [f"{key}={value}" for key, value in values.items()]
    subprocess.run(args, cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return out


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


with tempfile.TemporaryDirectory(prefix="banterhouse2-repro-", dir=ROOT / "build") as td:
    root = Path(td)
    a, b = build("a", root), build("b", root)
    for name in ("SMOKE.bin", "SMOKE.dsk"):
        ah, bh = digest(a / name), digest(b / name)
        if ah != bh:
            raise SystemExit(f"FAIL: {name} differs between clean builds: {ah} != {bh}")
        print(f"PASS: {name} reproducible SHA-256 {ah}")
