#!/usr/bin/env python3
"""Remove study-only copiers from runtime backgrounds, leaving canonical art intact."""
from pathlib import Path
import build_cpc_screen_studies as art
ROOT=Path(__file__).resolve().parents[1]
SLUGS=('01-copias','02-produccion','03-calle','04-purple')
def clean_background(kind):
 sprites={name:(ROOT/'assets/source/canonical'/f'{name}.masked.bin').read_bytes() for name in ('g_pitu','g_pitu_walk','g_alberto')}
 machine=art.machine
 try:
  _,original,_,_,_=art.scene(kind,sprites)
  art.machine=lambda *args:None
  _,clean,_,_,_=art.scene(kind,sprites)
 finally:art.machine=machine
 raw=(ROOT/'assets/source/canonical'/f'{SLUGS[kind]}.background.scr').read_bytes()
 result=bytearray(raw)
 for y in range(200):
  for x in range(0,160,2):
   at=(y&7)*2048+(y>>3)*80+x//2
   assert raw[at]==art.pack(original[y*160+x],original[y*160+x+1]),(kind,x,y)
   result[at]=art.pack(clean[y*160+x],clean[y*160+x+1])
 return bytes(result)
