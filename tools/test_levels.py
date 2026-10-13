#!/usr/bin/env python3
"""Positive/negative checks for level and geometry input validation."""
import copy
import json
import tempfile
from pathlib import Path

from build_levels import load_inputs, validate_geometry, validate_levels

ROOT = Path(__file__).resolve().parents[1]


def expect_rejected(name, callback):
    try:
        callback()
    except (ValueError, KeyError):
        return
    raise SystemExit(f"FAIL: entrada inválida aceptada: {name}")


def main():
    levels, geometries = load_inputs()
    if len(levels) != 24 or len(geometries) != 1:
        raise SystemExit("FAIL: inventario positivo inesperado")
    geometry = next(iter(geometries.values()))

    duplicate = copy.deepcopy(geometry)
    duplicate["surfaces"][1]["id"] = duplicate["surfaces"][0]["id"]
    expect_rejected("surface_id duplicado", lambda: validate_geometry(duplicate))

    zero_width = copy.deepcopy(geometry)
    zero_width["surfaces"][1]["width"] = 0
    expect_rejected("ancho cero", lambda: validate_geometry(zero_width))

    out_of_bounds = copy.deepcopy(geometry)
    out_of_bounds["surfaces"][1]["x"] = 159
    expect_rejected("superficie fuera de arena", lambda: validate_geometry(out_of_bounds))

    bad_reference = copy.deepcopy(levels)
    bad_reference[0]["geometry_id"] = "missing"
    expect_rejected("geometry_id inexistente", lambda: validate_levels(bad_reference, geometries))

    spawn_in_solid = copy.deepcopy(levels)
    spawn_in_solid[0]["spawn"]["y"] = 153
    expect_rejected("spawn dentro del suelo", lambda: validate_levels(spawn_in_solid, geometries))

    duplicate_arena = copy.deepcopy(levels)
    duplicate_arena[1]["id"] = duplicate_arena[0]["id"]
    expect_rejected("arena duplicada", lambda: validate_levels(duplicate_arena, geometries))

    print("PASS niveles: 24 arenas; negativos rechazados: ID, dimensiones, límites, referencia, spawn y duplicado")


if __name__ == "__main__":
    main()
