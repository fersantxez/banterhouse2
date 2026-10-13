#!/usr/bin/env python3
"""Build four *static* CPC Mode 0 studies, with no image-generation dependency.

Standard-library only. Draw on a 160x200 ink-index surface, encode CPC VRAM,
decode it back, and export indexed PNGs. This is a host art pipeline, not a
Z80 game renderer. Original Banterhouse inputs are opened read-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'cpc-studies'
WIDTH, HEIGHT = 160, 200
BASE_PALETTE = [0, 26, 11, 20, 9, 13, 18, 22, 25, 3, 7, 17, 15, 16, 12, 1]
HW = [0x14, 0x04, 0x15, 0x1C, 0x18, 0x1D, 0x0C, 0x05, 0x0D,
      0x16, 0x06, 0x17, 0x1E, 0, 0x1F, 0x0E, 0x07, 0x0F,
      0x12, 0x02, 0x13, 0x1A, 0x19, 0x1B, 0x0A, 0x03, 0x0B]
FONT = {
    'A':'010101111101101', 'B':'110101110101110', 'C':'011100100100011',
    'D':'110101101101110', 'E':'111100110100111', 'F':'111100110100100',
    'G':'011100101101011', 'H':'101101111101101', 'I':'111010010010111',
    'J':'001001001101010', 'K':'101101110101101', 'L':'100100100100111',
    'M':'101111111101101', 'N':'110101101101101', 'O':'010101101101010',
    'P':'110101110100100', 'Q':'010101101111011', 'R':'110101110101101',
    'S':'011100010001110', 'T':'111010010010010', 'U':'101101101101111',
    'V':'101101101101010', 'W':'101101111111101', 'X':'101101010101101',
    'Y':'101101010010010', 'Z':'111001010100111',
    '0':'111101101101111', '1':'010110010010111', '2':'110001010100111',
    '3':'110001010001110', '4':'101101111001001', '5':'111100110001110',
    '6':'011100111101111', '7':'111001010010010', '8':'111101111101111',
    '9':'111101111001110', '/':'001001010100100', '-':'000000111000000',
    ':':'000010000010000', ' ':'000000000000000', '!':'010010010000010',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pack(a, b):
    return ((a & 1) << 7 | (a & 2) << 2 | (a & 4) << 3 | (a & 8) >> 2 |
            (b & 1) << 6 | (b & 2) << 1 | (b & 4) << 2 | (b & 8) >> 3)


def unpack(v):
    return (((v >> 7) & 1) | ((v >> 2) & 2) | ((v >> 3) & 4) | ((v << 2) & 8),
            ((v >> 6) & 1) | ((v >> 1) & 2) | ((v >> 2) & 4) | ((v << 3) & 8))


def offset(xbyte, y):
    return ((y & 7) << 11) + (y >> 3) * 80 + xbyte


def to_scr(pixels):
    data = bytearray(16384)
    for y in range(HEIGHT):
        for x in range(0, WIDTH, 2):
            data[offset(x // 2, y)] = pack(pixels[y * WIDTH + x], pixels[y * WIDTH + x + 1])
    return bytes(data)


def from_scr(data):
    result = bytearray(WIDTH * HEIGHT)
    for y in range(HEIGHT):
        for xb in range(80):
            result[y * WIDTH + xb * 2:y * WIDTH + xb * 2 + 2] = bytes(unpack(data[offset(xb, y)]))
    return result


def rgb(ink):
    levels = [0, 128, 255]
    return bytes((levels[(ink % 9) // 3], levels[ink // 9], levels[ink % 3]))


def png(path, pixels, palette, sx=1, sy=1):
    """PNG indexed to the exact 16 pens, integer nearest-neighbour preview."""
    def chunk(kind, content):
        return struct.pack('>I', len(content)) + kind + content + struct.pack('>I', zlib.crc32(kind + content))
    rows = bytearray()
    for y in range(HEIGHT):
        row = b'\0' + b''.join(bytes([p]) * sx for p in pixels[y * WIDTH:(y + 1) * WIDTH])
        rows.extend(row * sy)
    data = b'\x89PNG\r\n\x1a\n'
    data += chunk(b'IHDR', struct.pack('>IIBBBBB', WIDTH * sx, HEIGHT * sy, 8, 3, 0, 0, 0))
    data += chunk(b'PLTE', b''.join(map(rgb, palette)))
    data += chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b'')
    path.write_bytes(data)


class Canvas:
    def __init__(self, fill=0):
        self.p = bytearray([fill] * (WIDTH * HEIGHT))

    def dot(self, x, y, ink):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self.p[y * WIDTH + x] = ink

    def rect(self, x, y, w, h, ink):
        for yy in range(max(y, 0), min(y + h, HEIGHT)):
            for xx in range(max(x, 0), min(x + w, WIDTH)):
                self.p[yy * WIDTH + xx] = ink

    def line(self, x0, y0, x1, y1, ink):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            self.dot(round(x0 + (x1 - x0) * i / steps), round(y0 + (y1 - y0) * i / steps), ink)

    def text(self, x, y, words, ink, sx=1, sy=1):
        for char in words:
            for pos, bit in enumerate(FONT[char]):
                if bit == '1':
                    self.rect(x + pos % 3 * sx, y + pos // 3 * sy, sx, sy, ink)
            x += 4 * sx

    def frame(self, x, y, w, h, outer, inner):
        self.rect(x, y, w, h, outer)
        self.rect(x + 1, y + 2, w - 2, h - 4, inner)

    def sprite(self, x, y, data):
        assert 0 <= x <= WIDTH - 16 and 0 <= y <= HEIGHT - 32
        for yy in range(32):
            for xb in range(8):
                start = yy * 16 + xb * 2
                masks, pens = unpack(data[start]), unpack(data[start + 1])
                for p in range(2):
                    assert masks[p] in (0, 15)
                    if masks[p] == 0:
                        self.dot(x + xb * 2 + p, y + yy, pens[p])


def platform(c, x, y, w, ink, kind):
    c.rect(x, y, w, 6, 0)
    c.rect(x, y, w, 2, 1)  # The same walkable edge in every chapter.
    c.rect(x, y + 2, w, 2, ink)
    for xx in range(x + 2, x + w - 2, 8):
        c.rect(xx, y + 4, 4, 1, 5 if kind != 1 else 12)


def machine(c, x, ground, accent):
    y = ground - 17
    c.rect(x + 3, y, 8, 4, 0)
    c.rect(x + 4, y, 6, 3, 1)
    c.frame(x, y + 3, 14, 12, 0, 5)
    c.rect(x + 1, y + 4, 12, 2, accent)
    c.rect(x + 2, y + 7, 8, 3, 0)
    c.rect(x + 3, y + 7, 6, 1, 1)
    c.rect(x + 11, y + 8, 1, 2, 11)
    c.rect(x + 2, y + 12, 10, 2, 15)
    c.rect(x + 2, ground - 2, 2, 2, 0)
    c.rect(x + 10, ground - 2, 2, 2, 0)


def paper(c, x, y, returned=False):
    c.rect(x, y, 4, 6, 0)
    c.rect(x + 1, y + 1, 2, 4, 3 if returned else 1)
    c.dot(x + 2, y + 2, 15)
    if returned:
        c.line(x - 3, y + 3, x - 1, y + 3, 3)


def poster(c, x, y, label, ink):
    width = max(4 * len(label) + 4, 22)
    c.frame(x, y, width, 30, ink, 0)
    c.text(x + 2, y + 3, label, 1)
    # Tiny, deliberately schematic performer and diagonal guitar: no portrait.
    mid = x + width // 2
    c.rect(mid - 1, y + 11, 3, 4, 13)
    c.rect(mid - 3, y + 15, 6, 7, ink)
    c.line(mid, y + 20, mid - 4, y + 26, 1)
    c.line(mid, y + 20, mid + 4, y + 26, 1)
    c.line(mid - 3, y + 22, mid + 6, y + 15, 11)


def scene(kind, sprites):
    # Only unused canonical pens (3, 6, 7, 8, 11) may vary.
    palette = BASE_PALETTE.copy()
    palette[6], palette[11] = 8, 24
    palette[7] = [10, 4, 1, 4][kind]
    c = Canvas(15 if kind == 2 else 7)
    accent = [3, 11, 6, 6][kind]
    if kind == 0:
        c.rect(0, 16, 160, 28, 15)
        c.text(8, 24, 'COPIAS', 3, 2, 2)
        c.text(9, 36, 'INFINITAS', 1)
        for x in range(0, 160, 32):
            c.line(x, 45, x, 182, 15)
        for x in (3, 38, 112):
            c.frame(x, 128, 22, 56, 15, 5)
            for y in (132, 148, 164):
                c.frame(x + 2, y, 18, 13, 15, 7)
                c.rect(x + 9, y + 3, 5, 1, 3)
        poster(c, 122, 47, 'PRINCE', 6)
        c.frame(4, 76, 22, 30, 15, 5)
        c.text(7, 80, 'V27', 1)
        for y in (91, 96, 101):
            c.rect(8, y, 14, 1, 15)
    elif kind == 1:
        c.rect(0, 16, 160, 31, 11)
        c.text(6, 21, 'VERSION 27', 0, 2, 2)
        c.text(7, 36, 'TODO PARA AYER', 0)
        for x in (4, 68, 132):
            c.rect(x, 49, 3, 135, 15)
            for y in range(52, 180, 16):
                c.line(x, y, x + 2, y + 4, 5)
        c.frame(5, 87, 28, 29, 15, 6)
        c.text(8, 91, 'POP!', 1)
        for x in range(8, 30, 7):
            c.line(x, 111, x + 3, 102, 11)
        c.frame(119, 54, 34, 30, 15, 3)
        c.text(122, 58, 'BOWIE', 15)
        c.line(136, 66, 130, 73, 6)
        c.line(130, 73, 140, 70, 6)
        c.line(140, 70, 133, 80, 6)
        # Flat, static paper rolls, no animated scenery.
        for x, h, ink in ((4, 26, 3), (22, 34, 6), (139, 25, 11)):
            c.frame(x, 184 - h, 13, h, 15, ink)
            c.rect(x + 3, 185 - h, 7, 2, 1)
    elif kind == 2:
        c.rect(0, 41, 62, 143, 7)
        c.rect(1, 48, 58, 136, 2)
        c.rect(105, 29, 55, 155, 10)
        c.rect(110, 32, 48, 152, 7)
        for x in (7, 26, 45, 115, 136):
            for y in (76, 116, 152):
                c.frame(x, y, 12, 21, 0, 7)
                c.rect(x + 2, y + 3, 7, 1, 3)
                c.rect(x + 5, y + 4, 1, 13, 5)
        c.frame(3, 19, 88, 23, 6, 0)
        c.text(8, 23, 'A LA CALLE', 11, 2, 2)
        c.frame(111, 40, 45, 25, 6, 0)
        c.text(114, 44, 'MADONNA', 1)
        c.text(114, 55, 'EN VIVO', 11)
        for x in range(112, 156, 6):
            c.rect(x, 67, 6, 7, 11 if (x - 112) // 6 % 2 else 6)
        # Original stick-figure mural, an economical nod to 80s dance graphics.
        c.rect(66, 100, 34, 28, 6)
        for x in (72, 85):
            c.rect(x, 104, 3, 4, 11)
            c.line(x + 1, 109, x + 1, 119, 11)
            c.line(x - 3, 109, x + 5, 114, 11)
            c.line(x + 1, 119, x - 3, 125, 11)
            c.line(x + 1, 119, x + 5, 124, 11)
    else:
        c.rect(0, 16, 160, 32, 0)
        c.text(8, 20, 'PURPLE PAPER', 6, 2, 2)
        c.text(43, 36, 'PRINCE NIGHT', 1)
        for x in (0, 150):
            c.rect(x, 48, 10, 136, 10)
            c.rect(x + 2, 48, 3, 136, 6)
        # Solid colour triangles baked into the background, no lighting engine.
        for yy in range(50, 131):
            extent = (yy - 50) // 5
            c.rect(53 - extent, yy, 1 + 2 * extent, 1, 15)
            c.rect(107 - extent, yy, 1 + 2 * extent, 1, 15)
        for x, y in ((11, 144), (134, 150)):
            c.frame(x, y, 14, 34, 0, 5)
            for yy in (y + 6, y + 22):
                c.frame(x + 3, yy, 8, 8, 0, 15)
                c.rect(x + 6, yy + 3, 2, 2, 5)
        # Motorcycle icon reduced to 24x17 logical pixels, static prop.
        for x in (99, 115):
            c.frame(x, 175, 7, 8, 0, 5)
        c.line(102, 176, 109, 168, 6)
        c.line(109, 168, 118, 178, 6)
        c.line(102, 178, 118, 178, 6)
        c.rect(104, 169, 9, 3, 0)
        c.line(116, 174, 118, 166, 1)
        c.line(115, 166, 119, 166, 1)

    # One shared geometry deliberately separates visual skin from level count.
    # The first raised platform leaves 36px above the floor, clearing Pitu's
    # full 32px visual body when she stands directly below it.
    ledges = [(0, 184, 160), (42, 150, 24), (80, 136, 28),
              (120, 112, 34), (76, 88, 26), (20, 64, 40)]
    for x, y, w in ledges:
        platform(c, x, y, w, accent, kind)
    c.rect(0, 190, 160, 10, 0)
    for x in range(0, 160, 8):
        c.rect(x, 193, 4, 2, accent)
    for x, ground in ((7, 184), (135, 112), (23, 64)):
        machine(c, x, ground, accent)
    # Exit marker, visible but closed while three machines remain.
    c.frame(42, 46, 12, 18, 0, 15)
    c.text(44, 49, 'X', 6)
    c.rect(49, 57, 2, 2, 11)
    if kind in (1, 3):
        c.frame(114, 121, 8, 13, 0, 7)
        c.line(115, 132, 120, 123, 11)

    c.rect(0, 0, 160, 16, 0)
    c.text(3, 3, 'P1 002500', 1)
    c.text(47, 3, 'VIDA 2', 3)
    c.text(85, 3, 'MAQ 3', 11)
    c.text(122, 3, f'FASE {kind + 1}', 6)
    c.rect(0, 13, 160, 1, accent)
    background = bytes(c.p)
    c.sprite(75, 152, sprites['g_pitu_walk'])
    # Alberto is a style/scale witness; only the office includes this NPC.
    actors = [{'name': 'Pitu', 'x': 75, 'y': 152, 'w': 16, 'h': 32}]
    if kind == 0:
        c.sprite(114, 152, sprites['g_alberto'])
        actors.append({'name': 'Alberto', 'x': 114, 'y': 152, 'w': 16, 'h': 32})
    paper(c, 48, 174)
    paper(c, 117, 96, returned=True)
    return c.p, background, palette, ledges, actors


def tilepack(pixels):
    """8x8 logical pixels = 32 packed bytes; 20x25 map, u8 if possible."""
    unique, ids, lookup = [], [], {}
    for ty in range(0, HEIGHT, 8):
        for tx in range(0, WIDTH, 8):
            tile = bytes(pack(pixels[(ty + y) * WIDTH + tx + x], pixels[(ty + y) * WIDTH + tx + x + 1])
                         for y in range(8) for x in range(0, 8, 2))
            if tile not in lookup:
                lookup[tile] = len(unique)
                unique.append(tile)
            ids.append(lookup[tile])
    index_bytes = 1 if len(unique) <= 256 else 2
    map_data = bytes(ids) if index_bytes == 1 else struct.pack('<500H', *ids)
    # Independent traversal verifies the tiles reconstruct the entire background.
    restored = bytearray(WIDTH * HEIGHT)
    for cell, tile_id in enumerate(ids):
        tx, ty = (cell % 20) * 8, (cell // 20) * 8
        for y in range(8):
            for xb in range(4):
                pos = (ty + y) * WIDTH + tx + xb * 2
                restored[pos:pos + 2] = bytes(unpack(unique[tile_id][y * 4 + xb]))
    assert restored == pixels
    return b''.join(unique), map_data, len(unique), index_bytes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, default=(ROOT.parent / 'banterhouse'))
    parser.add_argument('--compress', action='store_true', help='Measure local ZX0 and verify host decompression')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    source_path = args.original / 'src' / 'graphics.c'
    source_bytes = source_path.read_bytes()
    main_bytes = (args.original / 'src' / 'main.c').read_bytes()
    palette_definition = re.search(r'const u8 bh_palette\[16\]\s*=\s*\{(.*?)\}', main_bytes.decode(), re.S)
    expected_names = ['BLACK', 'BRIGHT_WHITE', 'SKY_BLUE', 'BRIGHT_CYAN', 'GREEN', 'WHITE',
                      'BRIGHT_GREEN', 'PASTEL_GREEN', 'PASTEL_YELLOW', 'RED', 'PURPLE',
                      'PASTEL_MAGENTA', 'ORANGE', 'PINK', 'YELLOW', 'BLUE']
    assert palette_definition and re.findall(r'HW_(\w+)', palette_definition[1]) == expected_names
    source = re.sub(r'#if 0\b.*?#endif', '', source_bytes.decode(), flags=re.S)
    sprites, sprite_report, used_pens = {}, {}, set()
    for name in ('g_pitu', 'g_pitu_walk', 'g_alberto'):
        match = re.search(r'const unsigned char\s+' + name + r'\[512\]\s*=\s*\{(.*?)\}', source, re.S)
        assert match, name
        data = bytes(int(v, 16) for v in re.findall(r'0x([0-9a-fA-F]{2})', match[1]))
        assert len(data) == 512
        assert all(m in (0, 0x55, 0xAA, 0xFF) and m & p == 0
                   for m, p in zip(data[::2], data[1::2]))
        pens = {p for mask, byte in zip(data[::2], data[1::2])
                for m, p in zip(unpack(mask), unpack(byte)) if m == 0}
        used_pens |= pens
        sprites[name] = data
        sprite_report[name] = {'bytes': len(data), 'sha256': digest(data), 'opaque_pens': sorted(pens)}
        (OUT / f'{name}.masked.bin').write_bytes(data)

    # Exhaustive test of every possible byte, plus boundary address vectors.
    for byte in range(256):
        assert pack(*unpack(byte)) == byte
    assert [offset(0, y) for y in (0, 1, 7, 8, 199)] == [0, 2048, 14336, 80, 16256]
    addresses = {offset(x, y) for y in range(200) for x in range(80)}
    assert len(addresses) == 16000 and max(addresses) == 16335
    report = {'scope': 'Static CPC Mode 0 art; host validation only; no emulator or FPS measurement',
              'source': str(source_path), 'source_sha256': digest(source_bytes),
              'source_palette_main_c_sha256': digest(main_bytes),
              'sprites': sprite_report, 'dimensions': [WIDTH, HEIGHT],
              'preview_scale': [5, 3], 'screen_bytes': 16384,
              'visible_bytes': 16000, 'unused_screen_bytes': 384,
              'tests': {'mode0_byte_roundtrips': 256, 'unique_visible_addresses': len(addresses),
                        'sprite_palette_preserved': True, 'full_screen_roundtrips': 4,
                        'tile_background_roundtrips': 4}, 'scenes': []}
    names = ['01-copias', '02-produccion', '03-calle', '04-purple']
    for kind, name in enumerate(names):
        pixels, bg, palette, ledges, actors = scene(kind, sprites)
        assert all(palette[p] == BASE_PALETTE[p] for p in used_pens)
        scr = to_scr(pixels)
        decoded = from_scr(scr)
        assert decoded == pixels and max(decoded) < 16
        (OUT / f'{name}.scr').write_bytes(scr)
        (OUT / f'{name}.background.scr').write_bytes(to_scr(bg))
        (OUT / f'{name}.fwpal').write_bytes(bytes(palette))
        (OUT / f'{name}.hwpal').write_bytes(bytes(0x40 | HW[p] for p in palette))
        png(OUT / f'{name}.native.png', decoded, palette)
        png(OUT / f'{name}.png', decoded, palette, 5, 3)
        tiles, map_data, ntiles, index_size = tilepack(bg)
        (OUT / f'{name}.tiles.bin').write_bytes(tiles)
        (OUT / f'{name}.map.bin').write_bytes(map_data)
        report['scenes'].append({'name': name, 'sha256_scr': digest(scr),
                                 'firmware_palette': palette, 'used_pens': sorted(set(pixels)),
                                 'unique_rgb_colours': len({rgb(palette[p]) for p in pixels}),
                                 'background_tiles_8x8': ntiles, 'tiles_bytes': len(tiles),
                                 'map_bytes': len(map_data), 'map_index_bytes': index_size,
                                 'tile_pack_bytes': len(tiles) + len(map_data),
                                 'platforms_x_y_w': ledges, 'actors': actors,
                                 'paper_count': 2, 'static_machine_count': 3})
    if args.compress:
        zxroot = ROOT / 'tmp/research-tools/ZX0'
        encoder, decoder = zxroot / 'src/zx0', zxroot / 'src/dzx0'
        assert encoder.is_file() and decoder.is_file(), 'Build ZX0 as described in research/README.md'
        report['zx0'] = {'git_sha': subprocess.check_output(['git', '-C', str(zxroot), 'rev-parse', 'HEAD'], text=True).strip(),
                         'encoder_sha256': digest(encoder.read_bytes()), 'scope': 'host sizes and round-trips; no Z80 timing'}
        for row in report['scenes']:
            source_file = OUT / (row['name'] + '.background.scr')
            target_file = source_file.with_suffix('.scr.zx0')
            subprocess.run([str(encoder), '-f', str(source_file), str(target_file)], check=True, capture_output=True)
            with tempfile.TemporaryDirectory() as temporary:
                restored = Path(temporary) / 'restored.scr'
                subprocess.run([str(decoder), str(target_file), str(restored)], check=True, capture_output=True)
                assert restored.read_bytes() == source_file.read_bytes()
            row['background_zx0_bytes'] = target_file.stat().st_size
            row['background_zx0_roundtrip'] = True
    else:
        # Avoid retaining compressed artifacts after a geometry/palette rebuild.
        for name in names:
            (OUT / (name + '.background.scr.zx0')).unlink(missing_ok=True)
    (OUT / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
