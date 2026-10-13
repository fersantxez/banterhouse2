#ifndef BANTERHOUSE2_PROJECTILE_H
#define BANTERHOUSE2_PROJECTILE_H

#include <stdint.h>

#define PROJECTILE_POOL_SIZE 4
#define PROJECTILE_NO_SLOT 255u

typedef enum {
   PROJECTILE_FREE = 0,
   PROJECTILE_RESERVED,
   PROJECTILE_HOSTILE,
   PROJECTILE_RETURNED
} ProjectileState;

typedef struct {
   int16_t xq, prev_xq;
   uint8_t y, dir, live, returned;
   uint8_t state, born, bounced, scored_mask;
} Projectile;

void projectile_pool_reset(Projectile pool[PROJECTILE_POOL_SIZE]);
uint8_t projectile_reserve(Projectile pool[PROJECTILE_POOL_SIZE]);
void projectile_release(Projectile pool[PROJECTILE_POOL_SIZE], uint8_t slot);
void projectile_fire(Projectile pool[PROJECTILE_POOL_SIZE], uint8_t slot,
                     int16_t xq, uint8_t y, uint8_t dir);
void projectile_mark_returned(Projectile *projectile, uint8_t dir);
void projectile_tick(Projectile *projectile, int8_t hostile_speed,
                    int8_t returned_speed);

#endif
