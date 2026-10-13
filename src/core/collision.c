#include "collision.h"

typedef struct { int16_t n, d; } CollisionFraction;

static void multiply_u16(uint16_t a, uint16_t b,
                         uint16_t *product_hi, uint16_t *product_lo) {
   uint8_t i;
   uint16_t add_hi = 0, add_lo = a, old_lo;
   uint16_t hi = 0, lo = 0;
   for (i = 0; i < 16; ++i) {
      if (b & 1u) {
         old_lo = lo;
         lo = (uint16_t)(lo + add_lo);
         hi = (uint16_t)(hi + add_hi + (lo < old_lo));
      }
      b >>= 1;
      add_hi = (uint16_t)((add_hi << 1) | (add_lo >> 15));
      add_lo <<= 1;
   }
   *product_hi = hi;
   *product_lo = lo;
}

static uint8_t product_less(uint16_t a_hi, uint16_t a_lo,
                            uint16_t b_hi, uint16_t b_lo) {
   return a_hi < b_hi || (a_hi == b_hi && a_lo < b_lo);
}

static uint8_t fraction_less(int16_t an_signed, int16_t ad,
                             int16_t bn_signed, int16_t bd) {
   uint8_t a_negative = an_signed < 0, b_negative = bn_signed < 0;
   uint16_t an = a_negative ? (uint16_t)-an_signed : (uint16_t)an_signed;
   uint16_t bn = b_negative ? (uint16_t)-bn_signed : (uint16_t)bn_signed;
   uint16_t left_hi, left_lo, right_hi, right_lo;
   if (a_negative != b_negative) return a_negative;
   multiply_u16(an, (uint16_t)bd, &left_hi, &left_lo);
   multiply_u16(bn, (uint16_t)ad, &right_hi, &right_lo);
   return a_negative ? product_less(right_hi, right_lo, left_hi, left_lo) :
                       product_less(left_hi, left_lo, right_hi, right_lo);
}

static uint8_t sweep_axis(int16_t a0, int16_t a1, int16_t as,
                          int16_t b0, int16_t b1, int16_t bs,
                          CollisionFraction *enter, CollisionFraction *exit) {
   int16_t rel0 = a0 - b0;
   int16_t velocity = (a1 - a0) - (b1 - b0);
   int16_t low = -as;
   int16_t high = bs;
   CollisionFraction first, last;
   if (!velocity) return rel0 < low || rel0 > high ? 0 : 1;
   if (velocity > 0) {
      first.n = (int16_t)(low - rel0);
      first.d = (int16_t)velocity;
      last.n = (int16_t)(high - rel0);
      last.d = (int16_t)velocity;
   } else {
      first.n = (int16_t)(rel0 - high);
      first.d = (int16_t)-velocity;
      last.n = (int16_t)(rel0 - low);
      last.d = (int16_t)-velocity;
   }
   if (fraction_less(enter->n, enter->d, first.n, first.d)) {
      enter->n = first.n;
      enter->d = first.d;
   }
   if (fraction_less(last.n, last.d, exit->n, exit->d)) {
      exit->n = last.n;
      exit->d = last.d;
   }
   return !fraction_less(exit->n, exit->d, enter->n, enter->d);
}

uint8_t collision_sweep_aabb(int16_t ax0, int16_t ay0,
                              int16_t ax1, int16_t ay1,
                              int16_t aw, int16_t ah,
                              int16_t bx0, int16_t by0,
                              int16_t bx1, int16_t by1,
                              int16_t bw, int16_t bh,
                              uint16_t *time_q16) {
   CollisionFraction enter, exit, zero, one;
   uint8_t hit;
   uint16_t scaled, numerator, denominator;
   zero.n = 0; zero.d = 1;
   one.n = 1; one.d = 1;
   enter.n = zero.n; enter.d = zero.d;
   exit.n = one.n; exit.d = one.d;
   hit = sweep_axis(ax0, ax1, aw, bx0, bx1, bw, &enter, &exit);
   if (hit) hit = sweep_axis(ay0, ay1, ah, by0, by1, bh, &enter, &exit);
   if (!hit || fraction_less(exit.n, exit.d, zero.n, zero.d) ||
       fraction_less(one.n, one.d, enter.n, enter.d)) return 0;
   if (fraction_less(enter.n, enter.d, zero.n, zero.d)) {
      enter.n = zero.n;
      enter.d = zero.d;
   }
   numerator = (uint16_t)enter.n;
   denominator = (uint16_t)enter.d;
   scaled = 0;
   {
      uint8_t bit;
      for (bit = 0; bit < 16; ++bit) {
         scaled <<= 1;
         if (numerator >= (uint16_t)(denominator - numerator)) {
            numerator = (uint16_t)(numerator - (denominator - numerator));
            scaled |= 1;
         } else numerator <<= 1;
      }
   }
   *time_q16 = scaled;
   return 1;
}

int16_t collision_interpolate_q16(int16_t a, int16_t b, uint16_t t_q16) {
   int16_t delta = (int16_t)(b - a);
   uint16_t magnitude = delta < 0 ? (uint16_t)-delta : (uint16_t)delta;
   uint16_t product_hi, product_lo;
   int16_t part;
   multiply_u16(magnitude, t_q16, &product_hi, &product_lo);
   (void)product_lo;
   part = (int16_t)product_hi;
   return (int16_t)(delta < 0 ? a - part : a + part);
}

#define Q_ONE PLAYER_Q_ONE

int32_t collision_floor_pixel(int32_t q) {
   if (q >= 0) return q / Q_ONE;
   return -((-q + Q_ONE - 1) / Q_ONE);
}

uint8_t collision_overlaps_x(int32_t xq, const PlayerPlatform *surface) {
   int32_t left = (int32_t)surface->x * Q_ONE;
   int32_t right = left + (int32_t)surface->w * Q_ONE;
   return xq + PLAYER_BODY_RIGHT * Q_ONE > left &&
          xq + PLAYER_BODY_LEFT * Q_ONE < right;
}

static uint8_t overlaps_y(int32_t yq, const PlayerPlatform *surface) {
   int32_t top = (int32_t)surface->y * Q_ONE;
   int32_t bottom = top + (int32_t)surface->h * Q_ONE;
   return yq + PLAYER_BODY_BOTTOM * Q_ONE > top &&
          yq + PLAYER_BODY_TOP * Q_ONE < bottom;
}

const PlayerPlatform *collision_surface_by_id(const PlayerPlatform *surfaces,
                                               uint8_t count, uint8_t id) {
   uint8_t i;
   for (i = 0; i < count; ++i)
      if (surfaces[i].id == id) return &surfaces[i];
   return 0;
}

uint8_t collision_resolve_x(PlayerState *s, int32_t old_xq,
                             int32_t proposed_xq,
                             const PlayerPlatform *surfaces, uint8_t count) {
   uint8_t i, collided = 0;
   int32_t best = proposed_xq;
   if (proposed_xq > old_xq) {
      int32_t first_left = 0x7fffffffL;
      for (i = 0; i < count; ++i) {
         const PlayerPlatform *p = &surfaces[i];
         int32_t left, old_right, new_right;
         if (p->kind != PLAYER_SURFACE_SOLID) continue;
         left = (int32_t)p->x * Q_ONE;
         old_right = old_xq + PLAYER_BODY_RIGHT * Q_ONE;
         new_right = proposed_xq + PLAYER_BODY_RIGHT * Q_ONE;
         if (old_right <= left && new_right > left && overlaps_y(s->yq, p) &&
             left < first_left) {
            first_left = left;
            best = left - PLAYER_BODY_RIGHT * Q_ONE;
            collided = 1;
         }
      }
   } else if (proposed_xq < old_xq) {
      int32_t last_right = -0x7fffffffL;
      for (i = 0; i < count; ++i) {
         const PlayerPlatform *p = &surfaces[i];
         int32_t right, old_left, new_left;
         if (p->kind != PLAYER_SURFACE_SOLID) continue;
         right = ((int32_t)p->x + p->w) * Q_ONE;
         old_left = old_xq + PLAYER_BODY_LEFT * Q_ONE;
         new_left = proposed_xq + PLAYER_BODY_LEFT * Q_ONE;
         if (old_left >= right && new_left < right && overlaps_y(s->yq, p) &&
             right > last_right) {
            last_right = right;
            best = right - PLAYER_BODY_LEFT * Q_ONE;
            collided = 1;
         }
      }
   }
   if (best < PLAYER_MIN_X * Q_ONE) {
      best = PLAYER_MIN_X * Q_ONE;
      s->vxq = 0;
      collided = 1;
   }
   if (best > PLAYER_MAX_X * Q_ONE) {
      best = PLAYER_MAX_X * Q_ONE;
      s->vxq = 0;
      collided = 1;
   }
   s->xq = (int16_t)best;
   if (collided) s->vxq = 0;
   return collided;
}

uint8_t collision_resolve_y(PlayerState *s, int32_t old_yq,
                             int32_t proposed_yq,
                             const PlayerPlatform *surfaces, uint8_t count) {
   uint8_t i, landed = 0;
   int32_t best_top = 0x7fffffffL;
   uint8_t best_id = 255;
   if (proposed_yq > old_yq) {
      int32_t old_feet = old_yq + PLAYER_BODY_BOTTOM * Q_ONE;
      int32_t new_feet = proposed_yq + PLAYER_BODY_BOTTOM * Q_ONE;
      for (i = 0; i < count; ++i) {
         const PlayerPlatform *p = &surfaces[i];
         int32_t top = (int32_t)p->y * Q_ONE;
         if ((p->kind != PLAYER_SURFACE_SOLID &&
              p->kind != PLAYER_SURFACE_ONE_WAY) ||
             (p->kind == PLAYER_SURFACE_ONE_WAY && p->id == s->ignore_surface_id))
            continue;
         if (old_feet <= top && new_feet >= top && collision_overlaps_x(s->xq, p) &&
             (top < best_top || (top == best_top && p->id < best_id))) {
            best_top = top;
            best_id = p->id;
            landed = 1;
         }
      }
      if (landed) {
         s->yq = (int16_t)(best_top - PLAYER_BODY_BOTTOM * Q_ONE);
         s->vyq = 0;
         s->grounded = 1;
         s->support_id = best_id;
         s->jump_min_ticks = 0;
         s->ignore_surface_id = 255;
         s->drop_ticks = 0;
         return 1;
      }
   } else if (proposed_yq < old_yq) {
      int32_t highest_bottom = -0x7fffffffL;
      int32_t old_head = old_yq + PLAYER_BODY_TOP * Q_ONE;
      int32_t new_head = proposed_yq + PLAYER_BODY_TOP * Q_ONE;
      for (i = 0; i < count; ++i) {
         const PlayerPlatform *p = &surfaces[i];
         int32_t bottom;
         if (p->kind != PLAYER_SURFACE_SOLID) continue;
         bottom = ((int32_t)p->y + p->h) * Q_ONE;
         if (old_head >= bottom && new_head < bottom && collision_overlaps_x(s->xq, p) &&
             bottom > highest_bottom) highest_bottom = bottom;
      }
      if (highest_bottom != -0x7fffffffL) {
         s->yq = (int16_t)(highest_bottom - PLAYER_BODY_TOP * Q_ONE);
         s->vyq = 0;
         return 0;
      }
   }
   if (proposed_yq > 32767L || proposed_yq < -32768L) {
      s->physics_error = 1;
      if (proposed_yq > 32767L) proposed_yq = 32767L;
      else proposed_yq = -32768L;
      s->vyq = 0;
   }
   s->yq = (int16_t)proposed_yq;
   return 0;
}
