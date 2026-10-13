#!/usr/bin/env python3
"""Check saved Caprice32 gate-array palette snapshots for all gallery scenes."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_caprice_snapshot_palette import check_palette  # noqa: E402

SCENES = ("01-copias", "02-produccion", "03-calle", "04-purple")
SNAPSHOTS = ROOT / "research/runs/20261012T234446Z-T03-snapshot-palette/caprice"

for scene in SCENES:
    check_palette(scene, SNAPSHOTS / f"{scene}.sna")
