#!/usr/bin/env python3
"""Build CPC renderer scenario tables and independent expected VRAM hashes."""
import argparse
import json
import zlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import reference_compositor as oracle  # noqa: E402

SPRITE_IDS = {"pitu": 0, "alberto": 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT / "build/render-cpc")
    parser.add_argument("--only-frame", type=int,
                        help="emit one zero-based CPC scenario for diagnosis")
    args = parser.parse_args()
    out = args.outdir if args.outdir.is_absolute() else ROOT / args.outdir
    out.mkdir(parents=True, exist_ok=True)
    source = json.loads((ROOT / "tests/cpc/render/scenarios.json").read_text())
    frames = source["frames"]
    if args.only_frame is not None:
        if not 0 <= args.only_frame < len(frames):
            raise SystemExit(f"FAIL: frame index {args.only_frame} is outside the scenario table")
        frames = [frames[args.only_frame]]
    header = ["#ifndef RENDER_SCENARIOS_H", "#define RENDER_SCENARIOS_H", "#include <stdint.h>",
              "#define RG_TEST_PITU 0u", "#define RG_TEST_ALBERTO 1u",
              "#define RENDER_TEST_FRAME_COUNT %du" % len(frames),
              "typedef struct { uint8_t sprite, pose; int16_t x, y; uint8_t facing_left, layer, id; } RenderTestActor;",
              "typedef struct { uint8_t background, count; RenderTestActor actors[2]; } RenderTestFrame;",
              "static const RenderTestFrame render_test_frames[RENDER_TEST_FRAME_COUNT] = {"]
    expected_hashes = []
    final = None
    for frame in frames:
        actors = frame["actors"]
        if len(actors) > 2:
            raise SystemExit("FAIL: CPC fixture currently supports at most two actors per frame")
        header.append("  {%du, %du, {" % (frame["background"], len(actors)))
        for actor in actors:
            sprite_id = SPRITE_IDS[actor["sprite"]]
            header.append("    {%du, %du, %d, %d, %du, %du, %du}," % (
                sprite_id, actor["pose"], actor["x"], actor["y"],
                int(actor["flip"]), actor["layer"], actor["id"]))
        header.append("  }},")
        bg = oracle.make_background(bool(frame["background"]))
        screen = oracle.compose(bg, actors)
        expected_hashes.append(zlib.crc32(screen) & 0xFFFFFFFF)
        final = bytearray(screen)
    header.extend(("};", "static const uint32_t render_test_crc32[RENDER_TEST_FRAME_COUNT] = {"))
    for start in range(0, len(expected_hashes), 4):
        header.append("  " + ", ".join(f"0x{value:08X}UL" for value in expected_hashes[start:start + 4]) + ",")
    header.extend(("};", "#endif", ""))
    (out / "render_scenarios.h").write_text("\n".join(header))
    final[0] = 0x55  # Visible pass marker added by the CPC fixture after CRC checks.
    (out / "render-final-vram.bin").write_bytes(final)
    result = {"frames": len(frames), "crc32": [f"{value:08x}" for value in expected_hashes],
              "final_screen_sha256": __import__("hashlib").sha256(final).hexdigest(),
              "actors_per_frame": [len(frame["actors"]) for frame in frames],
              "result": "PASS"}
    (out / "render-scenarios.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: generated {len(frames)} CPC frame vectors and independent CRC32 expectations")


if __name__ == "__main__":
    main()
