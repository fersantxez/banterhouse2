#ifndef BANTERHOUSE2_FLOW_H
#define BANTERHOUSE2_FLOW_H

#include <stdint.h>

#define FLOW_STARTING_LIVES 2
#define FLOW_INVULNERABILITY_TICKS 50

typedef struct {
   uint8_t lives;
   uint8_t invulnerability_ticks;
   uint8_t dead;
   uint8_t retry_armed;
} ArenaFlow;

/* Start a clean attempt at its saved checkpoint. */
void flow_attempt_reset(ArenaFlow *flow);
/* Expire timers before resolving contacts in the current simulation tick. */
void flow_tick(ArenaFlow *flow);
/* Returns nonzero only when this valid hit causes the final death. */
uint8_t flow_hit(ArenaFlow *flow);
/* A dead player must release and then press action to request a retry. */
uint8_t flow_retry_input(ArenaFlow *flow, uint8_t pressed, uint8_t released,
                         uint8_t action_bit);

#endif
