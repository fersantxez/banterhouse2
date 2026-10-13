#include "state.h"

static void write_i16(uint8_t *out, int16_t value) {
   uint16_t bits = (uint16_t)value;
   out[0] = (uint8_t)bits;
   out[1] = (uint8_t)(bits >> 8);
}

static int16_t read_i16(const uint8_t *in) {
   uint16_t bits = (uint16_t)in[0] | ((uint16_t)in[1] << 8);
   int32_t value = bits;
   if (bits & 0x8000u) value -= 65536L;
   return (int16_t)value;
}

void player_state_encode(uint8_t out[PLAYER_STATE_SERIALIZED_SIZE],
                         const PlayerState *s) {
   write_i16(&out[0], s->xq);
   write_i16(&out[2], s->yq);
   write_i16(&out[4], s->vxq);
   write_i16(&out[6], s->vyq);
   out[8]=s->x; out[9]=s->y; out[10]=s->facing; out[11]=s->grounded;
   out[12]=s->jump_buffer; out[13]=s->coyote; out[14]=s->jump_min_ticks;
   out[15]=s->support_id; out[16]=s->ignore_surface_id;
   out[17]=s->drop_ticks; out[18]=s->physics_error;
}

void player_state_decode(PlayerState *s,
                         const uint8_t in[PLAYER_STATE_SERIALIZED_SIZE]) {
   s->xq=read_i16(&in[0]);
   s->yq=read_i16(&in[2]);
   s->vxq=read_i16(&in[4]);
   s->vyq=read_i16(&in[6]);
   s->x=in[8]; s->y=in[9]; s->facing=in[10]; s->grounded=in[11];
   s->jump_buffer=in[12]; s->coyote=in[13]; s->jump_min_ticks=in[14];
   s->support_id=in[15]; s->ignore_surface_id=in[16];
   s->drop_ticks=in[17]; s->physics_error=in[18];
}
