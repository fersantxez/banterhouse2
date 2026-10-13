#!/usr/bin/env python3
"""Build an isolated Caprice32 with host-side O02 Z80 cycle tracing."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from patch_caprice_timing import patch  # noqa: E402

PROFILE = ROOT / "cfg/emulator-timing.json"
URL = "https://github.com/ColinPitrat/caprice32.git"


def run(argv, *, cwd=None, log=None):
    proc = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    if log:
        Path(log).write_text(proc.stdout)
    if proc.returncode:
        tail = "\n".join(proc.stdout.splitlines()[-60:])
        raise RuntimeError(f"Command failed ({proc.returncode}): {argv!r}\n{tail}")
    return proc.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / ".tools/caprice32-src",
                        help="local clean checkout of the pinned upstream source")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    profile = json.loads(PROFILE.read_text())
    commit = profile["emulator"]["source_commit"]
    source = args.source.resolve()
    if not source.exists():
        source.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", URL, str(source)])
        run(["git", "-C", str(source), "checkout", "--quiet", commit])
    actual = run(["git", "-C", str(source), "rev-parse", "HEAD"]).strip()
    if actual != commit:
        raise RuntimeError(f"Caprice source must be {commit}, found {actual}")

    build_root = ROOT / "build/caprice-timing"
    checkout = build_root / "source"
    executable = checkout / "cap32"
    build_root.mkdir(parents=True, exist_ok=True)
    if not checkout.exists():
        run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(source), str(checkout)])
        run(["git", "-C", str(checkout), "checkout", "--quiet", commit])
    elif run(["git", "-C", str(checkout), "rev-parse", "HEAD"]).strip() != commit:
        raise RuntimeError(f"Generated Caprice checkout is not pinned to {commit}")

    z80 = (checkout / "src/z80.cpp").read_text()
    patched = patch(checkout)
    for relative in patched:
        if not (checkout / relative).is_file():
            raise RuntimeError(f"Incomplete Caprice instrumentation patch: {relative}")

    build_log = build_root / "build.log"
    run(["make", f"-j{args.jobs}", "ARCH=macos", "WITHOUT_GL=TRUE",
         f"APP_PATH={checkout}/"], cwd=checkout, log=build_log)
    if not executable.is_file():
        raise RuntimeError("Caprice build returned success without a cap32 executable")
    result = {
        "source_commit": commit,
        "patch_sha256": __import__("hashlib").sha256(
            "\n".join((checkout / p).read_text() for p in patched).encode()).hexdigest(),
        "executable": str(executable.relative_to(ROOT)),
        "executable_sha256": __import__("hashlib").sha256(executable.read_bytes()).hexdigest(),
        "build_log": str(build_log.relative_to(ROOT)),
        "patch_files": patched,
    }
    manifest = build_root / "manifest.json"
    manifest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
