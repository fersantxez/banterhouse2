#!/usr/bin/env python3
"""Capture a named macOS AVFoundation audio input to an evidence WAV."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import wave


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_audio_devices(ffmpeg: str) -> tuple[list[tuple[int, str]], str]:
    result = subprocess.run(
        [ffmpeg, "-hide_banner", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    listing = result.stdout
    if "AVFoundation audio devices:" not in listing:
        raise RuntimeError("FFmpeg did not return the AVFoundation audio-device list")
    devices = parse_audio_devices(listing)
    if not devices:
        raise RuntimeError("AVFoundation reported no audio inputs")
    return devices, listing


def parse_audio_devices(listing: str) -> list[tuple[int, str]]:
    if "AVFoundation audio devices:" not in listing:
        return []
    audio_listing = listing.split("AVFoundation audio devices:", 1)[1]
    return [(int(i), name.strip()) for i, name in re.findall(r"\[(\d+)\]\s+([^\r\n]+)", audio_listing)]


def capture(device: str, duration: float, output: Path, ffmpeg: str = "ffmpeg") -> dict[str, object]:
    binary = shutil.which(ffmpeg)
    if binary is None:
        raise FileNotFoundError(f"ffmpeg not found: {ffmpeg}")
    devices, listing = list_audio_devices(binary)
    matches = [index for index, name in devices if name == device]
    if len(matches) != 1:
        raise ValueError(f"expected one AVFoundation device named {device!r}, found {len(matches)}")
    index = matches[0]
    output.parent.mkdir(parents=True, exist_ok=True)
    start = datetime.now(timezone.utc).isoformat()
    command = [binary, "-hide_banner", "-y", "-f", "avfoundation", "-i", f":{index}",
               "-t", f"{duration:.3f}", "-af", "aresample=async=1:first_pts=0",
               "-c:a", "pcm_s16le", "-ac", "2", "-ar", "48000", str(output)]
    began = time.monotonic()
    try:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                check=False, timeout=duration + 30)
        returncode = result.returncode
        stderr = result.stderr[-4000:]
        error = None
    except subprocess.TimeoutExpired as timeout:
        returncode = None
        stderr = str(timeout)[-4000:]
        error = "capture_timeout"
    elapsed = time.monotonic() - began
    audio_duration = None
    if output.is_file() and output.stat().st_size > 44:
        try:
            with wave.open(str(output), "rb") as wav:
                audio_duration = wav.getnframes() / wav.getframerate()
        except (wave.Error, EOFError):
            audio_duration = None
    complete = (returncode == 0 and audio_duration is not None
                and audio_duration >= duration * 0.95 and output.stat().st_size > 44)
    report_path = output.with_suffix(output.suffix + ".capture.json")
    if complete:
        reason = "capture_complete"
    elif error:
        reason = error
    elif returncode != 0:
        reason = "ffmpeg_failed_or_empty_wav"
    elif audio_duration is None:
        reason = "invalid_wav"
    else:
        reason = "capture_shorter_than_requested"
    report: dict[str, object] = {
        "status": "pass" if complete else "fail",
        "reason": reason,
        "started_utc": start,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "device_name": device,
        "device_index_resolved_at_runtime": index,
        "device_listing": listing,
        "ffmpeg": binary,
        "ffmpeg_version": subprocess.run([binary, "-version"], text=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, check=False).stdout.splitlines()[0],
        "command": command,
        "requested_duration_seconds": duration,
        "wav_duration_seconds": round(audio_duration, 3) if audio_duration is not None else None,
        "returncode": returncode,
        "stderr": stderr,
        "wav": str(output.resolve()) if output.exists() else None,
        "wav_bytes": output.stat().st_size if output.exists() else 0,
        "wav_sha256": sha256(output) if output.is_file() else None,
        "report_path": str(report_path.resolve()),
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="destination WAV path")
    parser.add_argument("--device", default="BlackHole 2ch", help="exact AVFoundation input name")
    parser.add_argument("--duration", type=float, default=60, help="capture duration in seconds")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    if args.duration <= 0:
        parser.error("--duration must be > 0")
    try:
        report = capture(args.device, args.duration, args.output, args.ffmpeg)
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "fail", "error": str(error)}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
