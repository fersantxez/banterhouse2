#!/usr/bin/env python3
"""Build, execute, and verify one CPC case from an actual Caprice32 SNA/trace."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cpc_backend

DEFAULT_CASE = ROOT / "tests/cpc/telemetry/case.json"
DEFAULT_PROFILE = ROOT / "cfg/emulator-timing.json"


class RunnerError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def load_case(value: str) -> tuple[Path, dict[str, Any]]:
    path = DEFAULT_CASE if value == "telemetry" else Path(value)
    if not path.is_absolute():
        path = ROOT / path
    data = json.loads(path.read_text())
    for key in ("case_id", "build_id", "binary", "disk", "map", "autocmd", "markers"):
        if key not in data:
            raise RunnerError(f"case manifest missing {key}")
    return path.resolve(), data


def set_ini_value(text: str, section: str, key: str, value: str) -> str:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines)
                  if line.strip() == f"[{section}]"), None)
    if start is None:
        lines.extend(["", f"[{section}]", f"{key}={value}"])
        return "\n".join(lines) + "\n"
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].strip().startswith("[") and lines[i].strip().endswith("]")), len(lines))
    for i in range(start + 1, end):
        if re.match(rf"^\s*{re.escape(key)}\s*=", lines[i]):
            lines[i] = f"{key}={value}"
            break
    else:
        lines.insert(end, f"{key}={value}")
    return "\n".join(lines) + "\n"


def write_effective_config(profile: dict[str, Any], out: Path) -> Path:
    source = ROOT / ".tools/cap32.cfg"
    if not source.is_file():
        raise FileNotFoundError(f"missing pinned Caprice config: {source}")
    text = source.read_text()
    settings = profile["settings"]
    machine = profile["machine"]
    values = (
        ("system", "model", str(machine["caprice_model_id"])),
        ("system", "ram_size", str(machine["ram_kib"])),
        ("system", "speed", str(settings["speed_mhz"])),
        ("system", "limit_speed", "1" if settings["speed_limit"] else "0"),
        ("system", "auto_pause", "0"),
        ("video", "scr_fps", "1" if settings["fps_osd"] else "0"),
        ("sound", "enabled", "1" if settings["audio_emulation"] else "0"),
        ("file", "snap_path", str(out.resolve())),
    )
    for section, key, value in values:
        text = set_ini_value(text, section, key, value)
    path = out / "caprice-timing.cfg"
    path.write_text(text)
    return path


def build_artifacts(out: Path) -> dict[str, Any]:
    log = out / "build.log"
    proc = subprocess.run(["make", "test-o02-probe"], cwd=ROOT, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_text(proc.stdout)
    if proc.returncode:
        raise RunnerError(f"CPC probe build failed with {proc.returncode}; see {log}")
    return {
        "binary": ROOT / "build/o02-probe/O02.bin",
        "disk": ROOT / "build/o02-probe/O02.dsk",
        "map": ROOT / "build/o02-probe/O02.map",
        "build_log": log,
    }


def make_marker_file(case: dict[str, Any], map_path: Path, out: Path) -> Path:
    symbols = cpc_backend.parse_map_symbols(map_path)
    lines = []
    for marker in case["markers"]:
        address = cpc_backend.require_symbol(symbols, marker["symbol"])
        lines.append(f"{address:04X}\t{marker['label']}")
    path = out / "markers.tsv"
    path.write_text("\n".join(lines) + "\n")
    return path


def run_caprice(executable: Path, config: Path, disk: Path, autocmd: str,
                marker_path: Path, trace_path: Path, snapshot_path: Path,
                timeout_seconds: float, out: Path) -> tuple[int, float, str]:
    env = os.environ.copy()
    env.update({
        "BH2_TRACE_MARKERS": str(marker_path.resolve()),
        "BH2_CYCLE_TRACE": str(trace_path.resolve()),
        "BH2_SNAPSHOT_OUT": str(snapshot_path.resolve()),
    })
    command = [str(executable), "-v", "-c", str(config), "-a", autocmd, str(disk)]
    start = time.monotonic()
    try:
        proc = subprocess.run(command, cwd=ROOT, env=env, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              timeout=timeout_seconds)
        elapsed = time.monotonic() - start
        (out / "caprice.log").write_text(proc.stdout)
        return proc.returncode, elapsed, ""
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - start
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        (out / "caprice.log").write_text(output)
        return 124, elapsed, f"timeout after {timeout_seconds:.2f}s"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, help="'telemetry' or a case.json path")
    parser.add_argument("--variant", required=True, help="frozen variant identifier")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="host watchdog only; it is never reported as CPC cycles")
    parser.add_argument("--caprice-source", type=Path,
                        help="clean checkout at the pinned Caprice32 commit; otherwise .tools/caprice32-src")
    parser.add_argument("--no-build", action="store_true")
    args = parser.parse_args()

    try:
        if args.timeout <= 0:
            raise ValueError("--timeout must be positive")
        profile_path = args.profile if args.profile.is_absolute() else ROOT / args.profile
        case_path, case = load_case(args.case)
        profile_path = profile_path.resolve()
        profile = json.loads(profile_path.read_text())
        out = args.out if args.out.is_absolute() else ROOT / args.out
        out = out.resolve()
        out.mkdir(parents=True, exist_ok=True)
        if any(out.iterdir()):
            raise ValueError(f"output directory must be empty: {out}")

        required_profile = ("machine", "emulator", "settings", "measurement", "rom_sha256")
        missing = [field for field in required_profile if field not in profile]
        if missing:
            raise ValueError(f"incomplete timing profile: {', '.join(missing)}")
        if profile["machine"]["model"] != "CPC6128 classic" or profile["machine"]["ram_kib"] != 128:
            raise ValueError("O02 accepts only the CPC6128 classic 128 KiB profile")

        build = build_artifacts(out) if not args.no_build else {
            "binary": ROOT / case["binary"], "disk": ROOT / case["disk"],
            "map": ROOT / case["map"], "build_log": None,
        }
        binary, disk, map_path = (Path(build[name]) for name in ("binary", "disk", "map"))
        for path in (binary, disk, map_path):
            if not path.is_file():
                raise FileNotFoundError(f"probe artifact missing: {path}")
        for key, path in (("binary", binary), ("disk", disk), ("map", map_path)):
            if case.get(key) and Path(case[key]) != path.relative_to(ROOT):
                raise RunnerError(f"case artifact path mismatch for {key}: {case[key]} vs {path}")

        caprice_builder = ROOT / "tools/build_caprice_timing.py"
        caprice_manifest = ROOT / "build/caprice-timing/manifest.json"
        if not args.no_build or not (ROOT / profile["emulator"]["instrumented_binary"]).is_file():
            build_command = [sys.executable, str(caprice_builder)]
            if args.caprice_source:
                source = args.caprice_source if args.caprice_source.is_absolute() else ROOT / args.caprice_source
                build_command.extend(["--source", str(source.resolve())])
            proc = subprocess.run(build_command, cwd=ROOT, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (out / "caprice-build.log").write_text(proc.stdout)
            if proc.returncode:
                raise RunnerError(f"instrumented Caprice build failed with {proc.returncode}")
        emulator = ROOT / profile["emulator"]["instrumented_binary"]
        if not emulator.is_file() or not caprice_manifest.is_file():
            raise FileNotFoundError("instrumented Caprice binary or manifest is missing")

        config = write_effective_config(profile, out)
        markers = make_marker_file(case, map_path, out)
        trace = out / "cycles.csv"
        snapshot = out / "capture.sna"
        command_result, host_seconds, timeout_reason = run_caprice(
            emulator, config, disk, case["autocmd"], markers, trace, snapshot,
            args.timeout, out)
        commands = [{
            "argv": [str(emulator), "-v", "-c", str(config), "-a", case["autocmd"], str(disk)],
            "cwd": str(ROOT), "exit_code": command_result,
            "stdout": "caprice.log", "stderr": "caprice.log",
            "host_wall_seconds": host_seconds,
            "wall_time_is_cpc_cycles": False,
        }]
        if command_result != 0:
            raise RunnerError(timeout_reason or f"Caprice returned {command_result}")
        if not trace.is_file():
            raise RunnerError("Caprice exited without a cycle dump")
        if not snapshot.is_file():
            raise RunnerError("Caprice exited without a CPC snapshot")

        snapshot_result = cpc_backend.validate_snapshot(snapshot, case, binary, map_path)
        trace_result = cpc_backend.parse_cycle_trace(trace, case["markers"], profile)
        dumps = cpc_backend.write_dumps(snapshot, out / "dumps")
        case_result = {
            "id": case["case_id"], "status": "PASS",
            "evidence": ["capture.sna", "cycles.csv", *[str(Path(p).relative_to(out)) for p in dumps.values()]],
            "snapshot": snapshot_result,
            "timing": {key: value for key, value in trace_result.items() if key != "events"},
        }
        summary = {
            "schema_version": 1,
            "task_id": "O02",
            "variant": args.variant,
            "profile_id": profile["profile_id"],
            "case_id": case["case_id"],
            "case_build_id": case["build_id"],
            "binary_sha256": sha256(binary),
            "disk_sha256": sha256(disk),
            "map_sha256": sha256(map_path),
            "profile_sha256": sha256(profile_path),
            "effective_config_sha256": sha256(config),
            "emulator_sha256": sha256(emulator),
            "rom_sha256": profile["rom_sha256"],
            "expected_markers": len(case["markers"]),
            "observed_markers": trace_result["rows"],
            "cycle_resolution_cycles": trace_result["cycle_resolution_cycles"],
            "vsync_calibration": trace_result["vsync_calibration"],
            "snapshot": snapshot_result,
            "unmeasured": ["production gameplay phases; later fixture tasks add those symbols"],
        }
        json_write(out / "summary.json", summary)
        results = {
            "schema_version": 1, "task_id": "O02", "build_id": case["build_id"],
            "environment": {"profile": profile["profile_id"], "model": profile["machine"]["model"],
                             "ram_kib": profile["machine"]["ram_kib"],
                             "emulator_source_commit": profile["emulator"]["source_commit"]},
            "commands": commands,
            "cases": [case_result],
            "unmeasured": summary["unmeasured"],
            "next_step": "Integrate phase labels into frozen M2 load in O03/O04; do not treat probe time as game cost.",
        }
        json_write(out / "results.json", results)
        print(json.dumps({"status": "PASS", "out": str(out),
                          "vsync_calibration": trace_result["vsync_calibration"],
                          "snapshot_sha256": snapshot_result["snapshot_sha256"]}, indent=2))
        return 0
    except FileNotFoundError as exc:
        print(f"ENVIRONMENT MISSING: {exc}", file=sys.stderr)
        return 2
    except (ValueError, OSError, RunnerError, cpc_backend.BackendError,
            subprocess.SubprocessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
