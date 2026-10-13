#!/usr/bin/env python3
"""Read emulator RAM evidence; never writes state or controls the emulator."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def inspect(snapshot, complete=False, map_path=None, bin_path=None, require_demo=True):
 data=Path(snapshot).read_bytes()
 if data[:8]!=b'MV - SNA' or len(data)!=256+128*1024:raise ValueError('SNA CPC 128 KiB requerido')
 map_path=Path(map_path) if map_path else ROOT/'build/DEVUELTO.map'
 bin_path=Path(bin_path) if bin_path else ROOT/'build/DEVUELTO.bin'
 mapping=map_path.read_text()
 match=re.search(r'^\s*([0-9A-F]{8})\s+_validation_state\s',mapping,re.M)
 if not match:raise ValueError('Falta símbolo de evidencia en mapa')
 address=int(match[1],16)
 ram=data[256:];binary=bin_path.read_bytes()
 # All game code, replay, physics, art and audio precede the linked SDK.
 # The disk loader stores four caller SP/IX words in CODE at 0x7284..0x728B;
 # those eight bytes are intentionally mutable while loading chapters.
 # CPCTelera also keeps keyboard bytes and self-modifying immediates in CODE,
 # so compare the immutable prefix while masking only documented work cells.
 sdk_start=min(int(v,16) for v in re.findall(r'^\s*([0-9A-F]{8})\s+_cpct_\w+\s',mapping,re.M))
 expected=bytearray(binary[:sdk_start-256]);actual=bytearray(ram[256:sdk_start])
 for start,end in ((0x7284,0x728C),):
  lo=max(0,start-0x100);hi=min(len(actual),end-0x100)
  if lo<hi:actual[lo:hi]=expected[lo:hi]
 if actual!=expected:raise ValueError('Snapshot no pertenece al código/recursos del candidato actual')
 if not require_demo:
  return {'snapshot':str(snapshot),'snapshot_sha256':hashlib.sha256(data).hexdigest(),'loaded_candidate_code':True,'checked_until':hex(sdk_start),'mutable_loader_cells':['0x7284-0x728b']}
 state=ram[address:address+40]
 if state[:3]!=bytes([0xB2,1,1]):raise ValueError('La demo no ha arrancado')
 report={'snapshot':str(snapshot),'snapshot_sha256':hashlib.sha256(data).hexdigest(),'address':hex(address),'stage':state[4]+1,'mode':state[3],'lives':state[5],'ticks':int.from_bytes(state[6:8],'little'),'completed_arenas':[i+1 for i,v in enumerate(state[8:32]) if v==1],'score':int.from_bytes(state[32:34],'little'),'x':state[34],'y':state[35],'error':state[36]}
 if complete:
  fixture=json.loads((ROOT/'tests/fixtures/campaign-replay.json').read_text())
  if report['stage']!=24 or report['mode']!=4 or report['ticks']!=fixture['ticks'] or report['completed_arenas']!=list(range(1,25)) or report['error'] or report['score']!=fixture['expected_terminal']['score']:raise ValueError('Partida incompleta o diferente: '+json.dumps(report))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('snapshot',type=Path);p.add_argument('--complete',action='store_true');p.add_argument('--image-only',action='store_true',help='verifica identidad de imagen RAM sin exigir replay activo');p.add_argument('--map',type=Path);p.add_argument('--bin',type=Path);a=p.parse_args()
 print(json.dumps(inspect(a.snapshot,a.complete,a.map,a.bin,not a.image_only),indent=2))
