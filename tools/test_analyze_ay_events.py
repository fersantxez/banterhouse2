#!/usr/bin/env python3
"""Ensure AY event detector accepts expected SFX tones and rejects their absence."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("analyze_ay_events", ROOT / "tools/analyze_ay_events.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def write(path: Path, data: np.ndarray, rate: int = 48_000) -> None:
    pcm = np.clip(data, -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(pcm.tobytes())


def main() -> int:
    rate = 48_000
    time = np.arange(rate * 2) / rate
    period = 56
    hz = module.AY_TONE_CLOCK / period
    event = (time >= 0.5) & (time < 0.62)
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        with_sfx = base / "with-sfx.wav"
        write(with_sfx, np.where(event, 8_000 * np.sign(np.sin(2 * np.pi * hz * time)), 0))
        report = module.detect(with_sfx, [("seal", 0.48, 0.65, period)])
        assert report["all_events_detected"]
        assert report["events"][0]["expected_hz"] == round(hz, 2)

        no_sfx = base / "no-sfx.wav"
        write(no_sfx, np.zeros_like(time))
        report = module.detect(no_sfx, [("seal", 0.48, 0.65, period)])
        assert report["all_events_detected"] is False
    print("PASS AY PCM event detector accepts a seal tone and rejects its absence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
