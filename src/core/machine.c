#include "machine.h"

void machine_init(Machine *m, uint8_t x, uint8_t ground,
                  uint8_t direction, uint8_t initial_wait,
                  uint8_t warning_ticks, uint8_t period) {
   m->x = x;
   m->w = 14;
   m->ground = ground;
   m->y = (uint8_t)(ground - 17);
   m->dir = direction;
   m->live = 1;
   m->wait = initial_wait;
   m->state = MACHINE_IDLE;
   m->warning_ticks = warning_ticks;
   m->period = period;
   m->reserved_slot = PROJECTILE_NO_SLOT;
}

MachineEvent machine_tick(Machine *m, Projectile pool[PROJECTILE_POOL_SIZE]) {
   uint8_t slot;
   if (!m->live || m->state == MACHINE_OFF) return MACHINE_EVENT_NONE;
   if (m->state == MACHINE_IDLE) {
      if (m->wait) {
         --m->wait;
         return MACHINE_EVENT_NONE;
      }
      slot = projectile_reserve(pool);
      if (slot == PROJECTILE_NO_SLOT) return MACHINE_EVENT_NONE;
      m->reserved_slot = slot;
      if (!m->warning_ticks) {
         projectile_fire(pool, m->reserved_slot,
            (int16_t)((m->x + (m->dir ? 14 : 0)) * 2),
            (uint8_t)(m->ground - 12), m->dir);
         pool[m->reserved_slot].born = 0;
         m->reserved_slot = PROJECTILE_NO_SLOT;
         m->state = MACHINE_IDLE;
         m->wait = m->period;
         return MACHINE_EVENT_FIRED;
      }
      m->state = MACHINE_WARNING;
      m->wait = 0;
      return MACHINE_EVENT_WARNING;
   }
   if (m->state == MACHINE_WARNING) {
      if (m->wait < m->warning_ticks) {
         ++m->wait;
         if (m->wait < m->warning_ticks) return MACHINE_EVENT_NONE;
      }
      m->state = MACHINE_FIRE;
      return MACHINE_EVENT_NONE;
   }
   if (m->state == MACHINE_FIRE) {
      projectile_fire(pool, m->reserved_slot,
         (int16_t)((m->x + (m->dir ? 14 : 0)) * 2),
         (uint8_t)(m->ground - 12), m->dir);
      m->reserved_slot = PROJECTILE_NO_SLOT;
      m->state = MACHINE_IDLE;
      m->wait = m->period;
      return MACHINE_EVENT_FIRED;
   }
   return MACHINE_EVENT_NONE;
}

void machine_turn_off(Machine *m, Projectile pool[PROJECTILE_POOL_SIZE]) {
   if (m->reserved_slot != PROJECTILE_NO_SLOT)
      projectile_release(pool, m->reserved_slot);
   m->reserved_slot = PROJECTILE_NO_SLOT;
   m->state = MACHINE_OFF;
   m->live = 0;
   m->wait = 0;
}

void machine_pool_reset(Machine machines[MACHINE_POOL_SIZE],
                        Projectile pool[PROJECTILE_POOL_SIZE]) {
   uint8_t i;
   projectile_pool_reset(pool);
   for (i = 0; i < MACHINE_POOL_SIZE; ++i) {
      machines[i].x = machines[i].y = machines[i].w = 0;
      machines[i].ground = machines[i].dir = machines[i].live = 0;
      machines[i].wait = machines[i].warning_ticks = machines[i].period = 0;
      machines[i].state = MACHINE_OFF;
      machines[i].reserved_slot = PROJECTILE_NO_SLOT;
   }
}
