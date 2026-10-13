#!/usr/bin/env python3
"""Read (never alter) game state in native CPC snapshots for manual QA."""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SIZES={'pitu':19,'papers':24,'machines':21,'mode':1,'stage':1,'lives':1,'score':2,'ticks':2,'pause_return':1}
def read(path):
 data=Path(path).read_bytes();ram=data[256:]
 if data[:8]!=b'MV - SNA' or len(ram)!=128*1024:raise ValueError('Expected CPC 128K SNA')
 if ram[256:768]!=(ROOT/'build/DEVUELTO.bin').read_bytes()[:512]:raise ValueError('Different code')
 listing=(ROOT/'build/obj/main.rst').read_text()
 values={}
 for name,size in SIZES.items():
  match=re.search(r'^\s*([0-9A-F]{8})\s+\d+ _'+name+r':',listing,re.M)
  if not match:raise ValueError('Missing linked symbol '+name)
  addr=int(match[1],16);values[name]=ram[addr:addr+size].hex()
 return values
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('first',type=Path);p.add_argument('second',type=Path,nargs='?');a=p.parse_args()
 first=read(a.first)
 if a.second:
  second=read(a.second)
  assert first['mode']==second['mode']=='05','Not paused'
  assert first==second,'Simulation changed during pause'
  print(json.dumps({'pause_frozen':True,'state':first},indent=2))
 else:print(json.dumps(first,indent=2))
