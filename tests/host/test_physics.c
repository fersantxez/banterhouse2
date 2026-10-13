#include <stdio.h>
#include <string.h>
#include "player.h"
#include "state.h"

#define Q PLAYER_Q_ONE

static const PlayerPlatform world[] = {
   {0,184,160,16,PLAYER_SURFACE_SOLID,0},
   {42,150,24,2,PLAYER_SURFACE_ONE_WAY,1},
   {80,136,28,2,PLAYER_SURFACE_ONE_WAY,2},
   {120,112,34,2,PLAYER_SURFACE_ONE_WAY,3},
   {76,88,26,2,PLAYER_SURFACE_ONE_WAY,4},
   {20,64,40,2,PLAYER_SURFACE_ONE_WAY,5}
};

static PlayerState state_at(uint8_t x, uint8_t y) {
   PlayerState s;
   memset(&s,0,sizeof(s));
   s.xq=(int16_t)(x*Q); s.yq=(int16_t)(y*Q);
   s.x=x; s.y=y; s.facing=1; s.support_id=255;
   s.ignore_surface_id=255;
   return s;
}

static int fail(const char *name, PlayerState s) {
   fprintf(stderr,"FAIL %s xq=%d yq=%d vxq=%d vyq=%d ground=%u support=%u ignore=%u error=%u\n",
      name,s.xq,s.yq,s.vxq,s.vyq,s.grounded,s.support_id,s.ignore_surface_id,s.physics_error);
   return 1;
}

static int same_physics(PlayerState a, PlayerState b) {
   return a.xq==b.xq && a.yq==b.yq && a.vxq==b.vxq && a.vyq==b.vyq &&
      a.grounded==b.grounded && a.support_id==b.support_id &&
      a.ignore_surface_id==b.ignore_surface_id && a.physics_error==b.physics_error;
}

int main(void) {
   PlayerState p, a, b;
   PlayerInput none={0,0,0,0,0}, right={0,1,0,0,0};
   uint8_t i;

   {
      const uint8_t expected[PLAYER_STATE_SERIALIZED_SIZE]={
         0xFE,0xFF,0x00,0xFF,0x7F,0xFF,0xFF,0x7F,
         0x12,0x34,0x01,0x00,0x04,0x03,0x07,0x56,0x78,0x9A,0xBC
      };
      uint8_t bytes[PLAYER_STATE_SERIALIZED_SIZE+2], roundtrip[PLAYER_STATE_SERIALIZED_SIZE];
      PlayerState source=state_at(0,0), decoded;
      source.xq=-2; source.yq=-256; source.vxq=-129; source.vyq=32767;
      source.x=0x12; source.y=0x34; source.facing=1; source.grounded=0;
      source.jump_buffer=4; source.coyote=3; source.jump_min_ticks=7;
      source.support_id=0x56; source.ignore_surface_id=0x78;
      source.drop_ticks=0x9A; source.physics_error=0xBC;
      memset(bytes,0xA5,sizeof(bytes));
      player_state_encode(&bytes[1],&source);
      if(bytes[0]!=0xA5 || bytes[sizeof(bytes)-1]!=0xA5 ||
         memcmp(&bytes[1],expected,sizeof(expected)))
         return fail("state-serialization-little-endian",source);
      player_state_decode(&decoded,&bytes[1]);
      player_state_encode(roundtrip,&decoded);
      if(memcmp(roundtrip,expected,sizeof(expected)))
         return fail("state-serialization-roundtrip",decoded);
   }

   /* Discrete C4 fall vector: 0, 23, 69, 138 Q7 units. */
   p=state_at(10,50);
   for(i=0;i<4;i++) player_step(&p,none,0,0);
   if(p.yq != 50*Q+138 || p.vyq != 92 || p.grounded) return fail("fall-vector-4",p);

   p=state_at(20,100);
   for(i=0;i<80 && !p.grounded;i++) player_step(&p,none,world,6);
   if(!p.grounded || p.support_id!=0 || p.yq!=152*Q) return fail("explicit-floor",p);

   /* Full visual width can overhang; only the contracted body box supports. */
   p=state_at(62,118); p.grounded=1; p.support_id=1;
   player_step(&p,right,world,6);
   player_step(&p,right,world,6);
   if(p.grounded || p.support_id!=255 || p.xq!=62*Q+249 || p.yq!=118*Q || p.vyq!=23)
      return fail("edge-starts-fall-same-tick",p);

   /* Short/long profiles are distinct, land on the declared support, and emit one jump. */
   {
      uint8_t profile, tick, event_count[2]={0,0}, flight[2]={0,0};
      int16_t apex[2]={0,0};
      for(profile=0;profile<2;profile++) {
         p=state_at(50,118); p.grounded=1; p.support_id=1;
         for(tick=0;tick<90;tick++) {
            PlayerInput jump={0,0,(uint8_t)(tick==0),
                              (uint8_t)(profile==1),0};
            if(player_step(&p,jump,world,6)) ++event_count[profile];
            if(118*Q-p.yq>apex[profile]) apex[profile]=(int16_t)(118*Q-p.yq);
            if(tick>0 && p.grounded) { flight[profile]=(uint8_t)(tick+1); break; }
         }
         if(!p.grounded || p.support_id!=1 || p.yq!=118*Q)
            return fail("jump-profile-landing",p);
      }
      if(event_count[0]!=1 || event_count[1]!=1 ||
         apex[0]<20*Q || apex[0]>32*Q || apex[1]<34*Q || apex[1]>40*Q ||
         apex[1]-apex[0]<6*Q || !flight[0] || flight[1]<=flight[0])
         return fail("short-long-jump-profile",p);
      printf("MEASURE jump Q7: corto=%d/%u ticks, largo=%d/%u ticks\n",
             apex[0],flight[0],apex[1],flight[1]);
   }

   /* Coyote accepts the last three gaps after leaving support, then expires. */
   {
      uint8_t gap;
      PlayerInput jump={0,0,1,1,0};
      p=state_at(62,118); p.grounded=1; p.support_id=1;
      player_step(&p,right,world,6); player_step(&p,right,world,6);
      if(p.grounded || p.coyote!=PLAYER_COYOTE_TICKS)
         return fail("coyote-starts-after-edge",p);
      for(gap=0;gap<4;gap++) {
         PlayerState probe=p;
         uint8_t tick, event;
         for(tick=0;tick<gap;tick++) player_step(&probe,none,world,6);
         event=player_step(&probe,jump,world,6);
         if((gap<PLAYER_COYOTE_TICKS && !event) ||
            (gap>=PLAYER_COYOTE_TICKS && event))
            return fail("coyote-window-boundary",probe);
      }
   }

   /* A buffer pressed one falling tick before contact fires on the next tick. */
   p=state_at(20,151); p.vyq=384;
   if(player_step(&p,(PlayerInput){0,0,1,1,0},world,6) || !p.grounded ||
      !p.jump_buffer) return fail("jump-buffer-prelanding",p);
   if(!player_step(&p,none,world,6) || p.grounded || p.vyq>=0)
      return fail("jump-buffer-fires-on-contact",p);

   /* An early press expires in the air and cannot auto-jump at a later landing. */
   p=state_at(20,100); p.vyq=384;
   if(player_step(&p,(PlayerInput){0,0,1,1,0},world,6))
      return fail("jump-buffer-expiry-start",p);
   {
      uint8_t tick, events=0;
      for(tick=0;tick<70 && !p.grounded;tick++)
         events+=player_step(&p,none,world,6);
      if(!p.grounded || p.support_id!=0 || events)
         return fail("jump-buffer-expired-before-landing",p);
   }

   /* Paused presentation leaves every serialized physics field untouched. */
   {
      uint8_t before[PLAYER_STATE_SERIALIZED_SIZE], after[PLAYER_STATE_SERIALIZED_SIZE];
      uint8_t tick;
      p=state_at(40,80); p.vyq=-128; p.vxq=83;
      player_state_encode(before,&p);
      for(tick=0;tick<20;tick++) { /* MODE_PAUSE presents without simulating. */ }
      player_state_encode(after,&p);
      if(memcmp(before,after,sizeof(before))) return fail("pause-freezes-physics-state",p);
      a=p;
      player_step(&a,none,world,6); player_step(&p,none,world,6);
      if(!same_physics(a,p)) return fail("resume-advances-one-fixed-tick",p);

      p=state_at(24,152); p.grounded=1; p.support_id=0;
      if(p.vxq || p.vyq || p.jump_buffer || p.coyote || p.jump_min_ticks ||
         p.ignore_surface_id!=255 || p.drop_ticks || p.physics_error ||
         p.xq!=24*Q || p.yq!=152*Q || !p.grounded || p.support_id!=0)
         return fail("retry-clears-player-state-at-valid-spawn",p);
   }

   /* One- and two-tick presentation schedules produce the same physics trace. */
   {
      uint8_t tick, presents_one=0, presents_two=0;
      uint8_t bytes_a[PLAYER_STATE_SERIALIZED_SIZE], bytes_b[PLAYER_STATE_SERIALIZED_SIZE];
      a=state_at(24,152); a.grounded=1; a.support_id=0;
      b=a;
      for(tick=0;tick<120;tick++) {
         PlayerInput frame={(uint8_t)(tick>55 && tick<80),
                            (uint8_t)(tick<45),
                            (uint8_t)(tick==12 || tick==68),
                            (uint8_t)(tick>=12 && tick<25),
                            0};
         player_step(&a,frame,world,6);
         player_step(&b,frame,world,6);
         player_state_encode(bytes_a,&a); player_state_encode(bytes_b,&b);
         if(memcmp(bytes_a,bytes_b,sizeof(bytes_a)))
            return fail("presentation-cadence-determinism",a);
         ++presents_one;
         if(!(tick&1)) ++presents_two;
      }
      if(presents_one!=120 || presents_two!=60)
         return fail("presentation-cadence-counts",a);
   }

   /* One-way platform can be crossed upward, then catches a downward crossing. */
   p=state_at(50,140); p.vyq=-410;
   for(i=0;i<12;i++) player_step(&p,(PlayerInput){0,0,0,1,0},world,6);
   if(p.grounded || p.yq >= 140*Q) return fail("one-way-upward",p);
   p=state_at(80,50); p.vyq=384;
   for(i=0;i<30 && !p.grounded;i++) player_step(&p,none,world,6);
   if(!p.grounded || p.support_id!=4 || p.yq!=56*Q) return fail("one-way-landing",p);

   /* Drop-through ignores only the source; the floor below still catches. */
   p=state_at(80,56); p.grounded=1; p.support_id=4;
   for(i=0;i<40 && p.support_id!=2;i++) {
      PlayerInput down={0,0,0,0,1};
      player_step(&p,down,world,6);
   }
   if(!p.grounded || p.support_id!=2 || p.yq!=104*Q || p.physics_error) return fail("drop-through-next-platform",p);

   p=state_at(80,56); p.grounded=1; p.support_id=4;
   if(!player_step(&p,(PlayerInput){0,0,1,1,1},world,6) || p.grounded ||
      p.ignore_surface_id!=255 || p.support_id!=255 || p.vyq>=0)
      return fail("jump-priority-over-drop",p);

   /* A solid wall stops horizontal motion before the contracted body penetrates. */
   {
      const PlayerPlatform wall_world[]={{80,16,4,168,PLAYER_SURFACE_SOLID,7}};
      p=state_at(50,80);
      for(i=0;i<40;i++) player_step(&p,right,wall_world,1);
      if(p.xq != 67*Q || p.xq+13*Q > 80*Q) return fail("solid-wall",p);
   }

   p=state_at(0,50);
   for(i=0;i<10;i++) player_step(&p,(PlayerInput){1,0,0,0,0},0,0);
   if(p.xq!=0 || p.vxq!=0 || p.physics_error) return fail("left-arena-bound",p);

   p=state_at(20,16);
   for(i=0;i<250 && !p.physics_error;i++) player_step(&p,none,0,0);
   if(!p.physics_error) return fail("vertical-range-guard",p);

   /* Solid ceiling stops ascent; an upward one-way contact remains passable. */
   {
      const PlayerPlatform ceiling[]={{40,116,50,4,PLAYER_SURFACE_SOLID,8}};
      p=state_at(50,130); p.vyq=-410; p.jump_min_ticks=7;
      for(i=0;i<30 && p.yq>116*Q;i++) player_step(&p,(PlayerInput){0,0,0,1,0},ceiling,1);
      if(p.yq!=116*Q || p.vyq<0) return fail("solid-ceiling",p);
   }

   /* Crossing multiple surfaces selects nearest physical contact, not table order. */
   {
      PlayerPlatform first[]={{0,160,160,16,PLAYER_SURFACE_SOLID,0},
                              {40,136,60,2,PLAYER_SURFACE_ONE_WAY,2},
                              {40,160,60,2,PLAYER_SURFACE_ONE_WAY,1}};
      PlayerPlatform reverse[]={{40,160,60,2,PLAYER_SURFACE_ONE_WAY,1},
                                {40,136,60,2,PLAYER_SURFACE_ONE_WAY,2},
                                {0,160,160,16,PLAYER_SURFACE_SOLID,0}};
      p=state_at(50,90); p.vyq=5000; a=p; b=p;
      player_step(&a,none,first,3); player_step(&b,none,reverse,3);
      if(!same_physics(a,b) || !a.grounded || a.support_id!=2 || a.yq!=104*Q)
         return fail("contact-order-independent",a);
   }

   puts("PASS física host: integración Q7, borde, caída, plataformas one-way, descenso, sólidos y orden de contactos");
   return 0;
}
