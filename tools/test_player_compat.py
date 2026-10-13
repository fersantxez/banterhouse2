#!/usr/bin/env python3
"""Differentially run the extracted player step against the frozen pre-fix C."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'research/runs/20261012T214508Z-F00-physics-repair/source-main.c'
FROZEN = ROOT / 'research/runs/20261012T220000Z-F01-F02-physics-repair/frozen-src/core'
CORE = FROZEN / 'player.c'
HEADER = FROZEN / 'player.h'


def extract_function(source):
    match = re.search(r'static void update_player\([^)]*\)\s*\{', source)
    if not match:
        raise SystemExit('FAIL: no se encuentra update_player en la fuente base congelada')
    start = match.start()
    brace = source.index('{', match.start())
    depth = 0
    for pos in range(brace, len(source)):
        if source[pos] == '{':
            depth += 1
        elif source[pos] == '}':
            depth -= 1
            if depth == 0:
                body = source[start:pos + 1]
                return body.replace('static void update_player(', 'static void reference_update_player(', 1)
    raise SystemExit('FAIL: cuerpo de update_player sin cerrar')


PRELUDE = r'''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "player.h"
typedef uint8_t u8;
typedef int16_t i16;
#define FACING_LEFT 0
#define FACING_RIGHT 1
#define FLOOR_Y 184
typedef PlayerPlatform Platform;
static Platform ledges[6] = {{0,184,160},{0,184,160},{0,184,160},{0,184,160},{0,184,160},{0,184,160}};
static u8 player_x, player_y, facing, grounded, jump_buffer, coyote, jump_min_ticks;
static i16 player_xq, player_yq, vxq, vyq;
static u8 sound_ticks, jump_sounds;
static void sfx_jump(void) { ++jump_sounds; }
static u8 overlap(u8 a, u8 aw, u8 b, u8 bw) { return a < b + bw && b < a + aw; }
'''


HARNESS = r'''
static void reference_tick(PlayerState *s, PlayerInput in) {
   player_x=s->x; player_y=s->y; facing=s->facing; grounded=s->grounded;
   jump_buffer=s->jump_buffer; coyote=s->coyote; jump_min_ticks=s->jump_min_ticks;
   player_xq=s->xq; player_yq=s->yq; vxq=s->vxq; vyq=s->vyq;
   reference_update_player(in.left,in.right,in.jump_pressed,in.jump_held,in.down);
   s->x=player_x; s->y=player_y; s->facing=facing; s->grounded=grounded;
   s->jump_buffer=jump_buffer; s->coyote=coyote; s->jump_min_ticks=jump_min_ticks;
   s->xq=player_xq; s->yq=player_yq; s->vxq=vxq; s->vyq=vyq;
   if (!s->grounded) s->support_id=255;
   else {
      unsigned i;
      for(i=0;i<6;i++) if((uint16_t)s->y+32==ledges[i].y &&
         s->x<ledges[i].x+ledges[i].w && ledges[i].x<s->x+16) { s->support_id=i; break; }
   }
}
static int same(PlayerState a, PlayerState b) {
   return a.xq==b.xq && a.yq==b.yq && a.vxq==b.vxq && a.vyq==b.vyq &&
      a.x==b.x && a.y==b.y && a.facing==b.facing && a.grounded==b.grounded &&
      a.jump_buffer==b.jump_buffer && a.coyote==b.coyote &&
      a.jump_min_ticks==b.jump_min_ticks && a.support_id==b.support_id;
}
int main(void) {
   PlayerState old={48,304,0,0,24,152,1,1,0,0,0,0}, current=old;
   uint32_t rng=0x6d2b79f5u; unsigned i;
   for(i=0;i<5000;i++) {
      PlayerInput in;
      uint8_t old_sounds=jump_sounds;
      rng^=rng<<13; rng^=rng>>17; rng^=rng<<5;
      in.left=(rng>>0)&1; in.right=(rng>>1)&1;
      in.jump_pressed=((rng>>2)%19)==0; in.jump_held=(rng>>3)&1;
      in.down=((rng>>4)%7)==0;
      reference_tick(&old,in);
      { uint8_t event=player_step(&current,in,ledges,6);
        if(event != (jump_sounds != old_sounds)) {
           fprintf(stderr,"FAIL evento tick=%u\n",i); return 2;
        }
      }
      if(!same(old,current)) {
         fprintf(stderr,"FAIL equivalencia tick=%u old=(%d,%d,%d,%d,%u) new=(%d,%d,%d,%d,%u)\n",
            i,old.xq,old.yq,old.vxq,old.vyq,old.grounded,
            current.xq,current.yq,current.vxq,current.vyq,current.grounded);
         return 3;
      }
   }
   ledges[0]=(Platform){0,184,160}; ledges[1]=(Platform){42,160,28};
   ledges[2]=(Platform){80,136,28}; ledges[3]=(Platform){120,112,34};
   ledges[4]=(Platform){76,88,26}; ledges[5]=(Platform){20,64,40};
   old=(PlayerState){138,256,0,0,69,128,1,1,0,0,0,1}; current=old;
   { PlayerInput in={0,1,0,0,0};
     reference_tick(&old,in); player_step(&current,in,ledges,6);
     reference_tick(&old,in); player_step(&current,in,ledges,6);
   }
   if(old.grounded!=1 || old.yq!=256 || old.vyq!=0 || old.xq<=140) return 4;
   if(current.grounded!=0 || current.yq!=256 || current.vyq!=1 ||
      current.support_id!=255 || current.xq!=141) {
      fprintf(stderr,"FAIL el borde no inicia la caída en el tick de pérdida de apoyo\n"); return 5;
   }
   old=(PlayerState){54,256,0,0,27,128,0,1,0,0,0,1}; current=old;
   { PlayerInput in={1,0,0,0,0};
     reference_tick(&old,in); player_step(&current,in,ledges,6);
   }
   if(old.grounded!=1 || current.grounded!=0 || current.support_id!=255 ||
      current.xq!=53 || current.vyq!=1) {
      fprintf(stderr,"FAIL el borde izquierdo no inicia la caída\n"); return 6;
   }
   printf("PASS compatibilidad de 5000 ticks; al borde: referencia flota y juego cae (xq=%d yq=%d grounded=%u vyq=%d)\n",
      current.xq,current.yq,current.grounded,current.vyq);
   return 0;
}
'''


def main():
    source = BASELINE.read_text()
    frozen_hash = hashlib.sha256(source.encode()).hexdigest()
    baseline = json.loads((BASELINE.parent / 'baseline.json').read_text())
    record = next(x for x in baseline['artifacts'] if x['path'].endswith('source-main.c'))
    if frozen_hash != record['sha256']:
        raise SystemExit('FAIL: hash de fuente base no coincide con F00')
    code = PRELUDE + extract_function(source) + HARNESS
    with tempfile.TemporaryDirectory(prefix='banterhouse2-physics-') as tmp:
        harness = Path(tmp) / 'compat.c'
        binary = Path(tmp) / 'compat'
        harness.write_text(code)
        subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',
                        '-I',str(HEADER.parent),str(harness),str(CORE),'-o',str(binary)],
                       check=True)
        result = subprocess.run([str(binary)],check=True,text=True,capture_output=True)
        print(result.stdout,end='')
        print('PASS fuente base SHA-256 '+frozen_hash)


if __name__ == '__main__':
    main()
