#!/usr/bin/env python3
"""Reject malformed M0 level data before emitting the CPC table."""
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_m0_level", ROOT / "tools/build_m0_level.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source = json.loads((ROOT / "assets/levels/m0.json").read_text())


def reject(name, mutate, fragment):
    candidate = copy.deepcopy(source)
    mutate(candidate)
    try:
        module.generate(candidate)
    except (KeyError, ValueError) as error:
        if fragment not in str(error):
            raise SystemExit(f"FAIL {name}: mensaje no específico: {error}")
        return
    raise SystemExit(f"FAIL {name}: geometry invalid accepted")


reject("duplicate-id", lambda d: d["surfaces"][2].update(id=1), "duplicado")
reject("out-of-bounds", lambda d: d["surfaces"][1].update(x=159), "sale del lienzo")
reject("missing-platform", lambda d: d["surfaces"].pop(), "se requiere suelo")
reject("unknown-kind", lambda d: d["surfaces"][1].update(kind="decoration"), "desconocido")
reject("unsupported-spawn", lambda d: d["spawn"].update(y=150), "spawn debe apoyar")
print("PASS: 5 geometrías M0 inválidas rechazadas con causa específica")
