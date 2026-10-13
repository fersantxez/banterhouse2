#!/usr/bin/env python3
"""Build and validate the H1 seal-window A/B CPC disks."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CPCT = ROOT / "tmp/cpctelera/cpctelera"
IDSK = CPCT / "tools/iDSK-0.13/bin/iDSK"


def run(command):
    subprocess.run([str(x) for x in command], cwd=ROOT, check=True)


def validate_disk(disk: Path, binary: Path):
    listing = subprocess.run([str(IDSK), str(disk), "-l"], cwd=ROOT,
                             text=True, capture_output=True, check=True).stdout
    if "DEVUELTO.BIN" not in listing.upper():
        raise SystemExit(f"FAIL: {disk} has no DEVUELTO.BIN")
    with tempfile.TemporaryDirectory(prefix="h1-disk-check-") as tmp:
        subprocess.run([str(IDSK), str(disk), "-g", "DEVUELTO.BIN"],
                       cwd=tmp, capture_output=True, check=True)
        payload = (Path(tmp) / "DEVUELTO.BIN").read_bytes()
    raw = binary.read_bytes()
    header, body = payload[:128], payload[128:]
    if len(header) != 128 or header[18] != 2:
        raise SystemExit(f"FAIL: invalid AMSDOS header in {disk}")
    if int.from_bytes(header[67:69], "little") != sum(header[:67]):
        raise SystemExit(f"FAIL: AMSDOS checksum in {disk}")
    if int.from_bytes(header[21:23], "little") != 0x0100:
        raise SystemExit(f"FAIL: {disk} load address is not 0x0100")
    if int.from_bytes(header[24:26], "little") != len(raw) or body[:len(raw)] != raw:
        raise SystemExit(f"FAIL: {disk} payload differs from {binary}")


def build(name: str, window: int):
    out = ROOT / "build/h1" / name
    src, obj = out / "src", out / "obj"
    run(["python3", "tools/build_m1_source.py", "--output", str(src)])
    run(["make", "-f", "project.mk", "all", f"SRCDIR={src}", f"OBJDIR={obj}",
         f"BINFILE={out}/DEVUELTO.bin", f"IHXFILE={out}/DEVUELTO.ihx",
         f"CDT={out}/DEVUELTO.cdt", f"DSK={out}/DEVUELTO.dsk",
         f"TARGET={out}/DEVUELTO.dsk", f"PROJNAME=H1{name}", "M1_ONLY=1",
         f"M1_SEAL_WINDOW={window}", "M1_SEAL_RECOVERY=8"])
    run(["python3", "tools/check_link_map.py", f"{out}/DEVUELTO.map"])
    validate_disk(out / "DEVUELTO.dsk", out / "DEVUELTO.bin")
    return {
        "variant": name,
        "active_ticks": window,
        "recovery_ticks": 8,
        "next_action_tick": window + 8,
        "machine_initial_wait_ticks": 50,
        "binary_bytes": (out / "DEVUELTO.bin").stat().st_size,
        "disk_bytes": (out / "DEVUELTO.dsk").stat().st_size,
        "binary_sha256": hashlib.sha256((out / "DEVUELTO.bin").read_bytes()).hexdigest(),
        "disk_sha256": hashlib.sha256((out / "DEVUELTO.dsk").read_bytes()).hexdigest(),
        "disk_payload_verified": True,
        "link_map_verified": True
    }


def main():
    results = {
        "task": "T14/H1",
        "scope": "A/B candidates only; no human approval is recorded by this tool",
        "variants": [build("A", 6), build("B", 8)]
    }
    print(json.dumps(results, indent=2))
    (ROOT / "build/h1/results.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
