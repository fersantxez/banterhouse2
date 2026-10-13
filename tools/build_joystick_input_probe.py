#!/usr/bin/env python3
"""Create a test-only input source that ignores keyboard and reads Joy0 only."""
from pathlib import Path
import re
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: build_joystick_input_probe.py INPUT_C OUTPUT_C", file=sys.stderr)
        return 2

    source = Path(sys.argv[1]).read_text()
    replacements = {
        r"cpct_isKeyPressed\(Key_CursorLeft\)\s*\|\|\s*cpct_isKeyPressed\(Joy0_Left\)":
            "cpct_isKeyPressed(Joy0_Left)",
        r"cpct_isKeyPressed\(Key_CursorRight\)\s*\|\|\s*cpct_isKeyPressed\(Joy0_Right\)":
            "cpct_isKeyPressed(Joy0_Right)",
        r"cpct_isKeyPressed\(Key_CursorUp\)\s*\|\|\s*cpct_isKeyPressed\(Joy0_Up\)":
            "cpct_isKeyPressed(Joy0_Up)",
        r"cpct_isKeyPressed\(Key_CursorDown\)\s*\|\|\s*cpct_isKeyPressed\(Joy0_Down\)":
            "cpct_isKeyPressed(Joy0_Down)",
        r"cpct_isKeyPressed\(Key_Space\)\s*\|\|\s*cpct_isKeyPressed\(Key_X\)\s*\|\|\s*\n\s*cpct_isKeyPressed\(Joy0_Fire1\)":
            "cpct_isKeyPressed(Joy0_Fire1)",
    }
    for pattern, replacement in replacements.items():
        source, count = re.subn(pattern, replacement, source)
        if count != 1:
            print(f"expected exactly one input mapping for {pattern}; found {count}", file=sys.stderr)
            return 1
    Path(sys.argv[2]).write_text(source)
    print("PASS: diagnostic input source samples Joy0 only; keyboard paths removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
