#include <cpctelera.h>
#include <stdint.h>
#include "core/player.h"
#include "core/state.h"

static const PlayerPlatform platforms[6] = {
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
static const uint8_t font[6][5] = {
   {6,5,6,4,4}, /* P */
   {2,5,7,5,5}, /* A */
   {3,4,2,1,6}, /* S */
   {7,4,6,4,4}, /* F */
   {7,2,2,2,7}, /* I */
   {4,4,4,4,7}  /* L */
};
static const uint8_t hex_font[16][5] = {
   {7,5,5,5,7},{2,6,2,2,7},{6,1,2,4,7},{6,1,2,1,6},
   {5,5,7,1,1},{7,4,6,1,6},{3,4,6,5,2},{7,1,2,2,2},
   {2,5,2,5,2},{2,5,3,1,6},{2,5,7,5,5},{6,5,6,5,6},
   {3,4,4,4,3},{6,5,5,5,6},{7,4,6,4,7},{7,4,6,4,4}
};

void physics_main(void);
void main(void) __naked {
   __asm
      ld sp, #0x7ff0
      jp _physics_main
   __endasm;
}

static uint8_t glyph(char c) {
   if(c=='P') return 0; if(c=='A') return 1; if(c=='S') return 2;
   if(c=='F') return 3; if(c=='I') return 4; return 5;
}

static void draw_result(const char *text, uint8_t ink, uint8_t y) {
   uint8_t i=0,row,col;
   while(text[i]) {
      uint8_t index=glyph(text[i]);
      for(row=0;row<5;row++) for(col=0;col<3;col++) {
         uint8_t pixel=(font[index][row] & (uint8_t)(4u >> col)) ? ink : 0;
         uint8_t *dst=cpct_getScreenPtr(CPCT_VMEM_START,
             (uint8_t)(12+i*4+col),(uint8_t)(y+row));
         dst[0]=cpct_px2byteM0(pixel,pixel);
      }
      ++i;
   }
}

static void draw_hex(uint8_t y, uint16_t value) {
   uint8_t digit,row,col;
   for(digit=0;digit<4;digit++) {
      uint8_t nibble=(uint8_t)((value >> (12-digit*4)) & 15);
      for(row=0;row<5;row++) for(col=0;col<3;col++) {
         uint8_t pixel=(hex_font[nibble][row] & (uint8_t)(4u >> col)) ? 11 : 0;
         uint8_t *dst=cpct_getScreenPtr(CPCT_VMEM_START,
             (uint8_t)(12+digit*4+col), (uint8_t)(y+row));
         dst[0]=cpct_px2byteM0(pixel,pixel);
      }
   }
}

static void state_at(PlayerState *p, uint8_t x, uint8_t y) {
   p->xq=x*128; p->yq=y*128; p->vxq=p->vyq=0;
   p->x=x; p->y=y; p->facing=1; p->grounded=0;
   p->jump_buffer=p->coyote=p->jump_min_ticks=0;
   p->support_id=p->ignore_surface_id=255;
   p->drop_ticks=p->physics_error=0;
}

static void copy_state(PlayerState *to, const PlayerState *from) {
   to->xq=from->xq; to->yq=from->yq; to->vxq=from->vxq; to->vyq=from->vyq;
   to->x=from->x; to->y=from->y; to->facing=from->facing; to->grounded=from->grounded;
   to->jump_buffer=from->jump_buffer; to->coyote=from->coyote;
   to->jump_min_ticks=from->jump_min_ticks; to->support_id=from->support_id;
   to->ignore_surface_id=from->ignore_surface_id; to->drop_ticks=from->drop_ticks;
   to->physics_error=from->physics_error;
}

void physics_main(void) {
   PlayerState p,a,b,diag;
   PlayerState decoded;
   PlayerInput none={0,0,0,0,0}, right={0,1,0,0,0}, left={1,0,0,0,0};
   PlayerInput down={0,0,0,0,1};
   uint16_t checks=0;
   uint8_t tick, drop_start_ok, events;
   uint8_t profile, flight[2]={0,0}, jump_events[2]={0,0}, gap;
   int16_t apex[2]={0,0};
   uint8_t encoded[PLAYER_STATE_SERIALIZED_SIZE];
   uint8_t roundtrip[PLAYER_STATE_SERIALIZED_SIZE];
   const uint8_t expected[PLAYER_STATE_SERIALIZED_SIZE]={
      0xFE,0xFF,0x00,0xFF,0x7F,0xFF,0xFF,0x7F,
      0x12,0x34,0x01,0x00,0x04,0x03,0x07,0x56,0x78,0x9A,0xBC
   };
   const PlayerPlatform wall[1]={{80,16,4,168,PLAYER_SURFACE_SOLID,7}};
   const PlayerPlatform ceiling[1]={{40,116,50,4,PLAYER_SURFACE_SOLID,8}};
   const PlayerPlatform first[3]={{0,160,160,16,PLAYER_SURFACE_SOLID,0},
      {40,136,60,2,PLAYER_SURFACE_ONE_WAY,2},
      {40,160,60,2,PLAYER_SURFACE_ONE_WAY,1}};
   const PlayerPlatform reverse[3]={{40,160,60,2,PLAYER_SURFACE_ONE_WAY,1},
      {40,136,60,2,PLAYER_SURFACE_ONE_WAY,2},
      {0,160,160,16,PLAYER_SURFACE_SOLID,0}};
   cpct_disableFirmware();
   cpct_setVideoMode(0);
   cpct_setPalette((uint8_t*)palette,16);
   cpct_memset(CPCT_VMEM_START,0,0x4000);
   state_at(&diag,0,0);

   /* 0: first tick without support begins falling in the same simulation tick. */
   state_at(&p,62,118); p.grounded=1; p.support_id=1;
   player_step(&p,right,platforms,6); player_step(&p,right,platforms,6);
   if(p.xq==62*128+249 && p.yq==118*128 && !p.grounded &&
      p.vyq==23 && p.support_id==255) checks|=1;

   /* 1: discrete free-fall values match the independently calculated vector. */
   state_at(&p,10,50);
   for(tick=0;tick<4;tick++) player_step(&p,none,0,0);
   if(p.yq==50*128+138 && p.vyq==92 && !p.grounded) checks|=2;

   /* 8: declared floor catches a fall without an implicit world clamp. */
   state_at(&p,20,100);
   for(tick=0;tick<80 && !p.grounded;tick++) player_step(&p,none,platforms,6);
   if(p.grounded && p.support_id==0 && p.yq==152*128) checks|=256;

   /* 2: one-way platform is passable from below while ascending. */
   state_at(&p,50,140); p.vyq=-410;
   for(tick=0;tick<12;tick++) player_step(&p,(PlayerInput){0,0,0,1,0},platforms,6);
   if(!p.grounded && p.yq<140*128) checks|=4;

   /* 3: downward crossing lands on the first reachable ledge. */
   state_at(&p,80,50); p.vyq=384;
   for(tick=0;tick<30 && !p.grounded;tick++) player_step(&p,none,platforms,6);
   if(p.grounded && p.support_id==4 && p.yq==56*128) checks|=8;

   /* 4: drop ignores its source and lands on the lower platform. */
   state_at(&p,80,56); p.grounded=1; p.support_id=4;
   player_step(&p,down,platforms,6);
   drop_start_ok=(uint8_t)(!p.grounded && p.support_id==255 && p.ignore_surface_id==4);
   if(!drop_start_ok) copy_state(&diag,&p);
   for(tick=0;tick<40 && p.support_id!=2;tick++) player_step(&p,down,platforms,6);
   if(drop_start_ok && p.grounded && p.support_id==2 && p.yq==104*128 && !p.physics_error) checks|=16;
   else if(drop_start_ok) copy_state(&diag,&p);

   /* 5: solid wall resolves at x=67 for the [x+3,x+13) body. */
   state_at(&p,50,80);
   for(tick=0;tick<40;tick++) player_step(&p,right,wall,1);
   if(p.xq==67*128 && p.xq+13*128<=80*128) checks|=32;

   /* 6: solid ceiling stops ascent at its underside. */
   state_at(&p,50,130); p.vyq=-410; p.jump_min_ticks=7;
   for(tick=0;tick<30 && p.yq>116*128;tick++)
      player_step(&p,(PlayerInput){0,0,0,1,0},ceiling,1);
   if(p.yq==116*128 && p.vyq>=0) checks|=64;

   /* 7: equal input gives the same nearest contact in either table order. */
   state_at(&p,50,90); p.vyq=5000; copy_state(&a,&p); copy_state(&b,&p);
   player_step(&a,none,first,3); player_step(&b,none,reverse,3);
   if(a.yq==104*128 && a.support_id==2 && a.grounded &&
      b.yq==a.yq && b.support_id==a.support_id && b.grounded) checks|=128;

   /* 9: arena edge clamps without signed wrap or a fake support. */
   state_at(&p,0,50);
   for(tick=0;tick<10;tick++) player_step(&p,left,0,0);
   if(p.xq==0 && p.vxq==0 && !p.physics_error) checks|=512;

   /* 10: an unbounded fall reports range exhaustion before int16 wraps. */
   state_at(&p,20,16);
   for(tick=0;tick<255 && !p.physics_error;tick++) player_step(&p,none,0,0);
   if(p.physics_error) checks|=1024;

   /* 11: explicit little-endian bytes survive CPC decode/encode and signed sentinels. */
   state_at(&p,0,0);
   p.xq=-2; p.yq=-256; p.vxq=-129; p.vyq=32767;
   p.x=0x12; p.y=0x34; p.facing=1; p.grounded=0;
   p.jump_buffer=4; p.coyote=3; p.jump_min_ticks=7;
   p.support_id=0x56; p.ignore_surface_id=0x78;
   p.drop_ticks=0x9A; p.physics_error=0xBC;
   player_state_encode(encoded,&p);
   player_state_decode(&decoded,encoded);
   player_state_encode(roundtrip,&decoded);
   for(tick=0;tick<PLAYER_STATE_SERIALIZED_SIZE;tick++)
      if(encoded[tick]!=expected[tick] || roundtrip[tick]!=expected[tick]) break;
   if(tick==PLAYER_STATE_SERIALIZED_SIZE && decoded.xq==-2 &&
      decoded.yq==-256 && decoded.vxq==-129 && decoded.vyq==32767 &&
      decoded.support_id==0x56 && decoded.physics_error==0xBC) checks|=2048;

   /* 12: measured short/long jump profiles from a real support. */
   for(profile=0;profile<2;profile++) {
      state_at(&p,50,118); p.grounded=1; p.support_id=1;
      for(tick=0;tick<90;tick++) {
         PlayerInput jump={(uint8_t)0,(uint8_t)0,(uint8_t)(tick==0),
                           (uint8_t)(profile==1),(uint8_t)0};
         jump_events[profile]+=player_step(&p,jump,platforms,6);
         if(118*128-p.yq>apex[profile]) apex[profile]=(int16_t)(118*128-p.yq);
         if(tick>0 && p.grounded) { flight[profile]=(uint8_t)(tick+1); break; }
      }
      if(!p.grounded || p.support_id!=1 || p.yq!=118*128) break;
   }
   if(profile==2 && jump_events[0]==1 && jump_events[1]==1 &&
      apex[0]>=20*128 && apex[0]<=32*128 &&
      apex[1]>=34*128 && apex[1]<=40*128 &&
      apex[1]-apex[0]>=6*128 && flight[0] && flight[1]>flight[0]) checks|=4096;

   /* 13: three post-edge coyote ticks accepted, fourth rejected. */
   state_at(&p,62,118); p.grounded=1; p.support_id=1;
   player_step(&p,right,platforms,6); player_step(&p,right,platforms,6);
   if(!p.grounded && p.coyote==PLAYER_COYOTE_TICKS) {
      uint8_t coyote_ok=1;
      for(gap=0;gap<=PLAYER_COYOTE_TICKS;gap++) {
         PlayerState probe;
         copy_state(&probe,&p);
         for(tick=0;tick<gap;tick++) player_step(&probe,none,platforms,6);
         if((player_step(&probe,(PlayerInput){0,0,1,1,0},platforms,6)!=0) !=
            (gap<PLAYER_COYOTE_TICKS)) coyote_ok=0;
      }
      if(coyote_ok) checks|=8192;
   }

   /* 14: a buffered press just before floor contact launches next tick. */
   state_at(&p,20,151); p.vyq=384;
   if(!player_step(&p,(PlayerInput){0,0,1,1,0},platforms,6) &&
      p.grounded && p.jump_buffer &&
      player_step(&p,none,platforms,6) && !p.grounded && p.vyq<0) checks|=16384;

   /* 15: buffer expires in the air and cannot auto-jump on later landing. */
   state_at(&p,20,100); p.vyq=384;
   events=player_step(&p,(PlayerInput){0,0,1,1,0},platforms,6);
   for(tick=0;tick<70 && !p.grounded;tick++)
      events+=player_step(&p,none,platforms,6);
   if(!events && p.grounded && p.support_id==0) checks|=32768;

   draw_result(checks==65535 ? "PASS" : "FAIL",checks==65535 ? 11 : 3,24);
   draw_hex(40,checks);
   draw_hex(108,(uint16_t)diag.xq);
   draw_hex(120,(uint16_t)diag.yq);
   draw_hex(132,(uint16_t)diag.vyq);
   draw_hex(144,(uint16_t)diag.support_id);
   draw_hex(156,(uint16_t)diag.grounded);
   draw_hex(168,(uint16_t)diag.ignore_surface_id);
   draw_hex(180,(uint16_t)diag.drop_ticks);
   while(1) cpct_waitVSYNC();
}
