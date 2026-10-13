#ifndef BANTERHOUSE2_STATE_H
#define BANTERHOUSE2_STATE_H

#include "player.h"

#define PLAYER_STATE_SERIALIZED_SIZE 19

void player_state_encode(uint8_t out[PLAYER_STATE_SERIALIZED_SIZE],
                         const PlayerState *state);
void player_state_decode(PlayerState *state,
                         const uint8_t in[PLAYER_STATE_SERIALIZED_SIZE]);

#endif
