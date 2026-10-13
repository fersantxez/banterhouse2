#include <stdio.h>
#include <string.h>
#include "core/player.h"
#include "core/collision.h"
#include "generated/m0_level.h"

int main(void) {
   PlayerState p;
   PlayerInput none = {0,0,0,0,0};
   PlayerInput right = {0,1,0,0,0};
   uint8_t i, saw_floor=0, saw_one_way=0;
   memset(&p,0,sizeof(p));
   p.x=M0_SPAWN_X; p.y=M0_SPAWN_Y;
   p.xq=(int16_t)(M0_SPAWN_X*PLAYER_Q_ONE);
   p.yq=(int16_t)(M0_SPAWN_Y*PLAYER_Q_ONE);
   p.grounded=1; p.facing=1; p.support_id=0; p.ignore_surface_id=255;
   if (M0_SURFACE_COUNT != 6 || p.yq + PLAYER_BODY_BOTTOM*PLAYER_Q_ONE !=
       (int32_t)m0_surfaces[0].y*PLAYER_Q_ONE) return 1;
   for (i=0;i<M0_SURFACE_COUNT;i++) {
      if (m0_surfaces[i].kind==PLAYER_SURFACE_SOLID) saw_floor++;
      if (m0_surfaces[i].kind==PLAYER_SURFACE_ONE_WAY) saw_one_way++;
   }
   if (saw_floor!=1 || saw_one_way!=5) return 2;
   /* Use production simulation: stepping off the one-way edge clears support
    * and begins gravity; the declared floor remains a valid landing. */
   p.x=62; p.xq=(int16_t)(62*PLAYER_Q_ONE); p.y=118;
   p.yq=(int16_t)(118*PLAYER_Q_ONE); p.support_id=1; p.grounded=1;
   player_step(&p,right,m0_surfaces,M0_SURFACE_COUNT);
   player_step(&p,right,m0_surfaces,M0_SURFACE_COUNT);
   if (p.grounded || p.support_id!=255 || p.vyq!=PLAYER_GRAVITY) return 3;
   for (i=0;i<80 && !p.grounded;i++) player_step(&p,none,m0_surfaces,M0_SURFACE_COUNT);
   if (!p.grounded || p.support_id!=0 || p.yq!=152*PLAYER_Q_ONE || p.physics_error) return 4;
   puts("PASS: M0 five-mark route table drives shared physics; edge fall and declared-floor landing");
   return 0;
}
