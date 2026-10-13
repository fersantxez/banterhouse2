#!/usr/bin/env python3
"""Copia sólo las entradas CPC del renderer/audio original a un run nuevo."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT.parent / 'banterhouse'
ALLOWLIST = [
    'Makefile', 'README.md', 'cfg/build_config.mk',
    'src/game_render.c', 'src/game_render.h', 'src/render.c', 'src/render.h',
    'src/graphics.c', 'src/graphics.h', 'src/audio.c', 'src/audio.h',
    'src/font_renderer.s', 'src/game.c', 'src/game.h',
    'src/game_state.c', 'src/main.c',
    'src/banterhouse-theme.s', 'src/banterhouse-theme.h',
    'src/banterhouse-sfx.s', 'src/banterhouse-sfx.h',
]

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path)
    a=ap.parse_args()
    dest=(a.out or ROOT/'research/runs'/f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-O01-legacy").expanduser().resolve()
    runs=(ROOT/'research/runs').resolve()
    source=SOURCE_ROOT.resolve()
    if source != (ROOT.parent / 'banterhouse') or dest.exists() or dest==runs or runs not in dest.parents or source in dest.parents:
        raise SystemExit('FAIL: destino debe ser nuevo bajo research/runs; origen original fijo en solo lectura')
    records=[]
    for rel in ALLOWLIST:
        p=source/rel
        if not p.is_file():
            records.append({'path':rel,'status':'unavailable'})
            continue
        before=sha(p); size=p.stat().st_size
        q=dest/'snapshot/banterhouse'/rel
        q.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,q)
        stable=before==sha(p); exact=before==sha(q)
        records.append({'path':rel,'bytes':size,'sha256':before,'snapshot_sha256':sha(q),
                        'source_unchanged_during_copy':stable,'snapshot_exact':exact,
                        'status':'copied' if stable and exact else 'fail'})
    if any(x.get('status')=='fail' for x in records):
        raise SystemExit('FAIL: copia o lectura cambió; conservar y revisar este run')
    prior=source/'release/banterhouse-release'
    bins=sorted(str(p.relative_to(source)) for p in prior.rglob('*') if p.is_file() and p.suffix.lower() in {'.dsk','.cdt','.bin','.sna'}) if prior.exists() else []
    out={'task':'O01','scope':'read-only source copy; no original scripts, build, emulator or writes','source':str(source),
         'release_binary_candidates':bins,'entries':records,
         'scope_note':'No compatible historical DSK selected; old source build/product equivalence remains unverified.'}
    dest.mkdir(parents=True,exist_ok=True)
    (dest/'legacy-reference.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'run':str(dest),'copied':sum(x['status']=='copied' for x in records),
                      'unavailable':[x['path'] for x in records if x['status']=='unavailable'],
                      'release_binary_candidates':bins},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
