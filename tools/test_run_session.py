#!/usr/bin/env python3
"""Lifecycle and negative-path tests for tools/run_session.py."""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_session.py"
PYTHON = sys.executable


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


class SessionCase:
    def __init__(self, folder: Path):
        self.folder = folder
        self.run_root = folder / "runs"
        self.lock = folder / "exclusive.lock"
        self.run_root.mkdir(parents=True)

    def command(self, *child: str, timeout: float = 0, term_grace: float = 0.2,
                run_dir: Path | None = None) -> list[str]:
        args = [PYTHON, str(RUNNER), "--run-root", str(self.run_root),
                "--lock-path", str(self.lock), "--timeout", str(timeout),
                "--term-grace", str(term_grace)]
        if run_dir:
            args += ["--run-dir", str(run_dir)]
        return args + ["--", *child]

    def outcome(self, name: str) -> dict:
        matches = list(self.run_root.glob(f"{name}/result.json"))
        if not matches:
            raise AssertionError(f"no result.json for {name}")
        return json.loads(matches[0].read_text())


def wait_for_manifest(folder: Path) -> dict:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        for path in folder.rglob("session.json"):
            data = json.loads(path.read_text())
            if data.get("pid"):
                return {"path": path, **data}
        time.sleep(0.02)
    raise AssertionError("child did not start")


def run(folder: Path) -> dict:
    folder.mkdir(parents=True, exist_ok=False)
    case = SessionCase(folder)
    # Success; log is unique, hash is present, and the lock is reusable after exit.
    rc = subprocess.run(case.command(PYTHON, "-c", "print('hello supervisor')"), capture_output=True, text=True, timeout=10)
    success = case.outcome(next(p.name for p in case.run_root.iterdir()))
    assert rc.returncode == 0 and success["status"] == "pass" and success["cleanup"]["process_group_absent"]
    assert success["log_sha256"] and "hello supervisor" in Path(success["log"]).read_text()

    # Launch failure and crashing child both produce explicit FAIL records.
    fail_dir = case.run_root / "launch-failure"
    rc = subprocess.run(case.command("/definitely/missing/caprice" , run_dir=fail_dir), capture_output=True, text=True, timeout=10)
    launch_fail = json.loads((fail_dir / "result.json").read_text())
    assert rc.returncode == 127 and launch_fail["reason"] == "launch_failed" and launch_fail["cleanup"]["process_group_absent"]
    missing_config_dir = case.run_root / "missing-config"
    rc = subprocess.run([PYTHON, str(RUNNER), "--run-root", str(case.run_root), "--run-dir", str(missing_config_dir),
                         "--lock-path", str(case.lock), "--config-template", str(folder / "absent.cfg"), "--",
                         PYTHON, "-c", "raise SystemExit('must not launch')"], capture_output=True, text=True, timeout=5)
    missing_config = json.loads((missing_config_dir / "result.json").read_text())
    assert rc.returncode == 66 and missing_config["reason"] == "config_template_missing"
    assert missing_config["cleanup"]["process_group"] is None
    invalid_disk = subprocess.run([PYTHON, str(ROOT / "tools/run_game.py"), str(folder / "absent.dsk")],
                                  capture_output=True, text=True, timeout=5)
    assert invalid_disk.returncode == 2 and "No existe" in invalid_disk.stderr
    crash_dir = case.run_root / "child-crash"
    rc = subprocess.run(case.command(PYTHON, "-c", "import os; os.abort()", run_dir=crash_dir), capture_output=True, text=True, timeout=10)
    crash = json.loads((crash_dir / "result.json").read_text())
    assert rc.returncode != 0 and crash["status"] == "fail" and crash["exit_code"] != 0

    # Timeout kills the session group and does not affect an unrelated process.
    sentinel = subprocess.Popen([PYTHON, "-c", "import time; time.sleep(30)"], start_new_session=True)
    timeout_dir = case.run_root / "timeout"
    try:
        rc = subprocess.run(case.command(PYTHON, "-c", "import time; time.sleep(30)", timeout=0.2,
                                         term_grace=0.2, run_dir=timeout_dir), capture_output=True, text=True, timeout=10)
        timed = json.loads((timeout_dir / "result.json").read_text())
        assert rc.returncode == 124 and timed["reason"] == "timeout" and timed["cleanup"]["process_group_absent"]
        assert alive(sentinel.pid), "unrelated sentinel process was terminated"
    finally:
        sentinel.terminate()
        sentinel.wait(timeout=3)

    # A second invocation cannot launch while the first owns the OS lock.
    first_dir = case.run_root / "exclusive-first"
    first = subprocess.Popen(case.command(PYTHON, "-c", "import time; time.sleep(30)", run_dir=first_dir),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    manifest = wait_for_manifest(first_dir)
    second = subprocess.run(case.command(PYTHON, "-c", "raise SystemExit('must not launch')"),
                            capture_output=True, text=True, timeout=5)
    assert second.returncode == 73 and "SESSION BUSY" in second.stderr
    first.send_signal(signal.SIGINT)
    first.wait(timeout=5)
    interrupted = json.loads((first_dir / "result.json").read_text())
    assert first.returncode == 130 and interrupted["signal"] == signal.SIGINT
    assert interrupted["cleanup"]["process_group_absent"]

    # A stale lock file has no stale kernel lock; flock safely reclaims it.
    case.lock.write_text("pid=999999; owner=crashed-process\n")
    stale = subprocess.run(case.command(PYTHON, "-c", "pass"), capture_output=True, text=True, timeout=5)
    stale_run = sorted(case.run_root.glob("*-session-*"), key=lambda p: p.stat().st_mtime)[-1]
    stale_result = json.loads((stale_run / "result.json").read_text())
    assert stale.returncode == 0 and stale_result["status"] == "pass"

    # SIGKILL of the runner releases the kernel lock. Clean the child it orphaned
    # by its exact session ID so this negative test itself leaves no process.
    abandoned_dir = case.run_root / "abandoned-supervisor"
    abandoned = subprocess.Popen(case.command(PYTHON, "-c", "import time; time.sleep(30)", run_dir=abandoned_dir),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    abandoned_manifest = wait_for_manifest(abandoned_dir)
    child_pgid = int(abandoned_manifest["process_group"])
    os.kill(abandoned.pid, signal.SIGKILL)
    abandoned.wait(timeout=5)
    # The direct child is deliberately orphaned after supervisor SIGKILL.
    # Reap only that exact process group, then verify lock recovery.
    try:
        os.killpg(child_pgid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    deadline = time.monotonic() + 3
    while alive(int(abandoned_manifest["pid"])) and time.monotonic() < deadline:
        time.sleep(0.05)
    recovery = subprocess.run(case.command(PYTHON, "-c", "pass"), capture_output=True, text=True, timeout=5)
    assert recovery.returncode == 0

    # Config template substitution creates a private, byte-identical copy.
    cfg = folder / "template.cfg"
    cfg.write_text("model=2\n")
    config_dir = case.run_root / "config-copy"
    rc = subprocess.run([PYTHON, str(RUNNER), "--run-root", str(case.run_root), "--run-dir", str(config_dir),
                         "--lock-path", str(case.lock), "--config-template", str(cfg), "--", PYTHON, "-c",
                         "import pathlib,sys; assert pathlib.Path(sys.argv[1]).read_text() == 'model=2\\n'", "{config}"],
                        capture_output=True, text=True, timeout=5)
    config_result = json.loads((config_dir / "result.json").read_text())
    assert rc.returncode == 0 and config_result["status"] == "pass"
    assert (config_dir / "template.cfg").read_bytes() == cfg.read_bytes()

    return {"success": "pass", "launch_failure": "pass", "missing_config_no_spawn": "pass",
            "invalid_disk_preflight": "pass", "child_crash": "pass",
            "timeout_cleanup": "pass", "unrelated_process_survived": "pass",
            "exclusive_second_invocation": "pass", "interrupt_cleanup": "pass",
            "stale_lock_recovery": "pass", "abandoned_lock_recovery": "pass",
            "private_config": "pass", "children": 11}


def main() -> int:
    destination = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    temporary = None
    if destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
        root = destination.parent / f"details-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{os.getpid()}"
        root.mkdir(parents=True, exist_ok=False)
    else:
        temporary = tempfile.TemporaryDirectory(prefix="bh2-run-session-")
        root = Path(temporary.name)
    result = run(root / "case")
    if destination:
        files = []
        for path in sorted(root.rglob("*")):
            if path.is_file():
                files.append({"path": str(path.relative_to(destination.parent)),
                              "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                              "bytes": path.stat().st_size})
        destination.write_text(json.dumps({"status": "pass", "cases": result,
                                           "evidence_root": str(root.relative_to(destination.parent)),
                                           "evidence_files": files}, indent=2) + "\n")
    print("PASS run_session lifecycle: " + json.dumps(result, sort_keys=True))
    if temporary:
        temporary.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
