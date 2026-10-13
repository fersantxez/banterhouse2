#include "projectile.h"

void projectile_pool_reset(Projectile pool[PROJECTILE_POOL_SIZE]) {
   uint8_t i;
   for (i = 0; i < PROJECTILE_POOL_SIZE; ++i) {
      pool[i].xq = 0;
      pool[i].prev_xq = 0;
      pool[i].y = pool[i].dir = pool[i].live = pool[i].returned = 0;
      pool[i].state = PROJECTILE_FREE;
      pool[i].born = pool[i].bounced = pool[i].scored_mask = 0;
   }
}

uint8_t projectile_reserve(Projectile pool[PROJECTILE_POOL_SIZE]) {
   uint8_t i;
   for (i = 0; i < PROJECTILE_POOL_SIZE; ++i) {
      if (pool[i].state == PROJECTILE_FREE) {
         pool[i].state = PROJECTILE_RESERVED;
         pool[i].live = pool[i].returned = pool[i].born = 0;
         pool[i].bounced = pool[i].scored_mask = 0;
         return i;
      }
   }
   return PROJECTILE_NO_SLOT;
}

void projectile_release(Projectile pool[PROJECTILE_POOL_SIZE], uint8_t slot) {
   if (slot < PROJECTILE_POOL_SIZE) {
      pool[slot].state = PROJECTILE_FREE;
      pool[slot].live = pool[slot].returned = pool[slot].born = 0;
   }
}

void projectile_fire(Projectile pool[PROJECTILE_POOL_SIZE], uint8_t slot,
                     int16_t xq, uint8_t y, uint8_t dir) {
   Projectile *p;
   if (slot >= PROJECTILE_POOL_SIZE || pool[slot].state != PROJECTILE_RESERVED)
      return;
   p = &pool[slot];
   p->xq = xq;
   p->prev_xq = xq;
   p->y = y;
   p->dir = dir;
   p->live = 1;
   p->returned = 0;
   p->state = PROJECTILE_HOSTILE;
   p->born = 1;
   p->bounced = p->scored_mask = 0;
}

void projectile_mark_returned(Projectile *p, uint8_t dir) {
   p->state = PROJECTILE_RETURNED;
   p->prev_xq = p->xq;
   p->returned = 1;
   p->dir = dir;
   /* T12 will consume the remaining swept segment on the turn tick. */
   p->born = 0;
}

void projectile_tick(Projectile *p, int8_t hostile_speed, int8_t returned_speed) {
   int8_t speed;
   if (p->state != PROJECTILE_HOSTILE && p->state != PROJECTILE_RETURNED) return;
   p->prev_xq = p->xq;
   if (p->born) {
      p->born = 0;
      return;
   }
   speed = p->state == PROJECTILE_RETURNED ? returned_speed : hostile_speed;
   p->xq += p->dir ? speed : (int8_t)-speed;
}
