#!/usr/bin/env python3
"""Check AVFoundation name resolution never confuses video and audio indices."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("capture_audio", ROOT / "tools/capture_audio.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def main() -> int:
    listing = """AVFoundation video devices:
[0] FaceTime HD Camera
[3] Capture screen 0
AVFoundation audio devices:
[0] Open Audio 8 DJ
[1] BlackHole 2ch
[2] MacBook Air Microphone
"""
    devices = module.parse_audio_devices(listing)
    assert devices == [(0, "Open Audio 8 DJ"), (1, "BlackHole 2ch"), (2, "MacBook Air Microphone")]
    assert module.parse_audio_devices("AVFoundation video devices:\n[1] BlackHole 2ch\n") == []
    assert module.parse_audio_devices("AVFoundation audio devices:\n") == []
    print("PASS AVFoundation resolver selects audio index by exact device name")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
