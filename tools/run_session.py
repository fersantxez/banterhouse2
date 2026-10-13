#!/usr/bin/env python3
"""Run one child process with an exclusive lock and a private evidence folder.

The lock is an advisory OS lock, so a killed supervisor cannot leave a stale
lock behind. Every invocation writes its own manifest, stdout/stderr log and
final result. Child processes share a new process group so failure, timeout or
interruption can clean up only the process tree created by this invocation.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def process_group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def stop_group(pgid: int, grace: float, child: subprocess.Popen[bytes] | None = None) -> list[str]:
    """Stop only the process group created by this supervisor."""
    actions: list[str] = []
    if not process_group_exists(pgid):
        return actions
    try:
        os.killpg(pgid, signal.SIGTERM)
        actions.append("SIGTERM")
    except PermissionError:
        # Some macOS launch contexts restrict signaling a process group even
        # when the direct child is ours. Fall back to the Popen-owned PID.
        if child is None:
            return ["SIGTERM_DENIED"]
        try:
            child.terminate()
            actions.append("SIGTERM_PID_FALLBACK")
        except ProcessLookupError:
            return actions
    except ProcessLookupError:
        return actions
    deadline = time.monotonic() + grace
    while process_group_exists(pgid) and time.monotonic() < deadline:
        if child is not None:
            child.poll()  # reap the direct child so a zombie does not look live
        time.sleep(0.05)
    if process_group_exists(pgid):
        try:
            os.killpg(pgid, signal.SIGKILL)
            actions.append("SIGKILL")
        except PermissionError:
            if child is not None:
                try:
                    child.kill()
                    actions.append("SIGKILL_PID_FALLBACK")
                except ProcessLookupError:
                    pass
        except ProcessLookupError:
            pass
    return actions


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=Path("research/runs"))
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--lock-path", type=Path, default=Path("build/.caprice-session.lock"))
    parser.add_argument("--timeout", type=float, default=0, help="seconds; 0 waits until the child exits")
    parser.add_argument("--term-grace", type=float, default=2.0)
    parser.add_argument("--config-template", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("falta el comando después de --")
    if args.timeout < 0 or args.term_grace < 0:
        parser.error("timeout y term-grace deben ser >= 0")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    run_root = args.run_root.resolve()
    lock_path = args.lock_path.resolve()
    run_dir = args.run_dir.resolve() if args.run_dir else None
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_file = lock_path.open("a+")
    try:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"SESSION BUSY: {lock_path}", file=sys.stderr)
            return 73

        started = time.time()
        if run_dir is None:
            stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(started))
            run_dir = run_root / f"{stamp}-session-{uuid.uuid4().hex[:8]}"
        run_dir.mkdir(parents=True, exist_ok=False)
        log_path = run_dir / "session.log"
        result_path = run_dir / "result.json"
        manifest_path = run_dir / "session.json"

        command = [str(part) for part in args.command]
        config_copy = None
        if args.config_template:
            template = args.config_template.resolve()
            if not template.is_file():
                result_path.write_text(json.dumps({
                    "status": "fail", "reason": "config_template_missing",
                    "path": str(template), "cleanup": {"process_group": None}
                }, indent=2) + "\n")
                return 66
            config_copy = run_dir / template.name
            config_copy.write_bytes(template.read_bytes())
            command = [str(config_copy) if item == "{config}" else item for item in command]

        manifest = {
            "run_id": run_dir.name,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
            "cwd": os.getcwd(),
            "command": command,
            "lock_path": str(lock_path),
            "config_template": str(args.config_template.resolve()) if args.config_template else None,
            "config_sha256": sha256(config_copy) if config_copy else None,
            "pid": None,
            "process_group": None,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        cleanup_actions: list[str] = []
        interrupted: int | None = None
        proc: subprocess.Popen[bytes] | None = None

        def on_signal(signum: int, _frame: object) -> None:
            nonlocal interrupted
            interrupted = signum
            if proc is not None:
                cleanup_actions.extend(stop_group(proc.pid, args.term_grace, proc))

        old_handlers = {}
        for signum in (signal.SIGINT, signal.SIGTERM):
            old_handlers[signum] = signal.signal(signum, on_signal)
        status = "fail"
        reason = "launch_failed"
        exit_code: int | None = None
        timed_out = False
        try:
            with log_path.open("wb") as log:
                proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                manifest["pid"] = proc.pid
                manifest["process_group"] = proc.pid
                manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
                try:
                    exit_code = proc.wait(timeout=args.timeout or None)
                    if interrupted is not None:
                        reason = f"interrupted_signal_{interrupted}"
                    elif exit_code == 0:
                        status, reason = "pass", "child_exit_0"
                    else:
                        reason = "child_nonzero_exit"
                except subprocess.TimeoutExpired:
                    timed_out = True
                    reason = "timeout"
                    cleanup_actions.extend(stop_group(proc.pid, args.term_grace, proc))
                    exit_code = proc.wait(timeout=max(1.0, args.term_grace + 1.0))
                finally:
                    # A well-behaved command has no background descendants. Remove
                    # any descendants that outlive its direct child before release.
                    cleanup_actions.extend(stop_group(proc.pid, args.term_grace, proc))
        except OSError as error:
            reason = "launch_failed"
            exit_code = None
            (run_dir / "launch-error.txt").write_text(f"{type(error).__name__}: {error}\n")
        finally:
            for signum, handler in old_handlers.items():
                signal.signal(signum, handler)

        clean = not (proc is not None and process_group_exists(proc.pid))
        finished = time.time()
        result = {
            "run_id": run_dir.name,
            "status": "pass" if status == "pass" and clean else "fail",
            "reason": reason if clean else "cleanup_failed",
            "started_epoch": started,
            "finished_epoch": finished,
            "duration_seconds": round(finished - started, 3),
            "pid": proc.pid if proc else None,
            "process_group": proc.pid if proc else None,
            "exit_code": exit_code,
            "timed_out": timed_out,
            "signal": interrupted,
            "log": str(log_path) if log_path.exists() else None,
            "log_sha256": sha256(log_path) if log_path.exists() else None,
            "cleanup": {"actions": cleanup_actions, "process_group_absent": clean},
        }
        result_path.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, ensure_ascii=False))
        if not clean:
            return 70
        if interrupted is not None:
            return 128 + interrupted
        if timed_out:
            return 124
        return exit_code if exit_code is not None else 127
    finally:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        finally:
            lock_file.close()


if __name__ == "__main__":
    raise SystemExit(main())
