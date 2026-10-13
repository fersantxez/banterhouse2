#!/usr/bin/env python3
"""Differential-test the CPC blitter against an independent pixel oracle."""
import importlib.util
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/render-reference"
OUT.mkdir(parents=True, exist_ok=True)

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

oracle = load_module("reference_compositor", ROOT / "tools/reference_compositor.py")
assets = load_module("runtime_assets", ROOT / "tools/build_runtime_assets.py")
raw_names = {"pitu": "g_pitu.masked.bin", "pitu_walk": "g_pitu_walk.masked.bin",
             "alberto": "g_alberto.masked.bin"}

base = oracle.make_background(False)
persistent = bytearray(base)
persistent[oracle.screen_offset(50, 130)] = 0xA5
hud_changed = bytearray(persistent)
hud_start = oracle.screen_offset(4, 4)
hud_changed[hud_start:hud_start + 8] = bytes([0x5A]) * 8
backgrounds = [bytes([value]) * oracle.SCREEN_BYTES for value in (0x00, 0xff, 0x55, 0xaa)]
backgrounds.extend((base, bytes(persistent), bytes(hud_changed), oracle.make_background(False)))
(OUT / "backgrounds.bin").write_bytes(b"".join(backgrounds))

paper_pixels = [[0 if (x + y) % 3 == 0 else (1 + x + 2 * y) % 16 for x in range(4)]
                for y in range(6)]
paper_opaque = [[not ((x == 3 and y in (1, 4)) or (x == 1 and y == 5))
                 for x in range(4)] for y in range(6)]
frames = []
xs = (-16, -15, -1, 0, 1, 143, 144, 145, 159, 160)
ys = (-32, -1, 0, 6, 7, 8, 14, 15, 16, 62, 63, 64,
      126, 127, 128, 190, 191, 192, 199, 200)
for xi, x in enumerate(xs):
    for yi, y in enumerate(ys):
        sprite = ("pitu", "pitu_walk", "alberto")[(xi + yi) % 3]
        frames.append({"background": (xi + yi) % 4, "actors": [{
            "id": 1, "layer": 1, "sprite": sprite, "x": x, "y": y,
            "flip": bool((xi + yi) & 1)}]})

# Paper contract: four pixels by six rows, including opaque pen zero and
# transparent cells, at y=5..9 and even/odd x including the right edge.
for y in range(5, 10):
    for x in (0, 1, 155, 156):
        frames.append({"background": 2 + (y & 1), "actors": [{
            "id": 9, "layer": 2, "sprite": "paper", "pixels": paper_pixels,
            "opaque": paper_opaque, "height": 6, "x": x, "y": y, "flip": False}]})

# Render order, crossings, pose changes, deletion/reuse, persistent and HUD
# updates, pause (stable repeated state), retry and a fresh scene.
frames.extend([
    {"background": 4, "actors": [
        {"id": 1, "layer": 1, "sprite": "pitu", "x": 56, "y": 120, "flip": False}]},
    {"background": 4, "actors": [
        {"id": 1, "layer": 1, "sprite": "pitu", "x": 58, "y": 120, "flip": False},
        {"id": 2, "layer": 0, "sprite": "alberto", "x": 62, "y": 120, "flip": True}]},
    {"background": 4, "actors": [
        {"id": 1, "layer": 1, "sprite": "pitu_walk", "x": 58, "y": 112, "flip": True},
        {"id": 2, "layer": 0, "sprite": "alberto", "x": 60, "y": 116, "flip": False},
        {"id": 3, "layer": 2, "sprite": "pitu", "x": 64, "y": 112, "flip": False}]},
    {"background": 4, "actors": [{"id": 2, "layer": 0, "sprite": "alberto",
        "x": 70, "y": 116, "flip": False}]},
    {"background": 4, "actors": []},
    {"background": 4, "actors": [{"id": 7, "layer": 1, "sprite": "pitu_walk",
        "x": 48, "y": 128, "flip": False}]},
    {"background": 5, "actors": [{"id": 7, "layer": 1, "sprite": "pitu_walk",
        "x": 48, "y": 128, "flip": False}]},
    {"background": 6, "actors": [{"id": 7, "layer": 1, "sprite": "pitu_walk",
        "x": 48, "y": 128, "flip": False}]},
    {"background": 6, "actors": []},
    {"background": 6, "actors": []},
    {"background": 4, "actors": [{"id": 7, "layer": 1, "sprite": "pitu_walk",
        "x": 48, "y": 128, "flip": False}]},
    {"background": 7, "actors": [{"id": 3, "layer": 1, "sprite": "pitu",
        "x": 20, "y": 96, "flip": True}]},
])

def encode_dynamic_variant(pixels, opaque, flip, shift):
    width = (len(pixels[0]) + shift + 1) // 2
    output = bytearray()
    for y, row in enumerate(pixels):
        source_pixels = row[::-1] if flip else row
        source_opaque = opaque[y][::-1] if flip else opaque[y]
        for col in range(width):
            pair = []
            for half in range(2):
                x = col * 2 + half - shift
                pair.append((source_pixels[x] if source_opaque[x] else 0,
                             source_opaque[x]) if 0 <= x < len(row)
                            else (0, False))
            output.append(assets.pack_mode0(*(15 if not item[1] else 0 for item in pair)))
            output.append(assets.pack_mode0(*(item[0] for item in pair)))
    return bytes(output)

variant_paths = {}
for sprite, filename in raw_names.items():
    raw = (ROOT / "assets/source/canonical" / filename).read_bytes()
    assets.validate_sprite(raw, filename)
    for flip in (False, True):
        for shift in (0, 1):
            path = OUT / f"{sprite}_{int(flip)}_{shift}.bin"
            path.write_bytes(assets.encode_variant(raw, flip, shift))
            variant_paths[(sprite, flip, shift)] = path
for flip in (False, True):
    for shift in (0, 1):
        path = OUT / f"paper_{int(flip)}_{shift}.bin"
        path.write_bytes(encode_dynamic_variant(paper_pixels, paper_opaque, flip, shift))
        variant_paths[("paper", flip, shift)] = path

vectors = bytearray(len(frames).to_bytes(2, "little"))
expected_frames = []
for frame in frames:
    actors = frame["actors"]
    ordered = sorted(enumerate(actors), key=lambda pair: (pair[1]["layer"], pair[1]["id"], pair[0]))
    vectors.extend((frame["background"], len(actors)))
    for _, actor in ordered:
        x, y = actor["x"], actor["y"]
        height = actor.get("height", 32)
        variant = variant_paths[(actor["sprite"], actor["flip"], x & 1)].read_bytes()
        width_bytes = len(variant) // (height * 2)
        vectors.extend(x.to_bytes(2, "little", signed=True))
        vectors.extend(y.to_bytes(2, "little", signed=True))
        vectors.extend((width_bytes, height))
        vectors.extend(variant)
    expected_frames.append(oracle.compose(backgrounds[frame["background"]], actors))
(OUT / "vectors.bin").write_bytes(vectors)

binary = OUT / "render_blit_test"
subprocess.run([
    os.environ.get("CC", "cc"), "-std=c99", "-Wall", "-Wextra", "-Werror",
    "-fsanitize=address,undefined", str(ROOT / "tests/host/render_blit.c"),
    str(ROOT / "src/render/render_g.c"), "-o", str(binary)
], check=True)
actual_path = OUT / "actual.bin"
subprocess.run([str(binary), str(OUT / "backgrounds.bin"), str(OUT / "vectors.bin"),
                str(actual_path)], check=True)
actual = actual_path.read_bytes()
if len(actual) != len(expected_frames) * oracle.SCREEN_BYTES:
    raise SystemExit("FAIL: C renderer returned a truncated/oversized frame stream")
for index, expected in enumerate(expected_frames):
    got = actual[index * oracle.SCREEN_BYTES:(index + 1) * oracle.SCREEN_BYTES]
    if got != expected:
        first = next(i for i, pair in enumerate(zip(got, expected)) if pair[0] != pair[1])
        phase, remainder = divmod(first, 0x0800)
        row_group, byte_x = divmod(remainder, 80)
        y, x = row_group * 8 + phase, byte_x * 2
        actual_pens = oracle.unpack_mode0(got[first])
        expected_pens = oracle.unpack_mode0(expected[first])
        if actual_pens[0] == expected_pens[0]:
            x += 1
        raise SystemExit(f"FAIL frame {index}: pixel ({x},{y}), CPC byte &{first:04X}: "
                         f"{got[first]:02X}!={expected[first]:02X}; "
                         f"pens {actual_pens}!={expected_pens}")

(OUT / "expected-final-vram.bin").write_bytes(expected_frames[-1])
manifest = {
    "frames": len(frames), "edge_sweep": {"x": list(xs), "y": list(ys)},
    "background_patterns": ["00", "FF", "55", "AA", "indexed", "persistent", "HUD", "new-scene"],
    "paper_probe": {"logical_size": "4x6", "y": list(range(5, 10)),
                    "transparent_and_black_opaque": True},
    "sequence": ["crossing", "pose-change", "remove", "reuse", "persistent-update",
                 "HUD-update", "pause", "retry", "new-scene"],
    "exact_screen_byte_comparisons": len(frames) * oracle.SCREEN_BYTES,
    "result": "PASS"
}
(OUT / "results.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(f"PASS: independent pixels == CPC blitter for {len(frames)} frames "
      f"({len(frames) * oracle.SCREEN_BYTES:,} bytes), edges, 4x6 paper, opacity and restore sequence.")
