#!/usr/bin/env python3
"""Host checks for the exact bytes imported into the CPC binary."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STUDIES = ROOT / "assets/source/canonical"
ZX = ROOT / "tmp/research-tools/ZX0/src"
spec = importlib.util.spec_from_file_location("runtime_assets", ROOT / "tools/build_runtime_assets.py")
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def read_symbols():
    source = (ROOT / "src/generated/runtime_assets.s").read_text()
    found = {}
    parts = re.split(r"(?m)^_([A-Za-z0-9_]+)::\s*$", source)
    for i in range(1, len(parts), 2):
        values = re.findall(r"0x([0-9a-fA-F]{2})", parts[i + 1].split(".globl", 1)[0])
        found[parts[i]] = bytes(int(x, 16) for x in values)
    return found


def reconstruct_tile_background(tiles, mapping):
    screen = bytearray(16384)
    tile_count = len(tiles) // 32
    require(len(mapping) == 500 and len(tiles) % 32 == 0,
            "tile/map dimensions are not 20x25 and complete 32-byte tiles")
    for ty in range(25):
        for tx in range(20):
            tile_id = mapping[ty * 20 + tx]
            require(tile_id < tile_count,
                    f"tile map index {ty*20+tx} references absent tile {tile_id}")
            tile = tiles[tile_id * 32:(tile_id + 1) * 32]
            for row in range(8):
                y = ty * 8 + row
                address = (y & 7) * 0x800 + (y >> 3) * 80 + tx * 4
                screen[address:address + 4] = tile[row * 4:row * 4 + 4]
    return bytes(screen)


def main():
    for byte in range(256):
        require(assets.pack_mode0(*assets.unpack_mode0(byte)) == byte,
                f"Mode 0 byte does not round-trip: {byte:02X}")

    generated = ROOT / "src/generated/runtime_assets.s"
    if not generated.exists():
        subprocess.run(["python3", str(ROOT / "tools/build_runtime_assets.py")], check=True)
    symbols = read_symbols()
    build_manifest = json.loads((ROOT / "src/generated/runtime_assets.json").read_text())
    slugs = ("01-copias", "02-produccion", "03-calle", "04-purple")
    total_raw = total_packed = 0
    for index, slug in enumerate(slugs, 1):
        raw = (STUDIES / f"{slug}.background.scr").read_bytes()
        packed = symbols[f"bg{index}"]
        runtime_raw = assets.clean_background(index-1)
        assets.validate_screen(raw, slug)
        full_screen = (STUDIES / f"{slug}.scr").read_bytes()
        assets.validate_screen(full_screen, f"{slug}.scr")
        firmware_palette = (STUDIES / f"{slug}.fwpal").read_bytes()
        hardware_palette = (STUDIES / f"{slug}.hwpal").read_bytes()
        assets.validate_palette(firmware_palette, f"{slug}.fwpal", 26)
        assets.validate_palette(hardware_palette, f"{slug}.hwpal", 31)
        tiles = (STUDIES / f"{slug}.tiles.bin").read_bytes()
        mapping = (STUDIES / f"{slug}.map.bin").read_bytes()
        assets.validate_tiles_and_map(tiles, mapping, slug)
        require(reconstruct_tile_background(tiles, mapping) == raw,
                f"{slug}: tile/map reconstruction differs from the CPC background")
        resource = next(item for item in build_manifest["resources"] if item["id"] == index)
        require(resource["source_sha256"] == hashlib.sha256(raw).hexdigest(),
                f"{slug}: generated manifest source hash differs")
        require(resource["runtime_sha256"] == hashlib.sha256(runtime_raw).hexdigest(), f"{slug}: runtime transform differs")
        with tempfile.TemporaryDirectory(prefix="banterhouse2-zx0-") as tmp:
            out = Path(tmp) / "screen.scr"
            packed_path = Path(tmp)/"runtime.zx0"
            packed_path.write_bytes(packed)
            subprocess.run([str(ZX / "dzx0"), str(packed_path), str(out)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            require(out.read_bytes() == runtime_raw, f"{slug}: ZX0 round-trip differs")
        total_raw += len(raw)
        total_packed += len(packed)

    for source, key in (("g_pitu.masked.bin", "pitu"),
                        ("g_pitu_walk.masked.bin", "pitu_walk"),
                        ("g_alberto.masked.bin", "alberto")):
        original = (STUDIES / source).read_bytes()
        assets.validate_sprite(original, source)
        require(assets.encode_variant(original, False, 0) == original,
                f"{key}: even/right sprite changed during import")
        for side, flip in (("r", False), ("l", True)):
            for shift in (0, 1):
                name = f"{key}_{side}_{shift}"
                expected = assets.encode_variant(original, flip, shift)
                require(symbols.get(name) == expected, f"{name}: aligned variant differs")

    for index, slug in enumerate(slugs, 1):
        expected = bytes(x & 0x1f for x in (STUDIES / f"{slug}.hwpal").read_bytes())
        require(symbols.get(f"palette{index}") == expected, f"palette{index}: hardware inks differ")
    print(f"PASS: 256 Mode 0 byte round-trips; 3 canonical actors × 4 alignment/direction variants; "
          f"4 exact ZX0 screens ({total_raw} -> {total_packed} bytes); 4 palettes.")


if __name__ == "__main__":
    main()
