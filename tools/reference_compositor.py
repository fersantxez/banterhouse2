#!/usr/bin/env python3
"""Independent per-pixel Mode 0 oracle for renderer G fixtures."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/source/canonical"
WIDTH, HEIGHT = 160, 200
SCREEN_BYTES = 0x4000


def unpack_mode0(value):
    return (((value >> 7) & 1) | ((value >> 2) & 2) | ((value >> 3) & 4) | ((value << 2) & 8),
            ((value >> 6) & 1) | ((value >> 1) & 2) | ((value >> 2) & 4) | ((value << 3) & 8))


def pack_mode0(left, right):
    return (((left & 1) << 7) | ((right & 1) << 6) |
            ((left & 2) << 2) | ((right & 2) << 1) |
            ((left & 4) << 3) | ((right & 4) << 2) |
            ((left & 8) >> 2) | ((right & 8) >> 3))


def screen_offset(x, y):
    return ((y & 7) * 0x800) + ((y >> 3) * 80) + (x >> 1)


def make_background(patch=False):
    data = bytearray((index * 37 + (index >> 4) * 11 + 0x5A) & 0xFF
                     for index in range(SCREEN_BYTES))
    if patch:
        # Simulated persistent world change beneath the actor's old box.
        data[screen_offset(50, 130)] = 0xA5
    return data


def _sprite_pixels(name):
    raw = (SOURCE / name).read_bytes()
    if len(raw) != 512:
        raise ValueError(f"{name}: expected 512 bytes")
    pixels, opaque = [], []
    for y in range(32):
        row_pixels, row_opaque = [], []
        for column in range(8):
            mask = unpack_mode0(raw[y * 16 + column * 2])
            ink = unpack_mode0(raw[y * 16 + column * 2 + 1])
            row_pixels.extend(ink)
            row_opaque.extend((mask[0] != 15, mask[1] != 15))
        pixels.append(row_pixels)
        opaque.append(row_opaque)
    return pixels, opaque


SPRITES = {
    "pitu": _sprite_pixels("g_pitu.masked.bin"),
    "pitu_walk": _sprite_pixels("g_pitu_walk.masked.bin"),
    "alberto": _sprite_pixels("g_alberto.masked.bin"),
}


def compose(background, actors):
    """Compose logical pixels, independently of CPC byte-mask variants."""
    screen = bytearray(background)
    ordered = sorted(enumerate(actors), key=lambda pair: (pair[1]["layer"], pair[1]["id"], pair[0]))
    for _, actor in ordered:
        if not actor.get("visible", True):
            continue
        if "pixels" in actor and "opaque" in actor:
            pixels, opaque = actor["pixels"], actor["opaque"]
        else:
            sprite_name = actor["sprite"]
            if sprite_name == "pitu" and actor.get("pose", 0) == 1:
                sprite_name = "pitu_walk"
            pixels, opaque = SPRITES[sprite_name]
        for source_y in range(len(pixels)):
            y = actor["y"] + source_y
            if not 0 <= y < HEIGHT:
                continue
            for source_x in range(len(pixels[source_y])):
                x = actor["x"] + source_x
                if not 0 <= x < WIDTH:
                    continue
                pixel_x = len(pixels[source_y]) - 1 - source_x if actor["flip"] else source_x
                if not opaque[source_y][pixel_x]:
                    continue
                offset = screen_offset(x, y)
                colors = list(unpack_mode0(screen[offset]))
                colors[x & 1] = pixels[source_y][pixel_x]
                screen[offset] = pack_mode0(*colors)
    return bytes(screen)
