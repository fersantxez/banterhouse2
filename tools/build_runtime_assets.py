#!/usr/bin/env python3
"""Build CPC runtime resources from the checked-in native Mode 0 studies."""
from pathlib import Path
import hashlib
import json
import sys
import subprocess
import tempfile
from build_machine_cleanup import clean_background

ROOT = Path(__file__).resolve().parents[1]
STUDIES = ROOT / "assets/source/canonical"
OUT = ROOT / "src/generated"


def unpack_mode0(byte):
    p0 = ((byte >> 7) & 1) | ((byte >> 2) & 2) | ((byte >> 3) & 4) | ((byte << 2) & 8)
    p1 = ((byte >> 6) & 1) | ((byte >> 1) & 2) | ((byte >> 2) & 4) | ((byte << 3) & 8)
    return p0, p1


def pack_mode0(p0, p1):
    return (((p0 & 1) << 7) | ((p1 & 1) << 6) |
            ((p0 & 2) << 2) | ((p1 & 2) << 1) |
            ((p0 & 4) << 3) | ((p1 & 4) << 2) |
            ((p0 & 8) >> 2) | ((p1 & 8) >> 3))


def validate_screen(raw, name):
    if len(raw) != 16384:
        raise ValueError(f"{name}: screen must be exactly 16384 bytes, got {len(raw)}")


def validate_palette(raw, name, limit):
    if len(raw) != 16:
        raise ValueError(f"{name}: palette must contain exactly 16 inks, got {len(raw)}")
    for index, value in enumerate(raw):
        ink = value & 0x1f
        if ink > limit:
            raise ValueError(f"{name}[{index}]: ink {ink} exceeds classic CPC range 0..{limit}")


def validate_tiles_and_map(tiles, mapping, name):
    if len(tiles) == 0 or len(tiles) % 32:
        raise ValueError(f"{name}: tile data must contain complete 32-byte Mode 0 tiles")
    count = len(tiles) // 32
    if count > 256:
        raise ValueError(f"{name}: {count} tiles exceed one-byte map indices")
    if len(mapping) != 20 * 25:
        raise ValueError(f"{name}: map must be exactly 500 indices for a 20x25 screen")
    for position, tile_id in enumerate(mapping):
        if tile_id >= count:
            raise ValueError(f"{name}: map index {position} references tile {tile_id}, count is {count}")


def validate_sprite(raw, name):
    if len(raw) != 512:
        raise ValueError(f"{name}: 16x32 masked sprite must be exactly 512 bytes, got {len(raw)}")
    for offset in range(0, len(raw), 2):
        mask, pixels = raw[offset], raw[offset + 1]
        for mask_pen, pixel_pen in zip(unpack_mode0(mask), unpack_mode0(pixels)):
            if mask_pen not in (0, 15):
                raise ValueError(f"{name}: partial transparency mask at byte {offset}")
            if pixel_pen & mask_pen:
                raise ValueError(f"{name}: masked pixel bits overlap at byte {offset}")


def decode_sprite(raw):
    pixels = []
    opaque = []
    for y in range(32):
        rowp, rowo = [], []
        for x in range(8):
            mask, colour = raw[y * 16 + x * 2:y * 16 + x * 2 + 2]
            mp = unpack_mode0(mask)
            cp = unpack_mode0(colour)
            rowp.extend(cp)
            rowo.extend((mp[0] != 15, mp[1] != 15))
        pixels.append(rowp)
        opaque.append(rowo)
    return pixels, opaque


def encode_variant(raw, flip, shift):
    pixels, opaque = decode_sprite(raw)
    width = 9 if shift else 8
    out = bytearray()
    for y in range(32):
        p = pixels[y][::-1] if flip else pixels[y]
        o = opaque[y][::-1] if flip else opaque[y]
        destp, desto = [], []
        for x in range(width * 2):
            source_x = x - shift
            destp.append(p[source_x] if 0 <= source_x < 16 else 0)
            desto.append(o[source_x] if 0 <= source_x < 16 else False)
        for x in range(width):
            out.append(pack_mode0(15 if not desto[x*2] else 0,
                                  15 if not desto[x*2+1] else 0))
            out.append(pack_mode0(destp[x*2], destp[x*2+1]))
    return bytes(out)


def emit_symbol(f, name, data):
    f.write(f".globl _{name}\n_{name}::\n")
    for i in range(0, len(data), 16):
        f.write("  .db " + ",".join(f"0x{x:02x}" for x in data[i:i+16]) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records, asm = [], []
    for index, slug in enumerate(("01-copias", "02-produccion", "03-calle", "04-purple"), 1):
        raw = (STUDIES / f"{slug}.background.scr").read_bytes()
        validate_screen(raw, slug)
        tiles = (STUDIES / f"{slug}.tiles.bin").read_bytes()
        mapping = (STUDIES / f"{slug}.map.bin").read_bytes()
        validate_tiles_and_map(tiles, mapping, slug)
        validate_palette((STUDIES / f"{slug}.fwpal").read_bytes(), f"{slug}.fwpal", 26)
        validate_palette((STUDIES / f"{slug}.hwpal").read_bytes(), f"{slug}.hwpal", 31)
        runtime_raw = clean_background(index-1)
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)/'screen.scr'
            dest = Path(folder)/'screen.zx0'
            source.write_bytes(runtime_raw)
            subprocess.run([str(ROOT/'tmp/research-tools/ZX0/src/zx0'), '-f', str(source), str(dest)], check=True, stdout=subprocess.DEVNULL)
            packed = dest.read_bytes()
        chapter_dir = ROOT / "build/chapter-assets"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        (chapter_dir / f"CH{index:02d}.BIN").write_bytes(packed)
        emit_symbol_buffer = []
        import io
        io_buf = io.StringIO()
        emit_symbol(io_buf, f"bg{index}", packed)
        asm.append(io_buf.getvalue())
        records.append({"id": index, "source": f"assets/source/canonical/{slug}.background.scr",
                        "source_sha256": hashlib.sha256(raw).hexdigest(),
                        "runtime_sha256": hashlib.sha256(runtime_raw).hexdigest(),
                        "transform": "remove study-only machines; draw live targets at runtime",
                        "bytes": len(raw), "packed_bytes": len(packed),
                        "tile_bytes": len(tiles), "map_bytes": len(mapping)})

    for source, key in (("g_pitu.masked.bin", "pitu"),
                        ("g_pitu_walk.masked.bin", "pitu_walk"),
                        ("g_alberto.masked.bin", "alberto")):
        raw = (STUDIES / source).read_bytes()
        validate_sprite(raw, source)
        for flip, side in ((False, "r"), (True, "l")):
            for shift in (0, 1):
                name = f"{key}_{side}_{shift}"
                data = encode_variant(raw, flip, shift)
                emit_symbol_buffer = []
                import io
                io_buf = io.StringIO()
                emit_symbol(io_buf, name, data)
                asm.append(io_buf.getvalue())
                records.append({"id": name, "source": f"assets/source/canonical/{source}",
                                "source_sha256": hashlib.sha256(raw).hexdigest(),
                        "runtime_sha256": hashlib.sha256(runtime_raw).hexdigest(),
                        "transform": "remove study-only machines; draw live targets at runtime",
                                "bytes": len(data), "width_bytes": 8 + shift,
                                "height": 32})

    for index, slug in enumerate(("01-copias", "02-produccion", "03-calle", "04-purple"), 1):
        palette = bytes(value & 0x1f for value in (STUDIES / f"{slug}.hwpal").read_bytes())
        validate_palette(palette, f"{slug}.hwpal", 31)
        import io
        io_buf = io.StringIO()
        emit_symbol(io_buf, f"palette{index}", palette)
        asm.append(io_buf.getvalue())

    # A 14x17 native copier, using exactly the study's construction and inks.
    import build_cpc_screen_studies as art
    canvas = art.Canvas(255)
    art.machine(canvas, 0, 17, 3)
    for shift in (0, 1):
        data = bytearray()
        width = 7 + shift
        for y in range(17):
            for xb in range(width):
                pixels=[]
                for pixel in range(2):
                    x=xb*2+pixel-shift
                    pixels.append(canvas.p[y*160+x] if 0<=x<14 else 255)
                data.extend((pack_mode0(*(15 if p==255 else 0 for p in pixels)),
                             pack_mode0(*(0 if p==255 else p for p in pixels))))
        io_buf=io.StringIO()
        emit_symbol(io_buf, 'copier_odd' if shift else 'copier_even', data)
        asm.append(io_buf.getvalue())

    (OUT / "runtime_assets.s").write_text("\n.area _CODE\n" + "\n".join(asm))
    manifest = {"format": "mode0-v1", "background_compression": "ZX0 standard forward",
                "resources": records}
    (OUT / "runtime_assets.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(OUT / "runtime_assets.s"),
                      "backgrounds": records[:4],
                      "sprite_variants": len(records)-4,
                      "assembly_bytes": (OUT / "runtime_assets.s").stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
