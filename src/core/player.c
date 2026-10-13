#include "collision.h"

static int32_t approach_zero(int32_t value, int32_t step) {
   if (value > step) return value - step;
   if (value < -step) return value + step;
   return 0;
}

static int32_t approach_target(int32_t value, int32_t target, int32_t step) {
   if (value < target) {
      value += step;
      return value > target ? target : value;
   }
   if (value > target) {
      value -= step;
      return value < target ? target : value;
   }
   return value;
}

uint8_t player_step(PlayerState *s, PlayerInput in,
                    const PlayerPlatform *surfaces, uint8_t surface_count) {
   uint8_t i, jump_event = 0, lost_support = 0;
   int32_t old_xq, old_yq, proposed_xq, proposed_yq;
   const PlayerPlatform *support;

   s->physics_error = 0;
   if (s->grounded) {
      support = collision_surface_by_id(surfaces, surface_count, s->support_id);
      if (!support || s->yq + PLAYER_BODY_BOTTOM * PLAYER_Q_ONE !=
                       (int32_t)support->y * PLAYER_Q_ONE ||
          !collision_overlaps_x(s->xq, support)) {
         s->grounded = 0;
         s->support_id = 255;
         s->coyote = PLAYER_COYOTE_TICKS;
         lost_support = 1;
      }
   }

   if (in.jump_pressed) s->jump_buffer = PLAYER_JUMP_BUFFER_TICKS;
   else if (s->jump_buffer) --s->jump_buffer;
   if (s->grounded) s->coyote = PLAYER_COYOTE_TICKS;

   /* Jump has priority over dropping through a one-way platform. */
   if (s->jump_buffer && s->coyote) {
      s->vyq = PLAYER_JUMP_SPEED;
      s->grounded = 0;
      s->support_id = 255;
      s->ignore_surface_id = 255;
      s->drop_ticks = 0;
      s->jump_min_ticks = PLAYER_MIN_JUMP_TICKS;
      s->coyote = s->jump_buffer = 0;
      jump_event = 1;
   }

   if (!jump_event && in.down && s->grounded) {
      support = collision_surface_by_id(surfaces, surface_count, s->support_id);
      if (support && support->kind == PLAYER_SURFACE_ONE_WAY) {
         s->grounded = 0;
         s->ignore_surface_id = support->id;
         s->support_id = 255;
         s->coyote = 0;
         s->drop_ticks = 0;
      }
   }

   if (in.left && !in.right) {
      s->facing = 0;
      s->vxq = (int16_t)approach_target(s->vxq, -PLAYER_MAX_SPEED_X,
                                        PLAYER_ACCEL_X);
   } else if (in.right && !in.left) {
      s->facing = 1;
      s->vxq = (int16_t)approach_target(s->vxq, PLAYER_MAX_SPEED_X,
                                        PLAYER_ACCEL_X);
   } else {
      s->vxq = (int16_t)approach_zero(s->vxq, PLAYER_ACCEL_X);
   }

   old_xq = s->xq;
   proposed_xq = old_xq + s->vxq;
   collision_resolve_x(s, old_xq, proposed_xq, surfaces, surface_count);

   if (s->grounded) {
      support = collision_surface_by_id(surfaces, surface_count, s->support_id);
      if (!support || s->yq + PLAYER_BODY_BOTTOM * PLAYER_Q_ONE !=
                       (int32_t)support->y * PLAYER_Q_ONE ||
          !collision_overlaps_x(s->xq, support)) {
         s->grounded = 0;
         s->support_id = 255;
         s->coyote = PLAYER_COYOTE_TICKS;
         lost_support = 1;
      }
   }

   if (!s->grounded) {
      if (s->jump_min_ticks) --s->jump_min_ticks;
      else if (!in.jump_held && s->vyq < PLAYER_JUMP_CUT)
         s->vyq = PLAYER_JUMP_CUT;
      old_yq = s->yq;
      proposed_yq = old_yq + s->vyq;
      if (proposed_yq < PLAYER_MIN_Y * PLAYER_Q_ONE) {
         proposed_yq = PLAYER_MIN_Y * PLAYER_Q_ONE;
         s->vyq = 0;
      }
      collision_resolve_y(s, old_yq, proposed_yq, surfaces, surface_count);
      if (!s->grounded && s->vyq < PLAYER_MAX_FALL) {
         int32_t next = (int32_t)s->vyq + PLAYER_GRAVITY;
         s->vyq = (int16_t)(next > PLAYER_MAX_FALL ? PLAYER_MAX_FALL : next);
      }
      if (s->ignore_surface_id != 255) {
         support = collision_surface_by_id(surfaces, surface_count,
                                           s->ignore_surface_id);
         if (!support || s->yq + PLAYER_BODY_TOP * PLAYER_Q_ONE >=
                          ((int32_t)support->y + support->h) * PLAYER_Q_ONE) {
            s->ignore_surface_id = 255;
            s->drop_ticks = 0;
         } else if (++s->drop_ticks > PLAYER_DROP_TIMEOUT_TICKS) {
            s->physics_error = 1;
         }
      }
   }

   if (!s->grounded && !lost_support && !jump_event && s->coyote)
      --s->coyote;
   s->x = (uint8_t)collision_floor_pixel(s->xq);
   s->y = (uint8_t)collision_floor_pixel(s->yq);
   for (i = 0; i < surface_count; ++i)
      if (surfaces[i].kind > PLAYER_SURFACE_ONE_WAY) s->physics_error = 1;
   return jump_event;
}
