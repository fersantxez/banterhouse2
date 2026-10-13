#!/usr/bin/env python3
"""Verify frozen source assets without consulting the original project."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets/source/canonical"
manifest = json.loads((BASE / "manifest.json").read_text())
seen = set()
for record in manifest["files"]:
    name = record["path"]
    if name in seen:
        raise SystemExit(f"FAIL: duplicate canonical path {name}")
    seen.add(name)
    path = BASE / name
    if not path.is_file():
        raise SystemExit(f"FAIL: missing frozen asset {name}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if path.stat().st_size != record["bytes"] or actual != record["sha256"]:
        raise SystemExit(f"FAIL: frozen asset differs from manifest: {name}")
if len(seen) != 35:
    raise SystemExit(f"FAIL: expected 35 frozen source inputs, found {len(seen)}")
print(f"PASS: {len(seen)} frozen inputs match source manifest hashes; original project not read")
