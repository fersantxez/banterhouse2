#include <cpctelera.h>
#include <stdint.h>
#include "core/player.h"
#include "core/collision.h"
#include "core/state.h"

#define Q PLAYER_Q_ONE
#define CAMPAIGN_REPLAY_SEED 0xB2C2u
#define CAMPAIGN_REPLAY_TICKS 256u
#define HOST_EXPECTED_REPLAY_HASH 0xB0D5
static const uint16_t host_prefix_hashes[16] = {
   0xE453,0x2A06,0x3445,0xF301,0xE8E3,0xCECB,0xC4B1,0x0D97,
   0x747F,0xEDF1,0xCA5D,0x6C55,0x447E,0x64C4,0x5DEB,0xB0D5
};

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
static const uint8_t font[5][5] = {
   {6,5,6,4,4}, {2,5,7,5,5}, {3,4,2,1,6},
   {7,4,6,4,4}, {6,1,2,1,6}
};
static const uint8_t hex_font[16][5] = {
   {7,5,5,5,7},{2,6,2,2,7},{6,1,2,4,7},{6,1,2,1,6},
   {5,5,7,1,1},{7,4,6,1,6},{3,4,6,5,2},{7,1,2,2,2},
   {2,5,2,5,2},{2,5,3,1,6},{2,5,7,5,5},{6,5,6,5,6},
   {3,4,4,4,3},{6,5,5,5,6},{7,4,6,4,7},{7,4,6,4,4}
};

void campaign_main(void);
void main(void) __naked {
   __asm
      ld sp, #0x7ff0
      jp _campaign_main
   __endasm;
}

static void draw_text(const uint8_t *text, uint8_t y, uint8_t ink) {
   uint8_t i=0,row,col,index;
   while(text[i]) {
      uint8_t c=text[i++];
      index=(c=='P')?0:(c=='A')?1:(c=='S')?2:(c=='F')?3:4;
      for(row=0;row<5;row++) for(col=0;col<3;col++) {
         uint8_t pixel=(font[index][row] & (uint8_t)(4u>>col)) ? ink : 0;
         uint8_t *dst=cpct_getScreenPtr(CPCT_VMEM_START,
             (uint8_t)(12+(i-1)*4+col),(uint8_t)(y+row));
         dst[0]=cpct_px2byteM0(pixel,pixel);
      }
   }
}

static void draw_hex(uint8_t y, uint16_t value) {
   uint8_t digit,row,col,nibble;
   for(digit=0;digit<4;digit++) {
      nibble=(uint8_t)((value>>(12-digit*4))&15);
      for(row=0;row<5;row++) for(col=0;col<3;col++) {
         uint8_t pixel=(hex_font[nibble][row] & (uint8_t)(4u>>col)) ? 11 : 0;
         uint8_t *dst=cpct_getScreenPtr(CPCT_VMEM_START,
             (uint8_t)(12+digit*4+col),(uint8_t)(y+row));
         dst[0]=cpct_px2byteM0(pixel,pixel);
      }
   }
}

static uint8_t valid(const PlayerState *p) {
   uint8_t i,found=0;
   if(p->physics_error || p->xq<0 || p->xq>PLAYER_MAX_X*Q ||
      p->yq<PLAYER_MIN_Y*Q || p->yq>152*Q ||
      p->x!=(uint8_t)collision_floor_pixel(p->xq) ||
      p->y!=(uint8_t)collision_floor_pixel(p->yq)) return 0;
   if(!p->grounded) return p->support_id==255;
   for(i=0;i<6;i++) if(surfaces[i].id==p->support_id &&
      p->yq+PLAYER_BODY_BOTTOM*Q==(int32_t)surfaces[i].y*Q &&
      collision_overlaps_x(p->xq,&surfaces[i])) found=1;
   return (uint8_t)(found && p->vyq==0);
}

void campaign_main(void) {
   PlayerState p={0};
   PlayerInput in;
   uint8_t bytes[PLAYER_STATE_SERIALIZED_SIZE],n,failed=0;
   uint16_t tick,digest=0xB271;
   uint16_t rng=CAMPAIGN_REPLAY_SEED,r;
   cpct_disableFirmware();
   cpct_setVideoMode(0);
   cpct_setPalette((uint8_t*)palette,16);
   cpct_memset(CPCT_VMEM_START,0,0x4000);
   p.x=24; p.y=152; p.xq=24*Q; p.yq=152*Q;
   p.grounded=1; p.facing=1; p.support_id=0; p.ignore_surface_id=255;
   for(tick=0;tick<CAMPAIGN_REPLAY_TICKS;tick++) {
      rng=(uint16_t)(rng*25173u+13849u);
      r=rng;
      in.left=(uint8_t)(r&1); in.right=(uint8_t)((r>>1)&1);
      in.jump_pressed=(uint8_t)(((r>>5)&31)==0);
      in.jump_held=(uint8_t)((r>>10)&1);
      in.down=(uint8_t)(((r>>11)&31)==0);
      player_step(&p,in,surfaces,6);
      if(!valid(&p)) { failed=1; break; }
      player_state_encode(bytes,&p);
      for(n=0;n<PLAYER_STATE_SERIALIZED_SIZE;n++)
         digest=(uint16_t)((uint16_t)(digest*257u)+(uint16_t)bytes[n]);
      if(((tick+1u)&15u)==0u) {
         if(digest!=host_prefix_hashes[tick>>4]) failed=1;
         draw_hex((uint8_t)(40u+(tick>>4)*8u),digest);
      }
   }
   draw_text((const uint8_t*)(!failed && tick==CAMPAIGN_REPLAY_TICKS &&
      digest==HOST_EXPECTED_REPLAY_HASH ? "PASS" : "FAIL"),24,
      (!failed && tick==CAMPAIGN_REPLAY_TICKS && digest==HOST_EXPECTED_REPLAY_HASH) ? 11 : 3);
   while(1) cpct_waitVSYNC();
}
