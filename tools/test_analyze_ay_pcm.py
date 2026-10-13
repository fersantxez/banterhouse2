#!/usr/bin/env python3
"""Verify PCM diagnostics accept a tune and reject silence or a stuck note."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("analyze_ay_pcm", ROOT / "tools/analyze_ay_pcm.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def write(path: Path, signal: np.ndarray, rate: int = 12_000) -> None:
    pcm = np.clip(signal, -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(pcm.tobytes())


def main() -> int:
    rate = 12_000
    time = np.arange(rate * 8) / rate
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        notes = [440, 523.25, 659.25, 587.33, 392, 493.88, 783.99, 659.25]
        def compose(step: float) -> np.ndarray:
            signal = np.zeros_like(time)
            for i, start in enumerate(np.arange(0, 8, step)):
                part = (time >= start) & (time < min(start + step, 8))
                local = time[part]
                hz = notes[i % len(notes)]
                bass = 65 + (i % 5) * 9
                signal[part] = 8_000 * np.sin(2 * np.pi * hz * local) + 2_000 * np.sin(2 * np.pi * bass * local)
            return signal

        tune = compose(0.12)
        path = base / "tune.wav"
        write(path, tune)
        report = module.analyze(path)
        assert report["assertions"]["pcm_signal_present"] is True
        assert report["assertions"]["melody_changes_pitch"] is True
        assert report["assertions"]["bass_changes_pitch"] is True
        assert report["assertions"]["no_unplanned_silence_over_2s"] is True
        assert report["assertions"]["tempo_stable_near_125_bpm"] is True

        silence = base / "silence.wav"
        write(silence, np.zeros_like(time))
        report = module.analyze(silence)
        assert report["assertions"]["pcm_signal_present"] is False
        assert report["assertions"]["no_unplanned_silence_over_2s"] is False

        fixed = base / "fixed.wav"
        write(fixed, 8_000 * np.sin(2 * np.pi * 440 * time))
        report = module.analyze(fixed)
        assert report["assertions"]["melody_changes_pitch"] is False
        assert report["assertions"]["bass_changes_pitch"] is False

        bass_only = base / "bass-only.wav"
        bass_signal = np.zeros_like(time)
        for i, start in enumerate(np.arange(0, 8, 0.12)):
            part = (time >= start) & (time < min(start + 0.12, 8))
            local = time[part]
            bass_signal[part] = 9_000 * np.sin(2 * np.pi * (58 + (i % 5) * 8) * local)
        write(bass_only, bass_signal)
        report = module.analyze(bass_only)
        assert report["assertions"]["bass_changes_pitch"] is True
        assert report["assertions"]["melody_changes_pitch"] is False

        slow = base / "corrupt-tempo.wav"
        write(slow, compose(0.24))
        report = module.analyze(slow)
        assert report["tempo_step_seconds_estimate"] > 0.20
        assert report["assertions"]["tempo_stable_near_125_bpm"] is False

        planned = base / "planned-pause.wav"
        paused = tune.copy()
        paused[2 * rate : 5 * rate] = 0
        write(planned, paused)
        report = module.analyze(planned, allowed_silence=[(2.0, 5.0)])
        assert report["longest_silence_seconds"] >= 2.5
        assert report["assertions"]["no_unplanned_silence_over_2s"] is True

        mixer_lost = base / "mixer-lost-after-effect.wav"
        broken = tune.copy()
        broken[2 * rate :] = 0
        write(mixer_lost, broken)
        report = module.analyze(mixer_lost)
        assert report["assertions"]["pcm_signal_present"] is True
        assert report["assertions"]["no_unplanned_silence_over_2s"] is False
    print("PASS AY PCM analyzer accepts changing melody/bass and rejects silence and a stuck tone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
