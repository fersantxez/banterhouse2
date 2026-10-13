#ifndef BANTERHOUSE2_COLLISION_H
#define BANTERHOUSE2_COLLISION_H

#include "player.h"

int32_t collision_floor_pixel(int32_t q);
uint8_t collision_overlaps_x(int32_t xq, const PlayerPlatform *surface);
const PlayerPlatform *collision_surface_by_id(const PlayerPlatform *surfaces,
                                               uint8_t count, uint8_t id);
uint8_t collision_resolve_x(PlayerState *state, int32_t old_xq,
                             int32_t proposed_xq,
                             const PlayerPlatform *surfaces, uint8_t count);
uint8_t collision_resolve_y(PlayerState *state, int32_t old_yq,
                             int32_t proposed_yq,
                             const PlayerPlatform *surfaces, uint8_t count);
/* Continuous relative-motion AABB test; time is returned as unsigned Q0.16. */
uint8_t collision_sweep_aabb(int16_t ax0, int16_t ay0,
                              int16_t ax1, int16_t ay1,
                              int16_t aw, int16_t ah,
                              int16_t bx0, int16_t by0,
                              int16_t bx1, int16_t by1,
                              int16_t bw, int16_t bh,
                              uint16_t *time_q16);
int16_t collision_interpolate_q16(int16_t a, int16_t b, uint16_t t_q16);

#endif
