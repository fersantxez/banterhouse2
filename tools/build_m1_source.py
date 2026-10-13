#!/usr/bin/env python3
"""Create the lean CPC source tree for the single-arena M1 playtest build."""
import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M1_DROP = {"bg2", "bg3", "bg4", "palette2", "palette3", "palette4"}
CAMPAIGN_DROP = {"bg1", "bg2", "bg3", "bg4"}
EXPERIMENT_FILES = {"state.c", "state.h", "banks.c", "banks.h", "bank_page.s", "render_g.c", "render_g.h"}


def filter_assets(source: Path, destination: Path, campaign: bool = False) -> None:
    drop = CAMPAIGN_DROP if campaign else M1_DROP
    text = source.read_text()
    lines = text.splitlines(keepends=True)
    chunks = []
    current = []
    current_symbol = None
    for line in lines:
        match = re.match(r"\.globl _([A-Za-z0-9_]+)\s*$", line.strip())
        if match:
            if current and current_symbol not in drop:
                chunks.extend(current)
            current = [line]
            current_symbol = match.group(1)
        else:
            current.append(line)
    if current and current_symbol not in drop:
        chunks.extend(current)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(chunks))
    kept = sorted({m.group(1) for m in re.finditer(r"^\.globl _([A-Za-z0-9_]+)$", "".join(chunks), re.M)})
    missing = drop & set(kept)
    if missing:
        raise SystemExit(f"FAIL: M1 asset filter retained {sorted(missing)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--campaign", action="store_true", help="omit all embedded chapter backgrounds; the DSK loader streams them")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve() if not args.output.is_absolute() else args.output
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(ROOT / "src", output,
                    ignore=lambda _directory, names: [name for name in names if name in EXPERIMENT_FILES])
    filter_assets(ROOT / "src/generated/runtime_assets.s",
                  output / "generated/runtime_assets.s", args.campaign)
    if args.campaign:
        print(f"PASS: campaign source prepared at {output}; all four backgrounds load from AMSDOS files")
    else:
        print(f"PASS: M1 source prepared at {output}; omitted 3 non-M1 backgrounds and palettes")


if __name__ == "__main__":
    main()
