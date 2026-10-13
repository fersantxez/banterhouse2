#!/usr/bin/env python3
"""Validate the first machine arena against the fixed CPC gameplay contract."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "assets/levels/m1.json").read_text())
assert data["schema_version"] == 1 and data["id"] == "m1"
assert data["bounds"] == {"x": 0, "y": 0, "width": 160, "height": 200}
assert data["geometry_id"] == "opening_arena_v1"
assert data["spawn"] == {"x": 24, "y": 152}
assert data["pools"] == {"machines": 3, "projectiles": 4}
assert data["timing_ticks"] == {"initial_wait": 140, "warning": 35, "period": 112}
assert len(data["machines"]) == 1
machine = data["machines"][0]
assert machine == {"id": 0, "x": 110, "ground_y": 184, "direction": "right"}
assert data["presentation"]["shell_static"] is True
assert data["presentation"]["warning_lamp"] == "cyan"
print("PASS: m1.json respeta geometría, máquina de apertura separada y cadencia legible")
