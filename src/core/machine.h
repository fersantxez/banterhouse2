#ifndef BANTERHOUSE2_MACHINE_H
#define BANTERHOUSE2_MACHINE_H

#include <stdint.h>
#include "projectile.h"

#define MACHINE_POOL_SIZE 3

typedef enum {
   MACHINE_IDLE = 0,
   MACHINE_WARNING,
   MACHINE_FIRE,
   MACHINE_OFF
} MachineState;

typedef enum {
   MACHINE_EVENT_NONE = 0,
   MACHINE_EVENT_WARNING,
   MACHINE_EVENT_FIRED
} MachineEvent;

typedef struct {
   uint8_t x, y, w, ground, dir, live, wait;
   uint8_t state, warning_ticks, period, reserved_slot;
} Machine;

void machine_init(Machine *machine, uint8_t x, uint8_t ground,
                  uint8_t direction, uint8_t initial_wait,
                  uint8_t warning_ticks, uint8_t period);
MachineEvent machine_tick(Machine *machine,
                          Projectile pool[PROJECTILE_POOL_SIZE]);
void machine_turn_off(Machine *machine,
                      Projectile pool[PROJECTILE_POOL_SIZE]);
void machine_pool_reset(Machine machines[MACHINE_POOL_SIZE],
                        Projectile pool[PROJECTILE_POOL_SIZE]);

#endif
