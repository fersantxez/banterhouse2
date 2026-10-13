#!/usr/bin/env python3
"""Regression tests for building the Caprice cold-boot keyboard stream."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("run_game", ROOT / "tools/run_game.py")
assert SPEC and SPEC.loader
run_game = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_game)


def main() -> int:
    expected = 'run"DEVUELTO.BIN"CAP32_DELAY'
    assert run_game.caprice_autorun_command() == expected
    assert run_game.caprice_autorun_command("PLAY.BIN") == 'run"PLAY.BIN"CAP32_DELAY'
    assert run_game.caprice_media_commands(Path('game.dsk')) == [expected]
    assert run_game.caprice_media_commands(Path('loader.dsk'), 'LOADER.BIN') == [
        'run"LOADER.BIN"CAP32_DELAY']
    assert run_game.caprice_media_commands(Path('game.CDT')) == [
        '|tape', 'run""CAP32_DELAY', 'CAP32_DELAYCAP32_TAPEPLAYCAP32_DELAY ']
    for invalid in ("", "../DEVUELTO.BIN", "DEVUELTO.BIN\n", "DEVUELTO.BIN\"RUN"):
        try:
            run_game.caprice_autorun_command(invalid)
        except ValueError:
            continue
        raise AssertionError(f"unsafe CPC program name accepted: {invalid!r}")
    print("PASS run_game autorun: BASIC command, boot delay and CPC Return token")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
