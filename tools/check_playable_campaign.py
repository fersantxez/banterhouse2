#!/usr/bin/env python3
"""Validate the embedded 24-screen campaign table and support geometry."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/main.c").read_text()
sys.path.insert(0, str(ROOT / "tools"))
from build_levels import load_inputs

stages, geometries = load_inputs()
assert len(stages) == 24
assert all(len(stage["machines"]) in (1, 2, 3) for stage in stages)
supports = {surface["y"]: surface for geometry in geometries.values()
            for surface in geometry["surfaces"]}
for stage in stages:
    assert stage["alberto"] in (True, False), stage["id"]
    for machine in stage["machines"]:
        support = supports.get(machine["ground_y"])
        assert support is not None, (stage["id"], machine)
        assert support["x"] <= machine["x"] <= support["x"] + support["width"] - 14
        assert machine["direction"] in (0, 1)

assert [len(stages[i]["machines"]) for i in (0, 1, 2)] == [1, 2, 3]
print("PASS estructural: 24 arenas desde JSON y apoyos declarados; no ejecuta reglas, combate ni final.")
