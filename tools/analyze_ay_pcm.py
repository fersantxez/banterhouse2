#!/usr/bin/env python3
"""Measure tonal AY output from a PCM WAV captured from the emulator."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import wave

import numpy as np


def analyze(
    path: Path,
    window_seconds: float = 0.5,
    allowed_silence: list[tuple[float, float]] | None = None,
    expected_step_seconds: float = 0.12,
) -> dict[str, object]:
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        rate = wav.getframerate()
        width = wav.getsampwidth()
        frames = wav.getnframes()
        if width != 2 or channels < 1 or rate < 8000:
            raise ValueError("expected PCM S16LE WAV with at least one channel")
        samples = np.frombuffer(wav.readframes(frames), dtype="<i2")
    if samples.size != frames * channels:
        raise ValueError("truncated PCM data")
    mono = samples.reshape(-1, channels).astype(np.float64).mean(axis=1)
    block = max(1024, round(rate * window_seconds))
    windows: list[dict[str, object]] = []
    for start in range(0, len(mono), block):
        segment = mono[start : min(start + block, len(mono))]
        if len(segment) < rate * 0.2:
            continue
        rms = math.sqrt(float(np.mean(segment * segment)))
        centered = segment - float(np.mean(segment))
        spectrum = np.abs(np.fft.rfft(centered * np.hanning(len(centered))))
        freqs = np.fft.rfftfreq(len(centered), 1 / rate)

        def strongest(low: float, high: float) -> tuple[float, float]:
            mask = (freqs >= low) & (freqs <= high)
            indices = np.flatnonzero(mask)
            if not len(indices):
                return (0.0, 0.0)
            idx = int(indices[np.argmax(spectrum[indices])])
            return (float(freqs[idx]), float(spectrum[idx]))

        melody_hz, melody_strength = strongest(300, 1800)
        bass_hz, bass_strength = strongest(35, 260)
        windows.append({
            "start_seconds": round(start / rate, 3),
            "duration_seconds": round(len(segment) / rate, 3),
            "rms": round(rms, 3),
            "rms_dbfs": round(20 * math.log10(max(rms / 32768, 1e-12)), 2),
            "peak": int(np.max(np.abs(segment))),
            "melody_peak_hz": round(melody_hz, 2),
            "melody_peak_strength": round(melody_strength, 1),
            "bass_peak_hz": round(bass_hz, 2),
            "bass_peak_strength": round(bass_strength, 1),
        })
    active = [w for w in windows if float(w["rms"]) >= 100]
    melody_bins = {round(float(w["melody_peak_hz"]) / 10) for w in active}
    bass_bins = {round(float(w["bass_peak_hz"]) / 5) for w in active}
    allowed = allowed_silence or []
    silent_windows = [w for w in windows if float(w["rms"]) < 100]
    unplanned = [
        w for w in silent_windows
        if not any(start <= float(w["start_seconds"]) + float(w["duration_seconds"]) / 2 < end
                   for start, end in allowed)
    ]

    def longest_run(items: list[dict[str, object]]) -> float:
        longest = current = 0.0
        previous_end = None
        for item in items:
            start = float(item["start_seconds"])
            duration = float(item["duration_seconds"])
            if previous_end is None or abs(start - previous_end) <= 0.01:
                current += duration
            else:
                current = duration
            longest = max(longest, current)
            previous_end = start + duration
        return round(longest, 3)

    unplanned_silence = longest_run(unplanned)
    clipped = [w for w in windows if int(w["peak"]) >= 32700]
    step_frames = max(1024, round(rate * expected_step_seconds))
    melody_steps: list[tuple[float, int]] = []
    for start in range(0, len(mono) - step_frames + 1, step_frames):
        segment = mono[start : start + step_frames]
        centered = segment - float(np.mean(segment))
        spectrum = np.abs(np.fft.rfft(centered * np.hanning(len(centered))))
        freqs = np.fft.rfftfreq(len(centered), 1 / rate)
        mask = (freqs >= 300) & (freqs <= 1800)
        indices = np.flatnonzero(mask)
        idx = int(indices[np.argmax(spectrum[indices])])
        peak = float(spectrum[idx])
        note = round(float(freqs[idx]) / 20) if peak >= 100_000 else 0
        melody_steps.append((start / rate, note))
    transitions: list[float] = []
    prior_note = None
    for start, note in melody_steps:
        if note != prior_note:
            transitions.append(start)
            prior_note = note
    intervals = np.diff(transitions)
    estimated_step = float(np.median(intervals)) if len(intervals) >= 4 else 0.0
    tempo_stable = (len(intervals) >= 4 and 0.08 <= estimated_step <= 0.20)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "source": str(path),
        "sha256": digest,
        "format": {"sample_rate": rate, "channels": channels, "sample_width_bytes": width},
        "duration_seconds": round(frames / rate, 3),
        "peak": int(np.max(np.abs(samples))) if samples.size else 0,
        "rms": round(math.sqrt(float(np.mean(samples.astype(np.float64) ** 2))), 3),
        "active_windows": len(active),
        "distinct_melody_bins_10hz": len(melody_bins),
        "distinct_bass_bins_5hz": len(bass_bins),
        "longest_silence_seconds": longest_run(silent_windows),
        "longest_unplanned_silence_seconds": unplanned_silence,
        "clipped_windows": len(clipped),
        "tempo_step_seconds_estimate": round(estimated_step, 4),
        "allowed_silence_intervals": [[start, end] for start, end in allowed],
        "windows": windows,
        "assertions": {
            "pcm_signal_present": bool(active),
            "melody_changes_pitch": len(melody_bins) >= 4,
            "bass_changes_pitch": len(bass_bins) >= 3,
            "no_unplanned_silence_over_2s": unplanned_silence <= 2.0,
            "no_sustained_clipping": len(clipped) < 4,
            "tempo_stable_near_125_bpm": bool(tempo_stable),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wav", type=Path)
    parser.add_argument("--window", type=float, default=0.5, help="spectral window in seconds")
    parser.add_argument("--allow-silence", action="append", default=[], metavar="START:END",
                        help="document an intentional silent interval; may be repeated")
    parser.add_argument("--expected-step", type=float, default=0.12,
                        help="expected AY melody step in seconds (125 BPM sixteenths = 0.12)")
    parser.add_argument("--json", type=Path, help="write report to this path")
    args = parser.parse_args()
    if args.window < 0.2:
        parser.error("--window must be at least 0.2 seconds")
    intervals: list[tuple[float, float]] = []
    for value in args.allow_silence:
        try:
            start_text, end_text = value.split(":", 1)
            interval = (float(start_text), float(end_text))
        except ValueError:
            parser.error(f"invalid --allow-silence interval: {value!r}")
        if interval[0] < 0 or interval[1] <= interval[0]:
            parser.error(f"invalid --allow-silence interval: {value!r}")
        intervals.append(interval)
    if args.expected_step <= 0:
        parser.error("--expected-step must be > 0")
    report = analyze(args.wav, args.window, intervals, args.expected_step)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered)
    print(rendered, end="")
    return 0 if all(report["assertions"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
