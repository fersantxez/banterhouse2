#include <cpctelera.h>
#include <stdint.h>
#include "core/player.h"
#include "core/collision.h"
#include "core/machine.h"
#include "core/projectile.h"
#include "game/flow.h"
#include "platform/clock.h"
#include "platform/clock_logic.h"
#include "platform/audio.h"
#include "platform/input.h"
#include "platform/telemetry.h"

#define SCR_X_MAX 159
#define FLOOR_Y 184
#define BG_MEM ((u8*)0x8000)
#define FACING_LEFT 0
#define FACING_RIGHT 1
#define MODE_TITLE 0
#define MODE_PLAY 1
#define MODE_HURT 2
#define MODE_CLEAR 3
#define MODE_WIN 4
#define MODE_PAUSE 5
#define MODE_CONTROLS 6
#define MODE_DISK_ERROR 7
#define CAMPAIGN_SCREENS 24
#define CHAPTER_SCREENS 6
/* Keep the opening copier far enough from spawn that a player can move
 * before the first paper reaches them. The 50 Hz first threat appears at
 * 3.5 seconds, then the wider interval gives the player room to learn it. */
#define FIRST_ARENA_OPENING_WAIT 140
#define FIRST_ARENA_OPENING_WARNING 35
#define FIRST_ARENA_PERIOD 112
#ifndef BH2_SEAL_WINDOW_TICKS
#define BH2_SEAL_WINDOW_TICKS 6
#endif
#ifndef BH2_SEAL_RECOVERY_TICKS
#define BH2_SEAL_RECOVERY_TICKS 8
#endif

extern const u8 copier_even[], copier_odd[];
extern const u8 bg1[], bg2[], bg3[], bg4[];
extern const u8 palette1[], palette2[], palette3[], palette4[];
extern const u8 pitu_r_0[], pitu_r_1[], pitu_l_0[], pitu_l_1[];
extern const u8 pitu_walk_r_0[], pitu_walk_r_1[], pitu_walk_l_0[], pitu_walk_l_1[];
extern const u8 alberto_r_0[], alberto_r_1[], alberto_l_0[], alberto_l_1[];
extern void zx0_from_c(const u8* source, u8* destination);
static const u8* pitu_pose(u8 moving);
static void draw_person(const u8* sprite, u8 x, u8 y, u8 is_alberto);

typedef Projectile Paper;
typedef PlayerPlatform Platform;
typedef struct { u8 x, ground, dir; } MachineStart;
typedef struct { u8 count, alberto; MachineStart machine[3]; } StageStart;
#include "generated/level_data.h"
#ifndef BH2_M1_ONLY
#include "generated/campaign_replay.h"
static u8 demo_active, demo_remaining, demo_mask, demo_previous;
static u16 demo_index, demo_tick_count;
/* Read-only evidence exported in SNA snapshots; never controls gameplay. */
volatile u8 validation_state[40];
#endif

#ifdef BH2_M1_ONLY
static const u8* const backgrounds[1] = { bg1 };
static const u8* const palettes[1] = { palette1 };
#elif !defined(BH2_STREAM_CHAPTERS)
static const u8* const backgrounds[4] = { bg1, bg2, bg3, bg4 };
static const u8* const palettes[4] = { palette1, palette2, palette3, palette4 };
#else
static const u8* const palettes[4] = { palette1, palette2, palette3, palette4 };
#endif

static Machine machines[MACHINE_POOL_SIZE];
static Paper papers[PROJECTILE_POOL_SIZE];
static u8 stage, mode, lives;
static ArenaFlow arena_flow;
static u8 seal_ticks, seal_cooldown, seal_hit_ticks, anim_ticks;
static u8 damage_candidate;
static u8 step_ticks;
static PlayerState pitu;
static i16 old_player_xq, old_player_yq;
static i16 alberto_xq;
static i16 old_alberto_xq;
#define player_x pitu.x
#define player_y pitu.y
#define facing pitu.facing
#define grounded pitu.grounded
#define jump_buffer pitu.jump_buffer
#define coyote pitu.coyote
#define jump_min_ticks pitu.jump_min_ticks
#define player_xq pitu.xq
#define player_yq pitu.yq
#define vxq pitu.vxq
#define vyq pitu.vyq
static u8 alberto_dir, pause_return;
static u16 score, stage_score_base, ticks, pause_ticks;
#define lives arena_flow.lives
#define hurt_ticks arena_flow.invulnerability_ticks
#define retry_armed arena_flow.retry_armed
static u8 alberto_active;
static u8 old_papers_live[4], old_papers_x[4], old_papers_y[4];
static u8 old_player_x, old_player_y, old_alberto_x, old_alberto_active;
static u8 fresh_background;
static u8 hud_stage = 255;
static u16 hud_score = 0xFFFF;
static u8 hud_lives, hud_active, overlay_mode, overlay_drawing;
static u8 menu_selection, menu_dirty, menu_music = 1;
static u8 previous_menu_m;
static u8 clock_started, retry_menu, disk_error;
#ifdef BH2_STREAM_CHAPTERS
extern u16 disk_prepare(void);
extern u16 disk_load_ch1(void);
extern u16 disk_load_ch2(void);
extern u16 disk_load_ch3(void);
extern u16 disk_load_ch4(void);
#endif
static u8* ptr_vram(u8 byte_x, u8 y);
static u8* ptr_bg(u8 byte_x, u8 y);
static void restore_box(u8 xbyte, u8 y, u8 width, u8 height);
static void fill_both(u8 xbyte, u8 y, u8 width, u8 height, u8 ink);
static void fill_screen_box(u8 xbyte, u8 y, u8 width, u8 height, u8 ink);
static void draw_machine_signal(u8 index, u8 on);
static u8 opening_machine_wait(void) { return FIRST_ARENA_OPENING_WAIT; }
static u8 opening_machine_warning(void) { return FIRST_ARENA_OPENING_WARNING; }
static const u8 menu_font[26][5] = {
   {7,5,7,5,5}, {6,5,6,5,6}, {7,4,4,4,7}, {6,5,5,5,6}, {7,4,6,4,7},
   {7,4,6,4,4}, {7,4,5,5,7}, {5,5,7,5,5}, {7,2,2,2,7}, {3,1,1,5,7},
   {5,5,6,5,5}, {4,4,4,4,7}, {5,7,7,5,5}, {5,7,7,7,5}, {7,5,5,5,7},
   {7,5,7,4,4}, {7,5,7,1,1}, {6,5,6,5,5}, {7,4,7,1,7}, {7,2,2,2,2},
   {5,5,5,5,7}, {5,5,5,5,2}, {5,5,7,7,5}, {5,5,2,5,5}, {5,5,2,2,2},
   {7,1,2,4,7}
};

static void draw_menu_text(u8 xbyte, u8 y, const char* text, u8 ink) {
   u8 i = 0, row;
   while (text[i]) {
      char ch = text[i++];
      u8 col = 0;
      if (ch >= 'A' && ch <= 'Z') col = (u8)(ch - 'A');
      for (row = 0; row < 5; ++row) {
         u8 bits = (ch >= 'A' && ch <= 'Z') ? menu_font[col][row] : 0;
         u8 p0 = (bits & 4) ? ink : 0;
         u8 p1 = (bits & 2) ? ink : 0;
         u8 p2 = (bits & 1) ? ink : 0;
         u8* screen = ptr_vram((u8)(xbyte + i * 2 - 2), (u8)(y + row));
         screen[0] = cpct_px2byteM0(p0, p1);
         screen[1] = cpct_px2byteM0(p2, 0);
      }
   }
}

static void draw_menu_frame(void) {
   restore_box(12, 42, 56, 108);
   fill_screen_box(12, 42, 56, 108, 0);
   fill_screen_box(12, 42, 56, 1, 13);
   fill_screen_box(12, 149, 56, 1, 11);
   fill_screen_box(12, 42, 1, 108, 11);
   fill_screen_box(67, 42, 1, 108, 13);
}

static void draw_menu(void) {
   u8 row, selected = menu_selection;
   overlay_drawing = 1;
   draw_menu_frame();
   draw_menu_text(25, 51, "BANTERHOUSE", 10);
   draw_menu_text(34, 60, "DEVUELTO", 13);
   draw_menu_text(21, 75, selected == 0 ? "JUGAR" : "JUGAR", selected == 0 ? 11 : 1);
   draw_menu_text(21, 86, "CONTROLES", selected == 1 ? 11 : 1);
   draw_menu_text(21, 97, menu_music ? "MUSICA ON" : "MUSICA OFF", selected == 2 ? 11 : 1);
   for (row = 0; row < 3; ++row)
      if (row == selected) fill_screen_box(18, (u8)(73 + row * 11), 45, 9, 0);
   /* Draw selected text last so its highlight does not erase its glyphs. */
   draw_menu_text(21, 75, "JUGAR", selected == 0 ? 11 : 1);
   draw_menu_text(21, 86, "CONTROLES", selected == 1 ? 11 : 1);
   draw_menu_text(21, 97, menu_music ? "MUSICA ON" : "MUSICA OFF", selected == 2 ? 11 : 1);
   draw_menu_text(18, 119, "ESPACIO ELEGIR", 10);
#ifndef BH2_M1_ONLY
   draw_menu_text(18, 132, "D DEMO COMPLETA", 1);
#endif
   overlay_drawing = 0;
   menu_dirty = 0;
}

static void draw_controls(void) {
   overlay_drawing = 1;
   draw_menu_frame();
   draw_menu_text(27, 53, "CONTROLES", 11);
   draw_menu_text(18, 70, "FLECHAS MUEVEN", 1);
   draw_menu_text(18, 81, "ARRIBA SALTA", 1);
   draw_menu_text(18, 92, "ABAJO BAJA", 1);
   draw_menu_text(18, 103, "X DEVUELVE", 1);
   draw_menu_text(18, 114, "P PAUSA R REINICIA", 1);
   draw_menu_text(18, 130, "ESPACIO VOLVER", 10);
   overlay_drawing = 0;
   menu_dirty = 0;
}
static const u8 digit_rows[10][5] = {
   {7,5,5,5,7}, {2,6,2,2,7}, {7,1,7,4,7}, {7,1,7,1,7},
   {5,5,7,1,1}, {7,4,7,1,7}, {7,4,7,5,7}, {7,1,1,1,1},
   {7,5,7,5,7}, {7,5,7,1,7}
};

static u8 key(i16 k) { return cpct_isKeyPressed(k); }
static u8 screen_x(u8 byte_x, u8 y) {
   u8* p = cpct_getScreenPtr(CPCT_VMEM_START, byte_x, y);
   return (u8)(p - CPCT_VMEM_START);
}
static u8* ptr_vram(u8 byte_x, u8 y) { return cpct_getScreenPtr(CPCT_VMEM_START, byte_x, y); }
static u8* ptr_bg(u8 byte_x, u8 y) { return cpct_getScreenPtr(BG_MEM, byte_x, y); }

static void restore_box(u8 xbyte, u8 y, u8 width, u8 height) {
   u8 row;
   for (row = 0; row < height; ++row)
      cpct_memcpy(ptr_vram(xbyte, (u8)(y + row)), ptr_bg(xbyte, (u8)(y + row)), width);
}

static void fill_both(u8 xbyte, u8 y, u8 width, u8 height, u8 ink) {
   u8 pattern = cpct_px2byteM0(ink, ink);
   u8 row;
   for (row = 0; row < height; ++row)
      cpct_drawSolidBox(ptr_vram(xbyte, (u8)(y + row)), pattern, width, 1);
}

static void fill_screen_box(u8 xbyte, u8 y, u8 width, u8 height, u8 ink) {
   u8 pattern = cpct_px2byteM0(ink, ink);
   u8 row;
   for (row = 0; row < height; ++row)
      cpct_drawSolidBox(ptr_vram(xbyte, (u8)(y + row)), pattern, width, 1);
}

#ifdef BH2_STREAM_PROBE
/* N08-only border color records the last completed streaming stage. */
static void stream_probe_mark(u8 phase) {
   /* CPC hardware ink number, deliberately within GA's 0..26 colour range. */
   cpct_setBorder((u16)phase);
}
#endif

#ifdef BH2_STREAM_CHAPTERS
/* Restore AMSDOS's intercepted cassette calls after BASIC has RUN this BIN. */
static u8 disk_ready;
/* One background is resident per six-arena chapter. Keep it in RAM between
   arenas and retries; only a chapter boundary should touch AMSDOS again. */
static u8 resident_chapter;
/* The full-page background at &8000..&BFFF overwrites the firmware jumpblock.
   Preserve &BB00..&BFFF in the 6128's otherwise-unused RAM bank 7. */
static u8 firmware_jumpblock_cached;
extern void disk_cache_workspace_save(void);
extern void disk_cache_workspace_restore(void);
static u16 firmware_handler;
u8 disk_load_error;

#ifdef BH2_STACK_PROBE
/* N08-only marker for the reserved downward-growing stack guard. */
static void stack_probe_mark(void) {
   u8* guard = (u8*)0x7D60;
   u16 i;
   for (i = 0; i < 0x0100; ++i) guard[i] = 0xA5;
}
#ifdef BH2_STACK_PROBE_CHECKPOINTS
static void stack_probe_checkpoint(u8 phase) {
   u8* guard = (u8*)0x7D60;
   u16 i;
   for (i = 0; i < 0x0100; ++i) if (guard[i] != 0xA5) {
      validation_state[38] = phase;
      for (;;) { }
   }
}
#endif
#endif

static void disk_reinitialize(void) {
   /* Restore AMSDOS's full working area before reusing its disk entry points.
      Chapter underlays occupy &8000..&BFFF, not only the jumpblock itself. */
   if (firmware_jumpblock_cached) disk_cache_workspace_restore();
   /* CPCtelera leaves the upper ROM disabled for direct video RAM access.
      Map AMSDOS before restoring its interrupt vector. */
   cpct_enableUpperROM();
#ifdef BH2_STREAM_PROBE
   stream_probe_mark(8);
#endif
   cpct_reenableFirmware(firmware_handler);
#ifdef BH2_STREAM_PROBE
   stream_probe_mark(9);
#endif
   disk_ready = (u8)(disk_prepare() != 0);
#ifdef BH2_STREAM_PROBE
   stream_probe_mark(10);
#endif
   /* The firmware interrupt handler lives in the upper ROM. Restore the
      null handler before hiding that ROM, so no IRQ can jump into RAM. */
   firmware_handler = cpct_disableFirmware();
#ifdef BH2_STREAM_PROBE
   stream_probe_mark(11);
#endif
   cpct_disableUpperROM();
#ifdef BH2_STREAM_PROBE
   stream_probe_mark(12);
#endif
   /* Bank 7 is safe only while AMSDOS is hidden. Preserve the full workspace
      after every successful initialization so a later chapter can restore it. */
   if (disk_ready) {
      disk_cache_workspace_save();
      firmware_jumpblock_cached = 1;
   }
   disk_error = disk_ready ^ 1;
}

static u8 load_chapter_background(u8 chapter) {
   u16 loaded = 0;
   if (resident_chapter == chapter) {
      /* Restore the immutable chapter underlay and remove the previous
         arena's sprites, HUD and end-of-level panel. */
      cpct_memcpy(CPCT_VMEM_START, BG_MEM, 0x4000);
      return 1;
   }
   audio_music_pause();
#ifdef BH2_STREAM_PROBE
   stream_probe_mark(1);
#endif
   /* Keep the RAM-resident game IRQ installed while changing ROM mapping.
      clock_stop() restores the firmware handler immediately, which is unsafe
      while the upper ROM is currently hidden. The blocking disk read is
      followed by clock_init(), which resets any queued ticks. */
   /* The renderer's graphics pages replace AMSDOS workspace. Rebuild it once
      immediately before each read, while those pages are disposable. */
   disk_reinitialize();
#ifdef BH2_STREAM_PROBE
   stream_probe_mark(2);
#endif
   if (disk_ready) disk_error = 2;
   if (disk_ready) {
      cpct_enableUpperROM();
      cpct_reenableFirmware(firmware_handler);
#ifdef BH2_STREAM_PROBE
      stream_probe_mark(3);
#endif
      if (chapter == 0) loaded = disk_load_ch1();
      else if (chapter == 1) loaded = disk_load_ch2();
      else if (chapter == 2) loaded = disk_load_ch3();
      else if (chapter == 3) loaded = disk_load_ch4();
      firmware_handler = cpct_disableFirmware();
      cpct_disableUpperROM();
#ifdef BH2_STREAM_PROBE
      stream_probe_mark(4);
#endif
   }
   if (loaded) {
      /* Load compressed bytes to the clean-background page, expand to video,
         then preserve the expanded image as the restore page. */
      zx0_from_c(BG_MEM, CPCT_VMEM_START);
#ifdef BH2_STREAM_PROBE
      stream_probe_mark(5);
#endif
      cpct_memcpy(BG_MEM, CPCT_VMEM_START, 0x4000);
#ifdef BH2_STREAM_PROBE
      stream_probe_mark(6);
#endif
      /* The full-page background copy overlaps CPCtelera's firmware RAM
         (&A6FC-&BFFF). It is intentionally left clobbered until the next
         chapter read, when the background page can be reused as scratch. */
      disk_error = 0;
      resident_chapter = chapter;
   }
   if (clock_started) clock_init();
   audio_music_resume();
#ifdef BH2_STREAM_PROBE
   stream_probe_mark(7);
#endif
   return (u8)(loaded != 0);
}
#endif

static void draw_marker(u8 x, u8 y, u8 colour) {
   fill_both((u8)(x >> 1), y, 2, 3, colour);
}

static void draw_digit(u8 xbyte, u8 y, u8 digit) {
   u8 row;
   for (row = 0; row < 5; ++row) {
      u8 bits = digit_rows[digit][row];
      u8 p0 = (bits & 4) ? 1 : 0;
      u8 p1 = (bits & 2) ? 1 : 0;
      u8 p2 = (bits & 1) ? 1 : 0;
      u8* v = ptr_vram(xbyte, (u8)(y + row));
      v[0] = cpct_px2byteM0(p0, p1);
      v[1] = cpct_px2byteM0(p2, 0);
   }
}

static void draw_number(u8 xbyte, u8 y, u16 value, u8 digits) {
   u8 n, digit;
   static const u16 powers[5] = {10000, 1000, 100, 10, 1};
   for (n = 0; n < digits; ++n) {
      u16 place = powers[5 - digits + n];
      digit = 0;
      while (value >= place) { value -= place; ++digit; }
      draw_digit((u8)(xbyte + n * 2), y, digit);
   }
}

static void draw_hud(void) {
   u8 i, active = 0;
   for (i=0;i<3;++i) active += machines[i].live;
   if (hud_stage != stage || hud_score != score || hud_lives != lives || hud_active != active) {
      /* cpct_drawSolidBox supports at most 64 bytes per row. */
      fill_both(0, 0, 40, 12, 0);
      fill_both(40, 0, 40, 12, 0);
      draw_menu_text(1,3,"FASE",1); draw_number(10,3,(u16)(stage+1),2);
      draw_menu_text(21,3,"VIDA",3); draw_number(30,3,lives,1);
      draw_menu_text(38,3,"MAQ",11); draw_number(45,3,active,1);
#ifndef BH2_M1_ONLY
      if (demo_active) draw_menu_text(49,3,"DEMO",10);
#endif
      draw_number(59,3,score,5);
      hud_stage=stage; hud_score=score; hud_lives=lives; hud_active=active;
   }
   /* Door occupies logical x=42..53, directly above the top platform.
      It is a foreground marker and must survive sprite background restores. */
   fill_both(22,49,4,8,active ? 6 : 11);
}

static void load_stage(u8 n, u8 show_menu) {
   u8 i, chapter, chapter_start, local_stage;
   if (n == 0 || show_menu) score = stage_score_base = 0;
   else if (n == stage) score = stage_score_base;
   else stage_score_base = score;
   stage = n;
#ifdef BH2_M1_ONLY
   chapter = 0;
   chapter_start = 0;
   n = 0;
#else
   if (stage >= 18) { chapter = 3; chapter_start = 18; }
   else if (stage >= 12) { chapter = 2; chapter_start = 12; }
   else if (stage >= 6) { chapter = 1; chapter_start = 6; }
   else { chapter = 0; chapter_start = 0; }
#endif
   local_stage = (u8)(stage - chapter_start);
#ifdef BH2_STREAM_CHAPTERS
   retry_menu = show_menu;
   if (!load_chapter_background(chapter)) {
      mode = MODE_DISK_ERROR;
      fill_screen_box(0, 0, 64, 200, 0);
      fill_screen_box(64, 0, 16, 200, 0);
      if (disk_error == 1) draw_menu_text(14, 72, "ERROR AMSDOS", 6);
      else if (disk_load_error == 1) draw_menu_text(14, 72, "ERROR OPEN", 6);
      else if (disk_load_error == 2) draw_menu_text(14, 72, "ERROR READ", 6);
      else draw_menu_text(14, 72, "ERROR ARCHIVO", 6);
      draw_menu_text(9, 99, "ESPACIO REINTENTAR", 11);
      return;
   }
#else
   zx0_from_c(backgrounds[chapter], BG_MEM);
   cpct_memcpy(CPCT_VMEM_START, BG_MEM, 0x4000);
#endif
   cpct_setPalette((u8*)palettes[chapter], 16);
   player_xq = 24 * PLAYER_Q_ONE;
   player_yq = (FLOOR_Y - 32) * PLAYER_Q_ONE;
   player_x = 24;
   player_y = (u8)(FLOOR_Y - 32);
   vxq = vyq = 0;
   facing = FACING_RIGHT;
   grounded = 1;
   pitu.support_id = 0;
   pitu.ignore_surface_id = 255;
   pitu.physics_error = pitu.drop_ticks = 0;
   jump_buffer = coyote = jump_min_ticks = 0;
   step_ticks = 0;
   flow_attempt_reset(&arena_flow);
   seal_ticks = seal_cooldown = seal_hit_ticks = 0;
   damage_candidate = 0;
   ticks = 0;

   alberto_xq = (u16)(112 * 2);
   alberto_dir = 0;
   alberto_active = campaign[stage].alberto;
   machine_pool_reset(machines, papers);
   for (i = 0; i < MACHINE_POOL_SIZE; ++i) {
      if (i < campaign[stage].count)
         machine_init(&machines[i], campaign[stage].machine[i].x,
            campaign[stage].machine[i].ground,
            campaign[stage].machine[i].dir,
            (u8)((stage == 0 ? opening_machine_wait() : 68) + i * 19 + local_stage * 5),
            (u8)(stage == 0 ? opening_machine_warning() : 0),
            (u8)(stage == 0 ? FIRST_ARENA_PERIOD :
                 76 - (stage < 10 ? stage * 3 : 30)));
      if (machines[i].live) {
         u8 odd = machines[i].x & 1;
         const u8* sprite = odd ? copier_odd : copier_even;
         cpct_drawSpriteMasked((void*)sprite,ptr_vram(machines[i].x>>1,machines[i].y),7+odd,17);
      }
   }
   mode = show_menu ? MODE_TITLE : MODE_PLAY;
   menu_selection = 0;
   menu_dirty = 1;
   fresh_background = 1;
   audio_cancel();
   overlay_mode = 255;
   hud_stage = 255;
   hud_score = 0xFFFF;
   draw_hud();
   draw_person(pitu_pose(0), player_x, player_y, 0);
}

static void draw_person(const u8* sprite, u8 x, u8 y, u8 is_alberto) {
   u8 odd = x & 1;
   u8 xbyte = (u8)(x >> 1);
   u8 width = (u8)(8 + odd);
   const u8* pose = sprite;
   u8* dst = ptr_vram(xbyte, y);
   (void)is_alberto;
   cpct_drawSpriteMasked((void*)pose, dst, width, 32);
}

static const u8* pitu_pose(u8 moving) {
   if (moving) {
      if (facing) return (player_x & 1) ? pitu_walk_r_1 : pitu_walk_r_0;
      return (player_x & 1) ? pitu_walk_l_1 : pitu_walk_l_0;
   }
   if (facing) return (player_x & 1) ? pitu_r_1 : pitu_r_0;
   return (player_x & 1) ? pitu_l_1 : pitu_l_0;
}

static const u8* alberto_pose(void) {
   u8 x = (u8)(alberto_xq >> 1);
   if (alberto_dir) return (x & 1) ? alberto_r_1 : alberto_r_0;
   return (x & 1) ? alberto_l_1 : alberto_l_0;
}

static void draw_paper(Paper* p) {
   u8 x = (u8)(p->xq >> 1);
   u8 xb = (u8)(x >> 1);
   u8 colour = p->returned ? 11 : 15;
   u8 a = cpct_px2byteM0(0, colour);
   u8 b = cpct_px2byteM0(colour, colour);
   u8* d;
   u8 i;
   for (i = 0; i < 4; ++i) {
      d = ptr_vram(xb, (u8)(p->y + i));
      if (i == 0) { d[0] = a; d[1] = b; }
      else if (i == 1) { d[0] = b; d[1] = b; }
      else if (i == 2) { d[0] = b; d[1] = cpct_px2byteM0(colour, 0); }
      else { d[0] = b; d[1] = cpct_px2byteM0(0, 0); }
   }
}

static void capture_old_positions(void) {
   u8 i;
   old_player_x = player_x;
   old_player_y = player_y;
   old_player_xq = player_xq;
   old_player_yq = player_yq;
   old_alberto_x = (u8)(alberto_xq >> 1);
   old_alberto_xq = alberto_xq;
   old_alberto_active = alberto_active;
   for (i = 0; i < 4; ++i) {
      old_papers_live[i] = papers[i].live;
      old_papers_x[i] = (u8)(papers[i].xq >> 1);
      old_papers_y[i] = papers[i].y;
   }
}

static void restore_old_positions(void) {
   u8 i;
   restore_box((u8)(old_player_x >> 1), old_player_y, (u8)(8 + (old_player_x & 1)), 32);
   if (old_alberto_active) restore_box((u8)(old_alberto_x >> 1), (u8)(FLOOR_Y - 32),
                               (u8)(8 + (old_alberto_x & 1)), 32);
   for (i = 0; i < 4; ++i) if (old_papers_live[i])
      restore_box((u8)(old_papers_x[i] >> 1), old_papers_y[i], 2, 4);
}

static void draw_all(u8 moving) {
   u8 i;
   draw_hud();
   if (mode == MODE_PLAY || mode == MODE_PAUSE || mode == MODE_CLEAR || mode == MODE_WIN) {
      /* The chapter background stays immutable. Redraw machines after moving
         sprites restore their old boxes, preserving shells and warning lamps. */
      for (i = 0; i < MACHINE_POOL_SIZE; ++i) if (machines[i].live)
         draw_machine_signal(i, (u8)(machines[i].state == MACHINE_WARNING));
      if (!hurt_ticks || (ticks & 4)) draw_person(pitu_pose(moving), player_x, player_y, 0);
   }
   if (mode == MODE_HURT && (ticks & 4)) draw_person(pitu_pose(0), player_x, player_y, 0);
   if (alberto_active && mode != MODE_WIN && mode != MODE_TITLE && mode != MODE_CONTROLS)
      draw_person(alberto_pose(), (u8)(alberto_xq >> 1), (u8)(FLOOR_Y - 32), 1);
   for (i = 0; i < 4; ++i) if (papers[i].live) draw_paper(&papers[i]);
   if (seal_ticks) fill_screen_box((player_x+(facing?12:0))>>1,player_y+17,2,5,
                                    seal_hit_ticks ? 3 : 11);
   if (mode == MODE_TITLE && menu_dirty) draw_menu();
   else if (mode == MODE_CONTROLS && menu_dirty) draw_controls();
}

static void draw_machine_signal(u8 index, u8 on) {
   Machine *m = &machines[index];
   u8 odd = m->x & 1;
   const u8 *sprite = odd ? copier_odd : copier_even;
   u8 xbyte = m->x >> 1;
   /* Redraw the fixed shell; only the warning lamp changes. */
   cpct_drawSpriteMasked((void*)sprite, ptr_vram(xbyte, m->y), 7 + odd, 17);
   if (on) fill_screen_box((u8)(xbyte + 5), (u8)(m->y + 2), 1, 2, 3);
}

static void update_player(u8 left, u8 right, u8 jump, u8 jump_held, u8 down) {
   PlayerInput input;
   u8 was_grounded = grounded;
   u8 old_x = player_x;
   input.left = left; input.right = right; input.jump_pressed = jump;
   input.jump_held = jump_held; input.down = down;
   if (player_step(&pitu, input, ledges, 6)) audio_request(AUDIO_EVENT_JUMP);
   if (!was_grounded && grounded) audio_request(AUDIO_EVENT_LAND);
   else if (grounded && player_x != old_x) {
      if (++step_ticks >= 10) {
         step_ticks = 0;
         audio_request(AUDIO_EVENT_STEP);
      }
   } else if (!grounded) step_ticks = 0;
}

static u8 overlap(u8 a, u8 aw, u8 b, u8 bw) { return a < b + bw && b < a + aw; }

/* The 24-screen demo is a legacy campaign fixture; keep its original timing. */
static void legacy_check_seal(void) {
   u8 i;
   for (i = 0; i < PROJECTILE_POOL_SIZE; ++i) if (seal_ticks && papers[i].live && !papers[i].returned) {
      u8 px = (u8)(papers[i].xq >> 1);
      u8 front = facing ? (u8)(player_x + 13) : (u8)(player_x > 5 ? player_x - 5 : 0);
      if (papers[i].y + 4 > player_y + 12 && papers[i].y < player_y + 26 &&
          overlap(px, 4, front, 8)) {
         projectile_mark_returned(&papers[i], facing);
         papers[i].xq += facing ? 8 : -8;
         score += 25;
         audio_request(AUDIO_EVENT_RETURN);
      }
   }
}

static int16_t paper_to_world_q(int16_t xq) { return (int16_t)(xq * 64); }

static u8 paper_player_contact(Paper *p, u8 index) {
   int16_t px0 = paper_to_world_q(p->prev_xq);
   int16_t px1 = paper_to_world_q(p->xq);
   int16_t py = (int16_t)(p->y * 128);
   int16_t bx0 = (int16_t)(old_player_xq + 3 * 128);
   int16_t bx1 = (int16_t)(pitu.xq + 3 * 128);
   int16_t by0 = (int16_t)(old_player_yq + 4 * 128);
   int16_t by1 = (int16_t)(pitu.yq + 4 * 128);
   uint16_t body_time = 0, seal_time = 0;
   u8 body_hit, seal_hit = 0;
   body_hit = collision_sweep_aabb(px0, py, px1, py, 4 * 128, 4 * 128,
      bx0, by0, bx1, by1, 10 * 128, 28 * 128, &body_time);
   if (seal_ticks && p->dir != facing) {
      int16_t offset = facing ? 13 * 128 : -5 * 128;
      int16_t sx0 = (int16_t)(old_player_xq + offset);
      int16_t sx1 = (int16_t)(pitu.xq + offset);
      int16_t sy0 = (int16_t)(old_player_yq + 17 * 128);
      int16_t sy1 = (int16_t)(pitu.yq + 17 * 128);
      seal_hit = collision_sweep_aabb(px0, py, px1, py, 4 * 128, 4 * 128,
         sx0, sy0, sx1, sy1, 8 * 128, 5 * 128, &seal_time);
   }
   if (seal_hit && (!body_hit || seal_time <= body_time)) {
      p->xq = collision_interpolate_q16(p->prev_xq, p->xq, seal_time);
      projectile_mark_returned(p, facing);
      p->bounced = 1;
      seal_hit_ticks = 2;
      score += 25;
      audio_request(AUDIO_EVENT_RETURN);
      return 1;
   }
   if (body_hit && !hurt_ticks) {
      projectile_release(papers, index);
      damage_candidate = 1;
      return 1;
   }
   return 0;
}

static u8 paper_world_contact(Paper *p, u8 index) {
   uint8_t i, best_id = 255;
   uint16_t best_time = 65535, time;
   int16_t px0 = paper_to_world_q(p->prev_xq);
   int16_t px1 = paper_to_world_q(p->xq);
   int16_t py = (int16_t)(p->y * 128);
   u8 have_hit = 0, hit_solid = 0;
   for (i = 0; i < MACHINE_POOL_SIZE; ++i) if (machines[i].live) {
      Machine *m = &machines[i];
      int16_t mx = (int16_t)((m->dir ? m->x + m->w - 4 : m->x) * 128);
      int16_t my = (int16_t)((m->ground - 12) * 128);
      if (collision_sweep_aabb(px0, py, px1, py, 4 * 128, 4 * 128,
            mx, my, mx, my, 4 * 128, 4 * 128, &time) &&
          (!have_hit || time < best_time)) {
         have_hit = 1;
         hit_solid = 0;
         best_time = time;
         best_id = i;
      }
   }
   for (i = 0; i < 6; ++i) if (ledges[i].kind == PLAYER_SURFACE_SOLID) {
      const PlayerPlatform *s = &ledges[i];
      if (collision_sweep_aabb(px0, py, px1, py, 4 * 128, 4 * 128,
            (int16_t)(s->x * 128), (int16_t)(s->y * 128),
            (int16_t)(s->x * 128), (int16_t)(s->y * 128),
            (int16_t)(s->w * 128), (int16_t)(s->h * 128), &time) &&
          (!have_hit || time < best_time)) {
         have_hit = 1;
         hit_solid = 1;
         best_time = time;
      }
   }
   if (have_hit) {
      if (!hit_solid) {
         Machine *m = &machines[best_id];
         machine_turn_off(m, papers);
         restore_box((u8)(m->x >> 1), m->y, 7, 17);
         score += 500;
         audio_request(AUDIO_EVENT_MACHINE);
      }
      projectile_release(papers, index);
      return 1;
   }
   return 0;
}

static void update_machines(void) {
   u8 i;
   for (i = 0; i < MACHINE_POOL_SIZE; ++i) if (machines[i].live) {
      MachineEvent event = machine_tick(&machines[i], papers);
      if (event == MACHINE_EVENT_WARNING) draw_machine_signal(i, 1);
      else if (event == MACHINE_EVENT_FIRED) draw_machine_signal(i, 0);
   }
}

static void update_papers(void) {
   u8 i, active = 0, completed = 0;
   uint16_t contact_time;
   damage_candidate = 0;
   for (i = 0; i < PROJECTILE_POOL_SIZE; ++i) if (papers[i].live) {
      Paper* p = &papers[i];
      projectile_tick(p, 3, 5);
      if ((p->xq < 0) || (p->xq > 312)) { projectile_release(papers, i); continue; }
      if (p->returned) {
         if (stage == 0) {
            if (paper_world_contact(p, i)) continue;
         } else {
            u8 j;
            for (j = 0; j < MACHINE_POOL_SIZE; ++j) if (machines[j].live &&
                p->y + 4 >= machines[j].ground - 13 && p->y <= machines[j].ground - 5 &&
                overlap((u8)(p->xq >> 1), 4, machines[j].x, machines[j].w)) {
               Machine *m = &machines[j];
               machine_turn_off(m, papers);
               restore_box((u8)(m->x >> 1), m->y, 7, 17);
               score += 500;
               audio_request(AUDIO_EVENT_MACHINE);
               projectile_release(papers, i);
               break;
            }
         }
         if (alberto_active && stage == 0 && collision_sweep_aabb(
               paper_to_world_q(p->prev_xq), (int16_t)(p->y * 128),
               paper_to_world_q(p->xq), (int16_t)(p->y * 128),
               4 * 128, 4 * 128,
               (int16_t)((old_alberto_xq >> 1) * 128),
               (FLOOR_Y - 32) * 128,
               (int16_t)((alberto_xq >> 1) * 128),
               (FLOOR_Y - 32) * 128,
               16 * 128, 32 * 128, &contact_time)) {
            projectile_release(papers, i);
            score += 100;
            alberto_active = 0;
         } else if (alberto_active && stage != 0 &&
             overlap((u8)(p->xq >> 1), 4, (u8)(alberto_xq >> 1), 16) &&
             p->y + 4 > FLOOR_Y - 32 && p->y < FLOOR_Y) {
            projectile_release(papers, i);
            score += 100;
            alberto_active = 0;
         }
      } else if (stage == 0) paper_player_contact(p, i);
      else if (!hurt_ticks &&
         overlap((u8)(p->xq >> 1), 4, (u8)(player_x + 3), 10) &&
         p->y + 4 > player_y + 4 && p->y < player_y + 32) {
         projectile_release(papers, i);
         damage_candidate = 1;
      }
   }
   for (i = 0; i < MACHINE_POOL_SIZE; ++i) active += machines[i].live;
   /* Turning off the final machine opens the exit and cancels every threat
      before damage is committed for this tick. */
   if (!active) {
      completed = 1;
      for (i = 0; i < MACHINE_POOL_SIZE; ++i) machine_turn_off(&machines[i], papers);
      projectile_pool_reset(papers);
      alberto_active = 0;
   }
   if (alberto_active && !hurt_ticks && collision_sweep_aabb(
         (int16_t)(old_player_xq + 3 * 128),
         (int16_t)(old_player_yq + 4 * 128),
         (int16_t)(pitu.xq + 3 * 128),
         (int16_t)(pitu.yq + 4 * 128), 10 * 128, 28 * 128,
         (int16_t)((old_alberto_xq >> 1) * 128), (FLOOR_Y - 32) * 128,
         (int16_t)((alberto_xq >> 1) * 128), (FLOOR_Y - 32) * 128,
         16 * 128, 32 * 128, &contact_time)) damage_candidate = 1;
   if (!completed && damage_candidate && !hurt_ticks) {
      u8 died = flow_hit(&arena_flow);
      audio_request(AUDIO_EVENT_DAMAGE);
      if (died) mode = MODE_HURT;
   }
   if (completed && player_x >= 40 && player_x <= 54 && grounded && pitu.support_id == 5)
      mode = stage == CAMPAIGN_SCREENS-1 ? MODE_WIN : MODE_CLEAR;
}

static void game_tick(void) {
   InputFrame input;
   u8 left, right, jump, jump_held, down, action, pressed;
   u8 prior_mode = mode;
   input_sample(&input);
#ifndef BH2_M1_ONLY
   if (demo_active && (input.pressed & INPUT_RESTART)) {
      demo_active=0; load_stage(0,1); return;
   }
#ifndef BH2_M1_ONLY
   if (!demo_active && mode==MODE_TITLE && key(Key_D)) {
      u8 i;
      menu_selection=0;
      demo_active=1; demo_index=0; demo_remaining=0; demo_previous=0; demo_tick_count=0;
      for(i=0;i<40;++i) validation_state[i]=0;
      validation_state[0]=0xB2; validation_state[1]=1; validation_state[2]=1;
   }
#endif
   if (demo_active) {
      if (!demo_remaining && demo_index < sizeof(demo_inputs)) {
         demo_remaining=demo_inputs[demo_index++];
         demo_mask=demo_inputs[demo_index++];
      }
      if (demo_remaining) {
         --demo_remaining;
         ++demo_tick_count;
         input.held=demo_mask;
         input.pressed=demo_mask & (u8)~demo_previous;
         input.released=demo_previous & (u8)~demo_mask;
         demo_previous=demo_mask;
      } else {
         demo_active=0; hud_stage=255;
      }
   }
#endif
   pressed = input.pressed;
   left = (input.held & INPUT_LEFT) != 0;
   right = (input.held & INPUT_RIGHT) != 0;
   jump = (input.pressed & INPUT_JUMP) != 0;
   jump_held = (input.held & INPUT_JUMP) != 0;
   down = (input.pressed & INPUT_DOWN) != 0;
   action = (input.pressed & INPUT_ACTION) != 0;
   capture_old_positions();
   if ((pressed & INPUT_PAUSE) && (mode == MODE_PLAY || mode == MODE_PAUSE)) {
      if (mode == MODE_PAUSE) {
         mode = pause_return;
         audio_music_resume();
      }
      else {
         pause_return = mode;
         mode = MODE_PAUSE;
         audio_cancel();
         audio_music_pause();
      }
   }
   if (mode == MODE_PAUSE) { ++pause_ticks; return; }
   /* Expirations happen before new contacts: a 50-tick grant protects the
      impact tick and the following 49 simulation ticks. */
   if (mode == MODE_PLAY) flow_tick(&arena_flow);
   if (mode == MODE_PLAY && seal_cooldown) --seal_cooldown;
   ++ticks;
   if (mode == MODE_DISK_ERROR) {
      if (action) load_stage(stage, retry_menu);
   } else if (mode == MODE_TITLE) {
      if (jump) { if (menu_selection) --menu_selection; menu_dirty = 1; }
      if (down) { if (menu_selection < 2) ++menu_selection; menu_dirty = 1; }
      if (key(Key_M) && !previous_menu_m) { menu_music = (u8)!menu_music; audio_music_toggle(); menu_dirty = 1; }
      if (action) {
         if (menu_selection == 0) {
            cpct_memcpy(CPCT_VMEM_START, BG_MEM, 0x4000);
            mode = MODE_PLAY;
            menu_dirty = 0;
            overlay_mode = 255;
            fresh_background = 1;
         }
         else if (menu_selection == 1) { mode = MODE_CONTROLS; menu_dirty = 1; }
         else { menu_music = (u8)!menu_music; audio_music_toggle(); menu_dirty = 1; }
      }
   } else if (mode == MODE_CONTROLS) {
      if (action || (pressed & 8)) { mode = MODE_TITLE; menu_dirty = 1; }
   } else if (mode == MODE_HURT) {
      if (flow_retry_input(&arena_flow, input.pressed, input.released, INPUT_ACTION))
         load_stage(stage, 0);
   } else if (mode == MODE_CLEAR) {
      if (action) {
#ifdef BH2_M1_ONLY
         load_stage(0, 0);
#else
         if (stage == CAMPAIGN_SCREENS - 1) mode = MODE_WIN; else load_stage((u8)(stage + 1), 0);
#endif
      }
   } else if (mode == MODE_WIN) {
      if (action) load_stage(0, 0);
   } else if (mode == MODE_PLAY) {
      if (pressed & INPUT_RESTART) { load_stage(stage, 0); return; }
      update_player(left, right, jump, jump_held, down);
      if (action && !seal_cooldown) {
         seal_ticks = stage == 0 ? BH2_SEAL_WINDOW_TICKS : 5;
         seal_cooldown = stage == 0 ? (BH2_SEAL_WINDOW_TICKS + BH2_SEAL_RECOVERY_TICKS) : 8;
         audio_request(AUDIO_EVENT_SEAL);
      }
      update_machines();
      if (stage != 0) legacy_check_seal();
      if (alberto_active) {
         if (alberto_dir) { if (alberto_xq < 276) alberto_xq += 2; else alberto_dir = 0; }
         else { if (alberto_xq > 8) alberto_xq -= 2; else alberto_dir = 1; }
      }
      update_papers();
      if (seal_ticks) --seal_ticks;
      if (seal_hit_ticks) --seal_hit_ticks;
   }
   if ((mode == MODE_CLEAR || mode == MODE_WIN) && prior_mode != mode)
      audio_request(AUDIO_EVENT_ARENA_CLEAR);
   previous_menu_m = key(Key_M);
}

#ifndef BH2_M1_ONLY
static void record_demo_evidence(void) {
   if (!demo_active) return;
      validation_state[3]=mode; validation_state[4]=stage; validation_state[5]=lives;
   validation_state[6]=(u8)demo_tick_count; validation_state[7]=(u8)(demo_tick_count>>8);
   if (mode==MODE_CLEAR || mode==MODE_WIN) validation_state[8+stage]=1;
   validation_state[32]=(u8)score; validation_state[33]=(u8)(score>>8);
   validation_state[34]=player_x; validation_state[35]=player_y;
   if (mode==MODE_HURT || pitu.physics_error) validation_state[36]=1;
}
#endif

/* Presentation reads the state produced by the fixed simulation tick. */
static void game_present(void) {
   if (mode == MODE_DISK_ERROR) return;
   if (mode == MODE_TITLE || mode == MODE_CONTROLS) {
      if (menu_dirty) {if (mode == MODE_TITLE) draw_menu(); else draw_controls();}
      return;
   }
   if (mode == MODE_PAUSE || mode == MODE_HURT || mode == MODE_CLEAR || mode == MODE_WIN) {
      if (overlay_mode != mode) {
         /* Rebuild the whole frame from the chapter underlay before drawing
            a modal panel. This removes any accumulated sprite/restore trails. */
         cpct_memcpy(CPCT_VMEM_START, BG_MEM, 0x4000);
#ifdef BH2_STACK_PROBE_CHECKPOINTS
         stack_probe_checkpoint(1);
#endif
         draw_all(0);
#ifdef BH2_STACK_PROBE_CHECKPOINTS
         stack_probe_checkpoint(2);
#endif
         draw_hud();
#ifdef BH2_STACK_PROBE_CHECKPOINTS
         stack_probe_checkpoint(3);
#endif
         fill_screen_box(10,69,60,54,0);
#ifdef BH2_STACK_PROBE_CHECKPOINTS
         stack_probe_checkpoint(4);
#endif
         fill_screen_box(10,69,60,1,11);
#ifdef BH2_STACK_PROBE_CHECKPOINTS
         stack_probe_checkpoint(5);
#endif
         overlay_drawing=1;
         if (mode == MODE_PAUSE) {
            draw_menu_text(33,80,"PAUSA",11);
            draw_menu_text(20,105,"P PARA CONTINUAR",1);
         } else if (mode == MODE_HURT) {
            draw_menu_text(27,80,"SIN VIDAS",6);
            draw_menu_text(14,105,"ESPACIO REINTENTAR",1);
         } else if (mode == MODE_CLEAR) {
            draw_menu_text(24,80,"FASE SUPERADA",11);
#ifdef BH2_STACK_PROBE_CHECKPOINTS
            stack_probe_checkpoint(6);
#endif
            draw_menu_text(14,105,"ESPACIO CONTINUAR",1);
#ifdef BH2_STACK_PROBE_CHECKPOINTS
            stack_probe_checkpoint(7);
#endif
         } else {
            draw_menu_text(22,80,"TODO DEVUELTO",11);
            draw_menu_text(19,93,"FIN DE LA CAMPANA",1);
            draw_menu_text(14,110,"ESPACIO OTRA PARTIDA",10);
         }
#ifdef BH2_STACK_PROBE_AFTER_DRAWALL
         if (*(volatile u8*)0x7D60 != 0xA5) {
            validation_state[38] = 2;
            for (;;) { }
         }
#endif
         overlay_drawing=0;
         overlay_mode=mode;
      }
      return;
   }
   if (overlay_mode != 255) {
      cpct_memcpy(CPCT_VMEM_START, BG_MEM, 0x4000);
      overlay_mode=255;
   }
   if (!fresh_background) restore_old_positions();
   else fresh_background=0;
   draw_all(vxq != 0);
}

#ifndef BH2_HOST
extern const u8 loading_bitmap[], loading_palette[];

static void show_loading_screen(void) {
   u8 frame;
   /* Hide decompression, then reveal the exact comic bitmap. The packed
    * source lives in BG_MEM until load_stage reuses it for the arena. */
   for (frame = 0; frame < 16; ++frame) cpct_setPALColour(frame, 0x54);
   cpct_setBorder(0x54);
   zx0_from_c(loading_bitmap, CPCT_VMEM_START);
   clock_wait_vsync_edge();
   cpct_setPalette((u8*)loading_palette, 16);
   for (frame = 0; frame < 150; ++frame) clock_wait_vsync_edge();
}

void main(void) {
   /* cpct_setStackLocation replaces SP, so keep main free of stack locals. */
#ifdef BH2_STREAM_CHAPTERS
   firmware_handler = cpct_disableFirmware();
   /* This binary has no SDCC CRT to apply initialized-data values. Force the
      first disk read explicitly before using the chapter cache. */
   resident_chapter = 255;
   /* BSS is not cleared when BASIC runs this no-CRT binary. Do not let random
      RAM contents trigger a restore from bank 7 before its first save. */
   firmware_jumpblock_cached = 0;
#else
   (void)cpct_disableFirmware();
#endif
   cpct_setStackLocation((void*)0x7ff0);
   cpct_setVideoMode(0);
   show_loading_screen();
#ifndef BH2_M1_ONLY
   demo_active = 0;
#endif
   overlay_drawing = 0;
   menu_music = 1;
   audio_init();
   cpct_setPalette((u8*)palette1, 16);
   input_reset();
   load_stage(0, 1);
   cpct_setVideoMode(0);
   game_present();
   telemetry_reset();
   clock_init();
   clock_started = 1;
#ifdef BH2_STACK_PROBE
   stack_probe_mark();
#endif
   while (1) {
      if (!clock_pending() && !clock_wait_vsync_edge()) continue;
      if (clock_is_overrun(clock_pending())) telemetry_overrun(clock_pending());
      while (clock_pop_tick()) {
         game_tick();
#ifdef BH2_STACK_PROBE_AFTER_TICK
         if (*(volatile u8*)0x7D60 != 0xA5) {
            *(volatile u8*)0x7C48 = 3;
            for (;;) { }
         }
#endif
#ifndef BH2_STACK_PROBE_AUDIO_OFF
         audio_tick();
#endif
#ifndef BH2_M1_ONLY
         record_demo_evidence();
#endif
         telemetry_present(clock_pending());
         game_present();
      }
   }
}

#endif
