#include <cpctelera.h>
#include <stdint.h>
#include "core/player.h"
#include "core/state.h"

#define Q PLAYER_Q_ONE
#define REPLAY_TICKS 120u
#define PAUSE_TICKS 12u

static const PlayerPlatform surfaces[6] = {
   {0,184,160,16,PLAYER_SURFACE_SOLID,0},
   {42,150,24,2,PLAYER_SURFACE_ONE_WAY,1},
   {80,136,28,2,PLAYER_SURFACE_ONE_WAY,2},
   {120,112,34,2,PLAYER_SURFACE_ONE_WAY,3},
   {76,88,26,2,PLAYER_SURFACE_ONE_WAY,4},
   {20,64,40,2,PLAYER_SURFACE_ONE_WAY,5}
};
static const uint8_t palette[16] = {
   0x14,0x0b,0x17,0x13,0x16,0x00,0x0d,0x06,
   0x03,0x1c,0x05,0x0a,0x0e,0x07,0x1e,0x04
};
static const uint8_t glyphs[4][5] = {
   {6,5,6,4,4}, {2,5,7,5,5}, {3,4,2,1,6}, {7,4,6,4,4}
};

void cadence_main(void);
void main(void) __naked {
   __asm
      ld sp, #0x7ff0
      jp _cadence_main
   __endasm;
}

static void draw_result(uint8_t pass) {
   const uint8_t *word = pass ? (const uint8_t*)"PASS" : (const uint8_t*)"FAIL";
   uint8_t i,row,col,index;
   for(i=0;i<4;i++) {
      uint8_t c=word[i];
      index=(c=='P')?0:(c=='A')?1:(c=='S')?2:3;
      for(row=0;row<5;row++) for(col=0;col<3;col++) {
         uint8_t pixel=(glyphs[index][row] & (uint8_t)(4u>>col)) ?
                       (pass?11:3) : 0;
         uint8_t *dst=cpct_getScreenPtr(CPCT_VMEM_START,
             (uint8_t)(12+i*4+col),(uint8_t)(24+row));
         dst[0]=cpct_px2byteM0(pixel,pixel);
      }
   }
}

static PlayerInput replay_input(uint8_t tick) {
   PlayerInput in;
   in.left=(uint8_t)((tick>=28 && tick<43) || tick==78);
   in.right=(uint8_t)(tick<24 || (tick>=48 && tick<76));
   in.jump_pressed=(uint8_t)(tick==8 || tick==64);
   in.jump_held=(uint8_t)((tick>=8 && tick<19) || (tick>=64 && tick<82));
   in.down=(uint8_t)(tick==96);
   return in;
}

static void spawn(PlayerState *p) {
   p->x=24; p->y=152; p->xq=24*Q; p->yq=152*Q;
   p->vxq=p->vyq=0; p->facing=1; p->grounded=1;
   p->jump_buffer=p->coyote=p->jump_min_ticks=0;
   p->support_id=0; p->ignore_surface_id=255;
   p->drop_ticks=p->physics_error=0;
}

static uint8_t same_state(const PlayerState *a,const PlayerState *b) {
   uint8_t aa[PLAYER_STATE_SERIALIZED_SIZE],bb[PLAYER_STATE_SERIALIZED_SIZE],i;
   player_state_encode(aa,a); player_state_encode(bb,b);
   for(i=0;i<PLAYER_STATE_SERIALIZED_SIZE;i++) if(aa[i]!=bb[i]) return 0;
   return 1;
}

void cadence_main(void) {
   PlayerState every_tick,every_two;
   uint8_t tick,pause,pass=1;
   uint8_t pause_state[PLAYER_STATE_SERIALIZED_SIZE],current_state[PLAYER_STATE_SERIALIZED_SIZE];
   uint16_t presents_tick=0,presents_two=0;
   cpct_disableFirmware();
   cpct_setVideoMode(0);
   cpct_setPalette((uint8_t*)palette,16);
   cpct_memset(CPCT_VMEM_START,0,0x4000);
   spawn(&every_tick); spawn(&every_two);

   for(tick=0;tick<REPLAY_TICKS;tick++) {
      if(tick==40) {
         player_state_encode(pause_state,&every_tick);
         for(pause=0;pause<PAUSE_TICKS;pause++) {
            player_state_encode(current_state,&every_tick);
            if(!same_state(&every_tick,&every_two)) pass=0;
            {
               uint8_t n;
               for(n=0;n<PLAYER_STATE_SERIALIZED_SIZE;n++)
                  if(current_state[n]!=pause_state[n]) pass=0;
            }
         }
      }
      player_step(&every_tick,replay_input(tick),surfaces,6);
      player_step(&every_two,replay_input(tick),surfaces,6);
      ++presents_tick;
      if((tick&1u)==0u) ++presents_two;
      if(!same_state(&every_tick,&every_two)) pass=0;
   }
   if(presents_tick!=REPLAY_TICKS || presents_two!=REPLAY_TICKS/2 ||
      every_tick.physics_error || every_two.physics_error) pass=0;
   draw_result(pass);
   while(1) cpct_waitVSYNC();
}
