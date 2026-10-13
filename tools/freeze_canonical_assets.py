#!/usr/bin/env python3
"""Freeze the already imported CPC studies with source and content hashes."""
import hashlib
import json
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIES = ROOT / "assets/cpc-studies"
DEST = ROOT / "assets/source/canonical"
SOURCE_MANIFEST = STUDIES / "manifest.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accept-revision', action='store_true',
                        help='replace previously frozen resources after an intentional source-study revision')
    args = parser.parse_args()
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    expected_sprites = manifest["sprites"]
    scene_hashes = {scene["name"]: scene["sha256_scr"] for scene in manifest["scenes"]}
    names = []
    for slug in ("01-copias", "02-produccion", "03-calle", "04-purple"):
        names.extend(f"{slug}{suffix}" for suffix in (
            ".scr", ".background.scr", ".background.scr.zx0", ".fwpal", ".hwpal",
            ".tiles.bin", ".map.bin", ".native.png"))
    names.extend(("g_pitu.masked.bin", "g_pitu_walk.masked.bin", "g_alberto.masked.bin"))

    records = []
    for name in names:
        source = STUDIES / name
        if not source.is_file():
            raise SystemExit(f"FAIL: missing canonical source file {source}")
        digest = sha256(source)
        if name.endswith(".scr") and not name.endswith(".background.scr"):
            slug = name.removesuffix(".scr")
            if scene_hashes.get(slug) != digest:
                raise SystemExit(f"FAIL: {name} disagrees with source-study manifest")
        sprite_id = name.removesuffix(".masked.bin")
        if sprite_id in expected_sprites and expected_sprites[sprite_id]["sha256"] != digest:
            raise SystemExit(f"FAIL: {name} disagrees with source-study manifest")
        destination = DEST / name
        if destination.exists() and sha256(destination) != digest and not args.accept_revision:
            raise SystemExit(f"FAIL: refusing to replace changed canonical file {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists() or (args.accept_revision and sha256(destination) != digest):
            shutil.copyfile(source, destination)
        if sha256(destination) != digest:
            raise SystemExit(f"FAIL: copy verification failed for {destination}")
        records.append({"path": name, "source": f"assets/cpc-studies/{name}",
                        "bytes": source.stat().st_size, "sha256": digest})

    frozen = {
        "schema_version": 1,
        "purpose": "Frozen CPC Mode 0 source resources for Banterhouse 2; no preview recoloring.",
        "upstream_source": manifest["source"],
        "upstream_source_sha256": manifest["source_sha256"],
        "upstream_palette_source_sha256": manifest["source_palette_main_c_sha256"],
        "upstream_manifest": "assets/cpc-studies/manifest.json",
        "upstream_manifest_sha256": sha256(SOURCE_MANIFEST),
        "files": records,
    }
    (DEST / "manifest.json").write_text(json.dumps(frozen, indent=2) + "\n")
    print(f"PASS: froze {len(records)} canonical inputs under {DEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
