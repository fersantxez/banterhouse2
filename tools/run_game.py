#!/usr/bin/env python3
"""Launch a DSK or CDT through the supervised Caprice32 session runner."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def caprice_autorun_command(program: str = 'DEVUELTO.BIN') -> str:
    """Type a BASIC RUN and delay the line's implicit Return until ready.

    Caprice32 4.6's --autocmd is a key event stream; it does not submit a
    BASIC line on its own. The parser appends a line feed (mapped to CPC
    Return) to every autocmd. CAP32_DELAY waits boot_time frames before that
    final event, so the firmware has accepted the complete command first.
    """
    if not program or any(ch not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._" for ch in program.upper()):
        raise ValueError("program name must be a CPC-safe filename")
    return f'run"{program}"CAP32_DELAY'


def caprice_media_commands(path: Path, program: str = 'DEVUELTO.BIN') -> list[str]:
    if path.suffix.lower() == '.cdt':
        return ['|tape', 'run""CAP32_DELAY', 'CAP32_DELAYCAP32_TAPEPLAYCAP32_DELAY ']
    # RUN is required for CPC BASIC to load large machine-code files at &0100.
    # The game enables AMSDOS itself after restoring the firmware.
    return [caprice_autorun_command(program)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disk", nargs="?", type=Path, default=ROOT / "release/Devuelto-CPC6128.dsk")
    parser.add_argument("--emulator", type=Path, default=ROOT / ".tools/cap32", help="path to a local Caprice32 executable")
    parser.add_argument("--program", default="DEVUELTO.BIN", help="BIN to RUN from a disk (default: DEVUELTO.BIN)")
    parser.add_argument("--timeout", type=float, default=0, help="segundos; 0 mantiene Caprice hasta cerrarlo")
    parser.add_argument("--run-root", type=Path, default=ROOT / "research/runs")
    parser.add_argument("--lock-path", type=Path, default=ROOT / "build/.caprice-session.lock")
    parser.add_argument("--config-template", type=Path, default=ROOT / ".tools/cap32.cfg")
    args = parser.parse_args()
    disk = args.disk.resolve()
    emulator = args.emulator.resolve()
    config = args.config_template.resolve()
    for path in (disk, emulator, config):
        if not path.is_file():
            parser.error(f"No existe {path}")
    if args.timeout < 0:
        parser.error("--timeout debe ser >= 0")

    if disk.suffix.lower() != '.cdt':
        try:
            caprice_autorun_command(args.program)
        except ValueError as error:
            parser.error(str(error))
    autorun = [item for line in caprice_media_commands(disk, args.program) for item in ('-a', line)]

    command = [
        sys.executable,
        str(ROOT / "tools/run_session.py"),
        "--run-root", str(args.run_root.resolve()),
        "--lock-path", str(args.lock_path.resolve()),
        "--config-template", str(config),
        "--timeout", str(args.timeout),
        "--", str(emulator), "-v", "-c", "{config}",
        *autorun, str(disk),
    ]
    medium_name = "la cinta" if disk.suffix.lower() == ".cdt" else "el disco"
    print(f"Cargando desde {medium_name}. Tras la portada aparecerá el menú. Cierra Caprice para terminar.", flush=True)
    return subprocess.call(command, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
