#!/usr/bin/env python3
"""Detect named AY sound-effect tones in time windows of runtime PCM."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import wave

import numpy as np

# AY tone period is clock/(16*period); measured Caprice CPC clock is ~1.00352 MHz.
AY_TONE_CLOCK = 1_003_520 / 16


def detect(path: Path, events: list[tuple[str, float, float, int]], threshold: float = 250_000) -> dict:
    with wave.open(str(path), "rb") as wav:
        channels, rate, width, frames = wav.getnchannels(), wav.getframerate(), wav.getsampwidth(), wav.getnframes()
        if width != 2 or channels < 1 or rate < 8000:
            raise ValueError("expected PCM S16LE WAV")
        samples = np.frombuffer(wav.readframes(frames), dtype="<i2")
    if len(samples) != frames * channels:
        raise ValueError("truncated WAV")
    mono = samples.reshape(-1, channels).astype(np.float64).mean(axis=1)
    results = []
    for name, start, end, period in events:
        a, b = max(0, round(start * rate)), min(len(mono), round(end * rate))
        if b - a < rate * 0.025 or period <= 0:
            raise ValueError(f"event {name} has an invalid or too-short time window")
        segment = mono[a:b]
        segment -= segment.mean()
        spectrum = np.abs(np.fft.rfft(segment * np.hanning(len(segment))))
        freqs = np.fft.rfftfreq(len(segment), 1 / rate)
        expected = AY_TONE_CLOCK / period
        mask = (freqs >= expected * 0.94) & (freqs <= expected * 1.06)
        measured = float(np.max(spectrum[mask])) if np.any(mask) else 0.0
        results.append({
            "event": name,
            "start_seconds": start,
            "end_seconds": end,
            "ay_period": period,
            "expected_hz": round(expected, 2),
            "measured_peak_strength": round(measured, 1),
            "detected": measured >= threshold,
        })
    return {
        "source": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "threshold": threshold,
        "events": results,
        "all_events_detected": bool(results) and all(item["detected"] for item in results),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wav", type=Path)
    parser.add_argument("--event", action="append", default=[], metavar="START:END:NAME:PERIOD",
                        help="expected AY SFX window; repeat for each event")
    parser.add_argument("--min-strength", type=float, default=250_000)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    events = []
    for spec in args.event:
        start, end, name, period = spec.split(":", 3)
        events.append((name, float(start), float(end), int(period)))
    report = detect(args.wav, events, args.min_strength)
    serialized = json.dumps(report, indent=2)
    if args.json:
        args.json.write_text(serialized + "\n")
    print(serialized)
    return 0 if report["all_events_detected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
