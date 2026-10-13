/* Includes the actual game implementation: only CPC I/O is stubbed. */
#define BH2_HOST 1
#include "../../src/main.c"
#undef grounded
#undef facing
#include <stdio.h>
#include <stdlib.h>
#define ASSET(name) const u8 name[1]={0}
ASSET(copier_even);ASSET(copier_odd);ASSET(bg1);ASSET(bg2);ASSET(bg3);ASSET(bg4);
ASSET(palette1);ASSET(palette2);ASSET(palette3);ASSET(palette4);
ASSET(pitu_r_0);ASSET(pitu_r_1);ASSET(pitu_l_0);ASSET(pitu_l_1);
ASSET(pitu_walk_r_0);ASSET(pitu_walk_r_1);ASSET(pitu_walk_l_0);ASSET(pitu_walk_l_1);
ASSET(alberto_r_0);ASSET(alberto_r_1);ASSET(alberto_l_0);ASSET(alberto_l_1);
void zx0_from_c(const u8* s,u8* d){(void)s;memset(host_ptr(d),0,16384);}
#define NOOP(f) void f(void){}
static AudioEvent played_audio[4096];
static unsigned played_count;
static void record_audio(AudioEvent event){if(played_count<sizeof(played_audio)/sizeof(played_audio[0]))played_audio[played_count++]=event;}
NOOP(sfx_init) NOOP(sfx_mute) NOOP(music_init) NOOP(music_tick) NOOP(music_toggle)
NOOP(music_pause) NOOP(music_resume)
void sfx_step(void){record_audio(AUDIO_EVENT_STEP);}
void sfx_jump(void){record_audio(AUDIO_EVENT_JUMP);}
void sfx_seal(void){record_audio(AUDIO_EVENT_SEAL);}
void sfx_land(void){record_audio(AUDIO_EVENT_LAND);}
void sfx_return(void){record_audio(AUDIO_EVENT_RETURN);}
void sfx_hit(void){record_audio(AUDIO_EVENT_DAMAGE);}
void sfx_machine(void){record_audio(AUDIO_EVENT_MACHINE);}
static u8 held_input, prev_input;
void input_reset(void){held_input=prev_input=0;}
void input_sample(InputFrame* f){input_derive(held_input,prev_input,f);prev_input=held_input;}
static void step(u8 keys){held_input=keys;game_tick();audio_tick();record_demo_evidence();}
static void set_hostile_paper(u8 slot,int16_t xq,u8 y,u8 dir){
 papers[slot].xq=xq;papers[slot].y=y;papers[slot].dir=dir;
 papers[slot].prev_xq=xq;
 papers[slot].live=1;papers[slot].returned=0;papers[slot].state=PROJECTILE_HOSTILE;
 papers[slot].born=0;papers[slot].bounced=0;papers[slot].scored_mask=0;
}

static u8 recording[60000];
static unsigned recorded;
static unsigned deaths, strategy;
static u8 auto_seal(u8 keys) {
 unsigned i; int front;
 for(i=0;i<4;i++) if(papers[i].live&&!papers[i].returned&&papers[i].y+4>player_y+12&&papers[i].y<player_y+26) {
  int x=papers[i].xq/2;
  if((papers[i].dir&&x>=player_x-12&&x<=player_x+4)||(!papers[i].dir&&x>=player_x+10&&x<=player_x+26))
   keys=(keys&~3)|(papers[i].dir?INPUT_LEFT:INPUT_RIGHT);
 }
 u8 face=(keys&INPUT_RIGHT)?1:(keys&INPUT_LEFT)?0:pitu.facing;
 front=face?player_x+13:(player_x>5?player_x-5:0);
 if(!seal_cooldown && !(prev_input&INPUT_ACTION)) {
  for(i=0;i<4;i++) if(papers[i].live&&!papers[i].returned&&papers[i].y+4>player_y+12&&papers[i].y<player_y+26) {
   int x=papers[i].xq/2;
   if(x+4>front-4&&x<front+12) keys|=INPUT_ACTION;
  }
  for(i=0;i<3;i++) if(machines[i].live&&machines[i].wait==0&&machines[i].ground==player_y+32) {
   int x=machines[i].x+(machines[i].dir?14:0);
   if(x+4>front&&x<front+8) keys|=INPUT_ACTION;
  }
 }
 return keys;
}
static int run(u8 keys) {
 keys=auto_seal(keys);
 assert(recorded<sizeof(recording));recording[recorded++]=keys;
 step(keys);
 if(mode==MODE_HURT) {deaths++;return 0;}
 return !pitu.physics_error;
}
static PlayerInput pi(u8 keys,u8 prev){PlayerInput in={(keys&1)!=0,(keys&2)!=0,(keys&4)&&!(prev&4),(keys&4)!=0,(keys&8)!=0};return in;}
/* Plan motions using copies of player_step; actual game advances only via run. */
static int jump_to(u8 to) {
 int x,dir,hold,move,t,walk_n;u8 walkkeys[160];
 PlayerState start,pred;
 u8 from=pitu.support_id,pk;
 if(from)for(unsigned w=0;w<strategy;w++)if(!run(0))return 0;
 for(int off=0;off<160;off++) {
  x=pitu.x+((off&1)?-1:1)*((off+1)/2)*2;
  if(x<0||x>144||x<ledges[from].x-11||x>=ledges[from].x+ledges[from].w-3)continue;
  start=pitu;walk_n=0;pk=prev_input;
  while(abs(start.x-x)>1 && walk_n<155) {
   u8 k=start.x<x?2:1;
   player_step(&start,pi(k,pk),ledges,6);pk=k;walkkeys[walk_n++]=k;
   if(!start.grounded||start.support_id!=from)break;
  }
  if(!start.grounded||start.support_id!=from||walk_n>=155)continue;
  player_step(&start,pi(0,pk),ledges,6);walkkeys[walk_n++]=0;
  if(!start.grounded)continue;
  for(dir=0;dir<2;dir++)for(hold=7;hold<=28;hold+=7)for(move=0;move<=44;move+=2){
   pred=start;pk=0;
   for(t=0;t<65;t++){
    u8 k=(t<hold?4:0)|(t<move?(dir?2:1):0);
    player_step(&pred,pi(k,pk),ledges,6);pk=k;
    if(t>0&&pred.grounded)break;
   }
   if(pred.grounded&&pred.support_id==to){
    int j;
    for(j=0;j<walk_n;j++)if(!run(walkkeys[j]))return 0;
    for(j=0;j<=t;j++)if(!run((j<hold?4:0)|(j<move?(dir?2:1):0)))return 0;
    if(pitu.support_id!=to){fprintf(stderr,"DIVERGED jump from %u to %u got %u\n",from,to,pitu.support_id);return 0;}
    return 1;
   }
  }
 }
 fprintf(stderr,"NO JUMP %u -> %u x=%u\n",from,to,player_x);return 0;
}
static int travel(u8 dest){
 unsigned n=0;
 if(pitu.grounded&&pitu.support_id>dest){
  while(!pitu.grounded||pitu.support_id!=0){if(!run((n++&1)?0:8)||n>400)return 0;}
 }
 while(!pitu.grounded){if(!run(0)||++n>500)return 0;}
 while(pitu.support_id<dest)if(!jump_to(pitu.support_id+1))return 0;
 return pitu.support_id==dest;
}
static int walk_to(int x){unsigned n=0;while(mode==MODE_PLAY && abs(player_x-x)>1){if(!run(player_x<x?2:1)||++n>220)return 0;}return run(0);}

static int solve_arena(unsigned delay){
 unsigned j,k,n;
 if(!run(0))return 0;
 for(n=0;n<delay;n++)if(!run(0))return 0;
 for(unsigned objective=0;objective<3;objective++){
  j=3;
  for(k=0;k<3;k++)if(machines[k].live && (j==3 || machines[k].ground>machines[j].ground))j=k;
  if(j==3)break;
  int stance;u8 support=0;
  for(k=0;k<6;k++)if(ledges[k].y==machines[j].ground)support=k;
  if(!travel(support))return 0;
  stance=machines[j].dir?machines[j].x+17:machines[j].x-19;
  if(stance<ledges[support].x-12)stance=ledges[support].x-12;
  if(stance>ledges[support].x+ledges[support].w-4)stance=ledges[support].x+ledges[support].w-4;
  if(stance<0)stance=0;if(stance>144)stance=144;
  if(!walk_to(stance))return 0;
  if(pitu.facing==machines[j].dir && !run(machines[j].dir?1:2))return 0;
  for(n=0;machines[j].live && n<450;n++)if(!run(0))return 0;
  if(machines[j].live)return 0;
 }
 if(!travel(5)||!walk_to(44))return 0;
 return mode==(stage==23?MODE_WIN:MODE_CLEAR);
}
static int solve(void){
 unsigned arena,delay,begin,t;u8 last=0;
 recorded=1;recording[0]=INPUT_ACTION;
 for(arena=0;arena<24;arena++){
  begin=recorded;
  for(delay=0;delay<1800;delay++){
   /* Offline search only. The chosen tape is replayed from cold game init below. */
   input_reset();load_stage(arena,0);recorded=begin;strategy=delay;
   if(solve_arena(0))break;
  }
  if(delay==1800){fprintf(stderr,"FAIL no solution arena %u\n",arena+1);return 1;}
  fprintf(stderr,"FOUND arena %u ticks=%u delay=%u lives=%u\n",arena+1,recorded-begin,delay,lives);
  if(arena<23){run(0);run(INPUT_ACTION);}
 }
 /* No state edits or stage skips from this point: execute every recorded key. */
 input_reset();load_stage(0,1);
 for(t=0;t<recorded;t++) {
  step(recording[t]);
  assert(mode!=MODE_HURT && !pitu.physics_error);
  assert(stage==last || stage==last+1);
  if(stage!=last){fprintf(stderr,"VERIFIED completed arena %u at tick %u\n",last+1,t);last=stage;}
 }
 assert(stage==23 && mode==MODE_WIN);
 FILE* out=fopen("build/campaign-inputs.bin","wb");assert(out);fwrite(recording,1,recorded,out);fclose(out);
 fprintf(stderr,"PASS actual game from menu through all 24 arenas to WIN: %u input ticks, score=%u\n",recorded,score);return 0;
}


static void test_swept_seal_contract(void){
 unsigned i,seals; u8 machine_xb;
 input_reset();load_stage(0,0);played_count=0;
 set_hostile_paper(0,76,172,0);step(INPUT_ACTION);
 assert(papers[0].live&&papers[0].returned&&papers[0].dir==1);
 assert(seal_ticks==BH2_SEAL_WINDOW_TICKS-1&&
        seal_cooldown==BH2_SEAL_WINDOW_TICKS+BH2_SEAL_RECOVERY_TICKS&&lives==2);
 for(i=0;i<BH2_SEAL_WINDOW_TICKS-2;i++){step(0);assert(seal_ticks>0);}
 step(0);assert(seal_ticks==0);
 for(i=0;i<BH2_SEAL_RECOVERY_TICKS-1;i++)step(0);
 assert(seal_cooldown==2);
 step(0);assert(seal_cooldown==1);
 step(INPUT_ACTION);assert(seal_cooldown==BH2_SEAL_WINDOW_TICKS+BH2_SEAL_RECOVERY_TICKS&&
                             seal_ticks==BH2_SEAL_WINDOW_TICKS-1);
 for(i=0;i<20;i++)step(INPUT_ACTION);
 assert(seal_ticks==0);
 seals=0;{unsigned returns=0;for(i=0;i<played_count;i++){
  seals+=played_audio[i]==AUDIO_EVENT_SEAL;
  returns+=played_audio[i]==AUDIO_EVENT_RETURN;
 }assert(seals==1&&returns==1);} /* success replaces the soft start cue */

 input_reset();load_stage(0,0);
 seal_ticks=6;set_hostile_paper(0,30,172,0);paper_player_contact(&papers[0],0);
 assert(!papers[0].returned); /* behind Pitu */
 set_hostile_paper(0,76,140,0);paper_player_contact(&papers[0],0);
 assert(!papers[0].returned); /* above the seal volume */
 set_hostile_paper(0,76,172,1);paper_player_contact(&papers[0],0);
 assert(!papers[0].returned); /* travelling away from the facing */

 input_reset();load_stage(0,0);pitu.facing=1;seal_ticks=6;
 set_hostile_paper(0,74,172,0); /* exact seal/body edge tie */
 assert(paper_player_contact(&papers[0],0));
 assert(papers[0].returned&&lives==2&&mode==MODE_PLAY);

 input_reset();load_stage(0,0);
 papers[0].live=1;papers[0].returned=1;papers[0].state=PROJECTILE_RETURNED;
 papers[0].dir=machines[0].dir?0:1;papers[0].y=172;
 papers[0].prev_xq=machines[0].dir?(machines[0].x+14)*2+12:machines[0].x*2-12;
 papers[0].xq=machines[0].dir?(machines[0].x+14)*2:machines[0].x*2;
 machine_xb=(u8)(machines[0].x>>1);
 for(i=0;i<17;i++){
  memset(ptr_bg(machine_xb,(u8)(167+i)),0x5A,7);
  memset(ptr_vram(machine_xb,(u8)(167+i)),0x00,7);
 }
 assert(paper_world_contact(&papers[0],0));
 assert(!machines[0].live&&!papers[0].live); /* swept through copier mouth */
 for(i=0;i<17;i++)assert(!memcmp(ptr_bg(machine_xb,(u8)(167+i)),ptr_vram(machine_xb,(u8)(167+i)),7));

 input_reset();load_stage(0,0);machines[0].live=0;papers[0].live=1;
 papers[0].returned=1;papers[0].state=PROJECTILE_RETURNED;papers[0].dir=1;
 papers[0].y=182;papers[0].prev_xq=100;papers[0].xq=120;
 assert(paper_world_contact(&papers[0],0));
 assert(!machines[0].live&&!papers[0].live); /* solid floor consumes the paper */

 input_reset();load_stage(0,0);
 set_hostile_paper(0,76,172,0);set_hostile_paper(1,78,172,0);
 step(INPUT_ACTION);
 assert(papers[0].returned&&papers[1].returned&&lives==2);
 input_reset();load_stage(0,0);played_count=0;
 set_hostile_paper(0,76,172,0);set_hostile_paper(1,60,172,0);
 step(INPUT_ACTION);
 assert(papers[0].returned&&!papers[1].live&&lives==1);
 assert(played_count==1&&played_audio[0]==AUDIO_EVENT_DAMAGE);
 puts("PASS D01-D05: seal window/recovery, direction, swept tie, mouth and simultaneous papers");
}

static void test_arena_flow_contracts(void) {
 unsigned i, reset;
 /* F01: enemy and paper overlap on the same tick; they consume one life.
    The impact tick and exactly 49 following ticks are protected. */
 input_reset(); load_stage(0,0); lives=2; alberto_active=1;
 alberto_xq=(i16)(player_x*2); alberto_dir=0;
 set_hostile_paper(0,(int16_t)(player_x*2+6),160,1);
 step(0);
 assert(lives==1 && hurt_ticks==50);
 for(i=0;i<49;i++) step(0);
 assert(lives==1 && hurt_ticks==1);
 set_hostile_paper(0,(int16_t)(player_x*2+6),160,1);
 step(0);
 assert(lives==0 && hurt_ticks==50 && mode==MODE_HURT);

 /* F02: holding action after death cannot retry; release then press can. */
 step(INPUT_ACTION); assert(mode==MODE_HURT && lives==0);
 for(i=0;i<20;i++) step(INPUT_ACTION);
 assert(mode==MODE_HURT);
 step(0); assert(mode==MODE_HURT);
 step(INPUT_ACTION);
 assert(mode==MODE_PLAY && lives==2 && score==0 && player_x==24);
 for(i=0;i<PROJECTILE_POOL_SIZE;i++) assert(!papers[i].live && papers[i].state==PROJECTILE_FREE);

 /* F03: final machine wins the tick over simultaneous Pitu damage and
    clears every hostile/reserved slot before damage is committed. */
 input_reset(); load_stage(0,0); lives=2;
 set_hostile_paper(0,(int16_t)(player_x*2+6),160,1);
 papers[1].state=PROJECTILE_RESERVED;
 papers[1].live=0;
 papers[2].state=PROJECTILE_RETURNED; papers[2].live=1; papers[2].returned=1;
 /* Stage 1 now opens with its copier facing away from Pitu, so this fixture
    approaches the copier from the right when checking clear-priority logic. */
 papers[2].dir=machines[0].dir ? 0 : 1; papers[2].y=172;
 papers[2].prev_xq=machines[0].dir?(machines[0].x+14)*2+12:machines[0].x*2-12;
 papers[2].xq=machines[0].dir?(machines[0].x+14)*2:machines[0].x*2;
 step(0);
 assert(!machines[0].live && lives==2 && score==500);
 assert(mode==MODE_PLAY && pitu.grounded); /* exit still needs entering */
 for(i=0;i<PROJECTILE_POOL_SIZE;i++) assert(!papers[i].live && papers[i].state==PROJECTILE_FREE);
 player_x=44; player_xq=44*PLAYER_Q_ONE; pitu.support_id=5; pitu.grounded=1;
 update_papers(); assert(mode==MODE_CLEAR);

 /* F04: machine pays once; retry restores checkpoint score and machine. */
 input_reset(); load_stage(0,0); score=0; stage_score_base=0;
 seal_ticks=6; set_hostile_paper(0,76,172,0); step(INPUT_ACTION);
 assert(papers[0].returned && score==25);
 /* A machine pays once, then its inactive shell cannot pay again. */
 load_stage(0,0);
 papers[0].state=PROJECTILE_RETURNED; papers[0].live=1; papers[0].returned=1;
 papers[0].dir=machines[0].dir ? 0 : 1; papers[0].y=172;
 papers[0].prev_xq=machines[0].dir?(machines[0].x+14)*2+12:machines[0].x*2-12;
 papers[0].xq=machines[0].dir?(machines[0].x+14)*2:machines[0].x*2;
 assert(paper_world_contact(&papers[0],0)); assert(score==500);
 papers[0].state=PROJECTILE_RETURNED; papers[0].live=1; papers[0].returned=1;
 papers[0].dir=machines[0].dir ? 0 : 1; papers[0].y=172;
 papers[0].prev_xq=machines[0].dir?(machines[0].x+14)*2+12:machines[0].x*2-12;
 papers[0].xq=machines[0].dir?(machines[0].x+14)*2:machines[0].x*2;
 assert(!paper_world_contact(&papers[0],0)); assert(score==500);
 /* A separate interrupted attempt restores its checkpoint on retry. */
 input_reset(); load_stage(0,0); score=25; stage_score_base=0;
 lives=1; set_hostile_paper(1,(int16_t)(player_x*2+6),160,1); step(0);
 assert(mode==MODE_HURT && score==25);
 step(INPUT_ACTION); step(0); step(INPUT_ACTION);
 assert(mode==MODE_PLAY && score==0 && machines[0].live && lives==2);

 /* F05: resetting during warning, seal recovery and airborne motion drops
    reservations, projectiles, timers, and transient player physics. */
 input_reset(); load_stage(0,0); machines[0].wait=0; update_machines();
 assert(machines[0].state==MACHINE_WARNING && machines[0].reserved_slot!=PROJECTILE_NO_SLOT);
 seal_cooldown=7; seal_ticks=3; hurt_ticks=9;
 pitu.grounded=0; pitu.support_id=255; vyq=-200; pitu.yq=140*PLAYER_Q_ONE;
 load_stage(0,0);
 assert(mode==MODE_PLAY && score==0 && lives==2 && player_x==24 && player_y==152);
 assert(pitu.grounded && pitu.support_id==0 && vyq==0);
 assert(!seal_cooldown && !seal_ticks && !hurt_ticks);
 for(i=0;i<PROJECTILE_POOL_SIZE;i++) assert(!papers[i].live && papers[i].state==PROJECTILE_FREE);
 assert(machines[0].state==MACHINE_IDLE && machines[0].reserved_slot==PROJECTILE_NO_SLOT);
 /* Repeat the actual in-RAM retry path 100 times from warning, active seal,
    and airborne player states. */
 for(reset=0;reset<100;reset++) {
  input_reset(); load_stage(0,0); machines[0].wait=0; update_machines();
  assert(machines[0].state==MACHINE_WARNING && machines[0].reserved_slot!=PROJECTILE_NO_SLOT);
  seal_ticks=3; seal_cooldown=8; pitu.grounded=0; pitu.support_id=255;
  vyq=-180; pitu.yq=145*PLAYER_Q_ONE; lives=1;
  set_hostile_paper(1,(int16_t)(player_x*2+6),160,1); step(0);
  assert(mode==MODE_HURT);
  step(INPUT_ACTION); assert(mode==MODE_HURT);
  step(0); step(INPUT_ACTION);
  assert(mode==MODE_PLAY && lives==2 && score==0 && pitu.grounded);
  assert(!hurt_ticks && !seal_ticks && !seal_cooldown && !papers[1].live);
  assert(machines[0].state==MACHINE_IDLE && machines[0].reserved_slot==PROJECTILE_NO_SLOT);
 }
 puts("PASS F01-F05: one hit/tick, exact recovery, release-press retry, completion priority, checkpoint reset");
}

static void test_opening_is_reaction_window(void) {
 unsigned i;
 input_reset(); load_stage(0,0);
 assert(player_x==24 && machines[0].x>=100);
 assert(machines[0].dir==FACING_RIGHT);
 assert(machines[0].wait==FIRST_ARENA_OPENING_WAIT);
 assert(machines[0].warning_ticks==FIRST_ARENA_OPENING_WARNING);
 assert(machines[0].period==FIRST_ARENA_PERIOD);
 for(i=0;i<FIRST_ARENA_OPENING_WAIT;i++) update_machines();
 assert(machines[0].state==MACHINE_IDLE && !papers[0].live);
 update_machines();
 assert(machines[0].state==MACHINE_WARNING && !papers[0].live);
 for(i=0;i<FIRST_ARENA_OPENING_WARNING;i++) update_machines();
 assert(machines[0].state==MACHINE_FIRE && !papers[0].live);
 update_machines();
 assert(papers[0].live && papers[0].dir==FACING_RIGHT);
 assert(papers[0].xq>(u16)(player_x*2));
 for(i=0;i<10;i++) { step(0); assert(lives==2); }
 puts("PASS opening: distant copier, 140-tick delay, visible 35-tick warning, 112-tick interval");
}

static void test_first_arena_rightward_approach_survives(void) {
 unsigned i;
 input_reset(); load_stage(0,0);
 /* Match the observed CPC input: walk right, jump, then take time to read
    the first incoming paper. This used to spend both lives on the opening. */
 for(i=0;i<45;i++) step(INPUT_RIGHT);
 for(i=0;i<11;i++) step(INPUT_JUMP);
 for(i=0;i<250;i++) step(0);
 assert(mode==MODE_PLAY && lives==2);
 puts("PASS opening gameplay: a normal right+short-jump approach stays alive through the first shot");
}

static void tests(void){
 unsigned i,t;PlayerState before;u16 tick_before;
 audio_init();
 input_reset();load_stage(0,0);
 set_hostile_paper(0,76,172,0);step(INPUT_ACTION);
 assert(papers[0].returned && papers[0].dir==1);
 input_reset();load_stage(0,0);pitu.facing=0;
 set_hostile_paper(0,42,172,1);step(INPUT_ACTION);
 assert(papers[0].returned && papers[0].dir==0);
 for(i=0;i<24;i++) {
  load_stage(i,0);machines[0].wait=0;update_machines();
  if(i==0)assert(machines[0].state==MACHINE_WARNING &&
                  machines[0].reserved_slot<PROJECTILE_POOL_SIZE);
  else assert(machines[0].state==MACHINE_IDLE && machines[0].wait>0 &&
              papers[0].live);
 }
 input_reset();load_stage(0,0);set_hostile_paper(0,312,172,1);update_papers();assert(!papers[0].live);
 set_hostile_paper(0,0,172,0);update_papers();assert(!papers[0].live);
 input_reset();load_stage(0,0);before=pitu;tick_before=ticks;
 step(INPUT_PAUSE);for(i=0;i<20;i++)step(0);
 assert(mode==MODE_PAUSE && ticks==tick_before && !memcmp(&before,&pitu,sizeof(pitu)));
 step(INPUT_PAUSE);assert(mode==MODE_PLAY);
 input_reset();load_stage(0,0);lives=1;set_hostile_paper(0,60,160,1);step(0);assert(mode==MODE_HURT);
 step(INPUT_ACTION);assert(mode==MODE_HURT);step(0);step(INPUT_ACTION);
 assert(mode==MODE_PLAY&&lives==2&&player_x==24);
 for(i=0;i<4;i++)assert(!papers[i].live);
 puts("PASS directed combat, all stage cooldowns, clipping, pause, death and retry");
 input_reset();load_stage(0,1);menu_selection=1;host_key_d=1;step(0);host_key_d=0;
 for(t=1;t<DEMO_TICKS;t++){
  step(0);game_present();
  assert(mode!=MODE_HURT && !pitu.physics_error && player_x<=144 && player_y<=152);
 }
 assert(stage==23&&mode==MODE_WIN&&score==36375);
 for(i=0;i<24;i++)assert(validation_state[8+i]==1);
 assert(validation_state[36]==0 && (validation_state[6]+256*validation_state[7])==DEMO_TICKS);
 assert(demo_index==sizeof(demo_inputs)&&demo_remaining==0);
 step(0);assert(!demo_active);
 step(INPUT_ACTION);assert(stage==0&&mode==MODE_PLAY&&score==0&&lives==2);
 puts("PASS SAME runtime demo decoder: menu -> 24 arenas -> WIN -> new game; no state edits during replay");
 input_reset();load_stage(0,0);played_count=0;
 for(i=0;i<24;i++)step(INPUT_JUMP);
 {unsigned jumps=0;for(i=0;i<played_count;i++)jumps+=played_audio[i]==AUDIO_EVENT_JUMP;assert(jumps==1);}
 input_reset();load_stage(0,0);played_count=0;step(INPUT_ACTION);
 assert(played_count==1&&played_audio[0]==AUDIO_EVENT_SEAL);
 input_reset();load_stage(0,0);played_count=0;step(INPUT_RIGHT|INPUT_JUMP);
 {u8 start_x=player_x;for(i=0;i<12;i++)step(INPUT_RIGHT);assert(player_x>start_x+5);}
 input_reset();load_stage(0,0);played_count=0;
 for(i=0;i<30;i++)step(INPUT_RIGHT);
 {unsigned steps=0;for(i=0;i<played_count;i++)steps+=played_audio[i]==AUDIO_EVENT_STEP;assert(steps>=1&&steps<=3);}
 input_reset();load_stage(0,0);played_count=0;pitu.grounded=0;pitu.support_id=255;pitu.yq=(FLOOR_Y-33)*PLAYER_Q_ONE;vyq=256;
 step(0);assert(pitu.grounded&&played_count&&played_audio[played_count-1]==AUDIO_EVENT_LAND);
 input_reset();load_stage(0,0);played_count=0;step(INPUT_JUMP);step(INPUT_PAUSE);step(INPUT_RIGHT);
 assert(mode==MODE_PAUSE&&pitu.x==24&&played_count==1&&played_audio[0]==AUDIO_EVENT_JUMP);
 step(INPUT_PAUSE);step(INPUT_RIGHT);assert(mode==MODE_PLAY&&pitu.xq>24*PLAYER_Q_ONE);
 played_count=0;audio_request(AUDIO_EVENT_JUMP);input_reset();load_stage(0,0);audio_tick();
 assert(played_count==0&&score==0&&lives==2&&papers[0].live==0);
 puts("PASS audio events: held jump once, grounded footsteps, landing, pause silence and RAM retry");
}
int main(int argc,char**argv){
 if(argc>1 && !strcmp(argv[1],"trace")){
  FILE* f=fopen("build/host-trace.bin","wb"); input_reset();load_stage(0,1);host_key_d=1;
  for(int t=0;t<150;t++){step(0);host_key_d=0;fwrite(&pitu,1,8,f);}
  fclose(f);return 0;
 }
 if(argc>1)return solve();test_swept_seal_contract();test_arena_flow_contracts();
 test_opening_is_reaction_window();test_first_arena_rightward_approach_survives();tests();return 0;
}
