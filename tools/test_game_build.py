#!/usr/bin/env python3
"""Verify header dependencies and compare the game with a clean Z80 build."""
import hashlib
import subprocess
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(args):
 return subprocess.run(args,cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True).stdout
for header in ('src/core/tuning.h','src/generated/level_data.h','src/generated/campaign_replay.h'):
 plan=run(['make','-n','-f','project.mk','all','-W',header])
 for source in ('src/core/player.c','src/main.c'):
  if ' -c  '+source+' ' not in plan:raise SystemExit(f'FAIL: {header} does not rebuild {source}')
print('PASS header dependency regression: physics, levels, replay rebuild Z80 objects')
with tempfile.TemporaryDirectory(prefix='game-repro-',dir=ROOT/'build') as td:
 out=Path(td).relative_to(ROOT)
 args=['make','-f','project.mk','all','SRCDIR=build/m1/src','M1_ONLY=1',f'OBJDIR={out}/obj',f'BINFILE={out}/DEVUELTO.bin',f'IHXFILE={out}/DEVUELTO.ihx',f'CDT={out}/DEVUELTO.cdt',f'DSK={out}/DEVUELTO.dsk',f'TARGET={out}/DEVUELTO.dsk']
 try:
  run(args)
  run([*args[:3], str(out/'DEVUELTO.cdt'), *args[4:]])
 except subprocess.CalledProcessError as e:print(e.stdout);raise
 for name in ('DEVUELTO.bin','DEVUELTO.dsk','DEVUELTO.cdt'):
  current=(ROOT/'build'/name).read_bytes();clean=(ROOT/out/name).read_bytes()
  if current!=clean:raise SystemExit('FAIL current game differs from clean build: '+name)
  print('PASS clean game matches '+name+' SHA-256 '+hashlib.sha256(current).hexdigest())
