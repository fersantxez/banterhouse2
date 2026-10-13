#include "flow.h"

void flow_attempt_reset(ArenaFlow *flow) {
   flow->lives = FLOW_STARTING_LIVES;
   flow->invulnerability_ticks = 0;
   flow->dead = 0;
   flow->retry_armed = 0;
}

void flow_tick(ArenaFlow *flow) {
   if (flow->invulnerability_ticks) --flow->invulnerability_ticks;
}

uint8_t flow_hit(ArenaFlow *flow) {
   if (flow->dead || flow->invulnerability_ticks) return 0;
   if (flow->lives) --flow->lives;
   flow->invulnerability_ticks = FLOW_INVULNERABILITY_TICKS;
   if (!flow->lives) {
      flow->dead = 1;
      flow->retry_armed = 0;
      return 1;
   }
   return 0;
}

uint8_t flow_retry_input(ArenaFlow *flow, uint8_t pressed, uint8_t released,
                         uint8_t action_bit) {
   if (!flow->dead) return 0;
   if (released & action_bit) flow->retry_armed = 1;
   if ((pressed & action_bit) && flow->retry_armed) {
      flow->retry_armed = 0;
      return 1;
   }
   return 0;
}
