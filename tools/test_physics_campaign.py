#!/usr/bin/env python3
"""Stress production physics from every campaign spawn with deterministic input."""
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src/core"

HARNESS = r'''
#include <stdio.h>
#include <stdint.h>
#include "player.h"
#include "collision.h"
#include "state.h"
static const PlayerPlatform surfaces[] = {
@SURFACES@
};
static const uint16_t cpc_prefix_hashes[16] = {
   0xE453,0x2A06,0x3445,0xF301,0xE8E3,0xCECB,0xC4B1,0x0D97,
   0x747F,0xEDF1,0xCA5D,0x6C55,0x447E,0x64C4,0x5DEB,0xB0D5
};
typedef struct { uint8_t x,y; } Spawn;
static const Spawn spawns[] = {@SPAWNS@};
static uint16_t next_random(uint16_t *state) {
   *state = (uint16_t)(*state * 25173u + 13849u);
   return *state;
}
static int valid(const PlayerState *p) {
   uint8_t i, found=0;
   if(p->physics_error || p->xq<0 || p->xq>PLAYER_MAX_X*PLAYER_Q_ONE ||
      p->yq<PLAYER_MIN_Y*PLAYER_Q_ONE || p->yq>152*PLAYER_Q_ONE ||
      p->x!=(uint8_t)collision_floor_pixel(p->xq) ||
      p->y!=(uint8_t)collision_floor_pixel(p->yq)) return 0;
   if(!p->grounded) return p->support_id==255;
   for(i=0;i<sizeof(surfaces)/sizeof(surfaces[0]);i++)
      if(surfaces[i].id==p->support_id &&
         p->yq+PLAYER_BODY_BOTTOM*PLAYER_Q_ONE==(int32_t)surfaces[i].y*PLAYER_Q_ONE &&
         collision_overlaps_x(p->xq,&surfaces[i])) found=1;
   return found && p->vyq==0;
}
static int run(uint16_t seed, uint8_t level, uint16_t ticks, uint16_t *digest) {
   PlayerState p={0};
   uint16_t tick;
   uint16_t rng=seed;
   uint8_t bytes[PLAYER_STATE_SERIALIZED_SIZE], n;
   p.x=spawns[level].x; p.y=spawns[level].y;
   p.xq=(int16_t)(p.x*PLAYER_Q_ONE); p.yq=(int16_t)(p.y*PLAYER_Q_ONE);
   p.grounded=1; p.facing=1; p.support_id=0; p.ignore_surface_id=255;
   *digest=0xB271;
   for(tick=0;tick<ticks;tick++) {
      uint16_t r=next_random(&rng);
      PlayerInput in={(uint8_t)(r&1),(uint8_t)((r>>1)&1),
         (uint8_t)(((r>>5)&31)==0),(uint8_t)((r>>10)&1),
         (uint8_t)(((r>>11)&31)==0)};
      player_step(&p,in,surfaces,(uint8_t)(sizeof(surfaces)/sizeof(surfaces[0])));
      if(!valid(&p)) { fprintf(stderr,"FAIL level=%u seed=%04X tick=%u xq=%d yq=%d support=%u ground=%u error=%u\n",
         (unsigned)level,(unsigned)seed,(unsigned)tick,p.xq,p.yq,p.support_id,p.grounded,p.physics_error); return 0; }
      player_state_encode(bytes,&p);
      for(n=0;n<PLAYER_STATE_SERIALIZED_SIZE;n++)
         *digest=(uint16_t)((uint16_t)(*digest*257u)+(uint16_t)bytes[n]);
      if(seed==0xB2C2u && level==0 && ticks==256 && ((tick+1u)%16u)==0u &&
         *digest!=cpc_prefix_hashes[tick/16u]) {
         fprintf(stderr,"FAIL CPC trace checkpoint=%u expected=%04X got=%04X\n",
            (unsigned)(tick+1u),(unsigned)cpc_prefix_hashes[tick/16u],(unsigned)*digest);
         return 0;
      }
   }
   return 1;
}
int main(void) {
   uint8_t level,seed_index;
   uint16_t digest,first_digest=0,replay_digest;
   uint32_t count=0;
   for(level=0;level<sizeof(spawns)/sizeof(spawns[0]);level++)
      for(seed_index=0;seed_index<10;seed_index++) {
         uint16_t seed=(uint16_t)(0xB2C2u+(uint16_t)level*0x0101u+(uint16_t)seed_index*0x1010u);
         if(!run(seed,level,10000,&digest)) return 1;
         if(level==0 && seed_index==0) first_digest=digest;
         ++count;
      }
   if(!run(0xB2C2u,0,10000,&replay_digest) || replay_digest!=first_digest) {
      fprintf(stderr,"FAIL replay determinism expected=%04X got=%04X\n",first_digest,replay_digest); return 1;
   }
   if(!run(0xB2C2u,0,256,&replay_digest)) return 1;
   printf("PASS campaign physics: %u arenas x 10 seeds x 10000 ticks = %lu ticks; replay=%04X; CPC-prefix-256=%04X\n",
      (unsigned)(sizeof(spawns)/sizeof(spawns[0])),(unsigned long)count*10000UL,first_digest,replay_digest);
   return 0;
}
'''


def main():
    levels = sorted((ROOT / "assets/levels").glob("arena_*.json"))
    geometries = json.loads((ROOT / "assets/levels/geometries/opening_arena_v1.json").read_text())
    kinds = {"solid": "PLAYER_SURFACE_SOLID", "one_way": "PLAYER_SURFACE_ONE_WAY"}
    rows = [f"{{{s['x']},{s['y']},{s['width']},{s['height']},{kinds[s['kind']]},{i}}}"
            for i, s in enumerate(geometries["surfaces"])]
    spawns = []
    for path in levels:
        level = json.loads(path.read_text())
        if level["geometry_id"] != geometries["id"]:
            raise SystemExit(f"FAIL geometría no soportada por el runner: {path}")
        spawns.append(f"{{{level['spawn']['x']},{level['spawn']['y']}}}")
    source = HARNESS.replace("@SURFACES@", ",\n".join(rows)).replace("@SPAWNS@", ",".join(spawns))
    with tempfile.TemporaryDirectory(prefix="banterhouse2-campaign-physics-") as temp:
        c_file = Path(temp) / "campaign.c"
        binary = Path(temp) / "campaign"
        c_file.write_text(source)
        subprocess.run(["cc", "-std=c99", "-O2", "-Wall", "-Wextra", "-Werror",
                        "-I", str(CORE), str(c_file), str(CORE / "player.c"),
                        str(CORE / "collision.c"), str(CORE / "state.c"), "-o", str(binary)], check=True)
        result = subprocess.run([str(binary)], check=True, text=True, capture_output=True)
    print(result.stdout, end="")


if __name__ == "__main__":
    main()
