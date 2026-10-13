#ifndef BANterHOUSE2_PLAYER_H
#define BANterHOUSE2_PLAYER_H

#include <stdint.h>
#include "tuning.h"

enum { PLAYER_SURFACE_SOLID = 0, PLAYER_SURFACE_ONE_WAY = 1 };

typedef struct {
   uint8_t x, y, w, h, kind, id;
} PlayerPlatform;

typedef PlayerPlatform PlayerSurface;

typedef struct {
   int16_t xq, yq, vxq, vyq;
   uint8_t x, y, facing, grounded;
   uint8_t jump_buffer, coyote, jump_min_ticks;
   uint8_t support_id;
   uint8_t ignore_surface_id, drop_ticks;
   uint8_t physics_error;
} PlayerState;

typedef struct {
   uint8_t left, right, jump_pressed, jump_held, down;
} PlayerInput;

/* Returns one when the tick requested the jump sound effect. */
uint8_t player_step(PlayerState *state, PlayerInput input,
                    const PlayerPlatform *platforms, uint8_t platform_count);

#endif
