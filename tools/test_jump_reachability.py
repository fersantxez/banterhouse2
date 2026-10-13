#!/usr/bin/env python3
"""Search reproducible host trajectories through the production player_step."""
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys_path = ROOT / "src/core"

HARNESS = r'''
#include <stdio.h>
#include <stdint.h>
#include "player.h"
static const PlayerPlatform surfaces[] = {
@SURFACES@
};
static int reachable(uint8_t from, uint8_t to) {
   uint8_t xi, hold, move, dir, tick;
   const PlayerPlatform *src=0, *dst=0;
   for(xi=0;xi<6;xi++) {
      if(surfaces[xi].id==from) src=&surfaces[xi];
      if(surfaces[xi].id==to) dst=&surfaces[xi];
   }
   if(!src || !dst) return 0;
   for(int16_t x=(int16_t)src->x-10; x<(int16_t)src->x+src->w-2; x+=4) {
      if(x<0 || x>144) continue;
      for(dir=0;dir<2;dir++) for(hold=7;hold<=21;hold+=7)
         for(move=0;move<=32;move+=4) {
            PlayerState s={0};
            s.xq=(int16_t)(x*PLAYER_Q_ONE);
            s.yq=(int16_t)(((int16_t)src->y-32)*PLAYER_Q_ONE);
            s.x=(uint8_t)x; s.y=(uint8_t)(src->y-32);
            s.facing=1; s.grounded=1; s.support_id=from;
            s.ignore_surface_id=255;
            for(tick=0;tick<55;tick++) {
               PlayerInput in={0,0,0,0,0};
               if(tick==0) in.jump_pressed=1;
               if(tick<hold) in.jump_held=1;
               if(tick<move) { if(dir) in.right=1; else in.left=1; }
               player_step(&s,in,surfaces,6);
               if(s.physics_error) break;
               if(tick>0 && s.grounded) {
                  if(s.support_id==to) return 1;
                  break;
               }
            }
         }
   }
   return 0;
}
int main(void) {
   uint8_t from,to;
   for(from=0;from<6;from++) for(to=0;to<6;to++)
      if(from!=to && reachable(from,to)) printf("%u %u\n",from,to);
   return 0;
}
'''


def main():
    geometry = json.loads((ROOT / "assets/levels/geometries/opening_arena_v1.json").read_text())
    kinds = {"solid": "PLAYER_SURFACE_SOLID", "one_way": "PLAYER_SURFACE_ONE_WAY"}
    rows = [f"{{{s['x']},{s['y']},{s['width']},{s['height']},{kinds[s['kind']]},{i}}}"
            for i, s in enumerate(geometry["surfaces"])]
    source = HARNESS.replace("@SURFACES@", ",\n".join(rows))
    with tempfile.TemporaryDirectory(prefix="banterhouse2-jumps-") as temp:
        c_file = Path(temp) / "reach.c"
        binary = Path(temp) / "reach"
        c_file.write_text(source)
        subprocess.run(["cc", "-std=c99", "-O2", "-Wall", "-Wextra", "-Werror",
                        "-I", str(sys_path), str(c_file),
                        str(sys_path / "player.c"), str(sys_path / "collision.c"),
                        "-o", str(binary)], check=True)
        output = subprocess.run([str(binary)], check=True, text=True,
                                capture_output=True).stdout
    edges = {tuple(map(int, line.split())) for line in output.splitlines() if line.strip()}
    graph = {i: {j for a, j in edges if a == i} for i in range(6)}
    reachable_ids = {0}
    frontier = [0]
    while frontier:
        current = frontier.pop()
        for nxt in graph[current] - reachable_ids:
            reachable_ids.add(nxt)
            frontier.append(nxt)
    if reachable_ids != set(range(6)):
        raise SystemExit(f"FAIL apoyos no alcanzables desde el suelo: {sorted(set(range(6))-reachable_ids)}; rutas={graph}")

    # Audit the entire 16x32 canonical sprite at every integer resting position
    # that still has positive overlap between the contracted body and its support.
    embeds = []
    for lower in geometry["surfaces"]:
        player_y = lower["y"] - 32
        for upper in geometry["surfaces"]:
            if upper["y"] >= lower["y"]:
                continue
            vertical_overlap = max(player_y, upper["y"]) < min(
                lower["y"], upper["y"] + upper["height"])
            if not vertical_overlap:
                continue
            for player_x in range(145):
                body_on_support = (player_x + 13 > lower["x"] and
                                   player_x + 3 < lower["x"] + lower["width"])
                sprite_hits_upper = (player_x < upper["x"] + upper["width"] and
                                     player_x + 16 > upper["x"])
                if body_on_support and sprite_hits_upper:
                    embeds.append((lower["id"], upper["id"], player_x))
    if embeds:
        raise SystemExit(f"FAIL sprite de reposo atraviesa otra plataforma: {embeds}")

    supports = {s["y"]: i for i, s in enumerate(geometry["surfaces"])}
    for level_path in sorted((ROOT / "assets/levels").glob("arena_*.json")):
        level = json.loads(level_path.read_text())
        for machine in level["machines"]:
            sid = supports[machine["ground_y"]]
            if sid not in reachable_ids:
                raise SystemExit(f"FAIL objetivo inaccesible: {level['id']} máquina {machine} apoyo {sid}")
    print(f"PASS rutas simuladas con player_step: apoyos alcanzables {sorted(reachable_ids)}; "
          f"{sum(len(v) for v in graph.values())} aristas de salto verificadas; "
          "sin sprite atravesado en reposo; máquinas de 24 arenas sobre apoyos alcanzables")


if __name__ == "__main__":
    main()
