#include <cpctelera.h>
#include <stdint.h>
#include "banks.h"
#include "render/render_g.h"
#include "render_asset_layout.h"
#include "render_scenarios.h"

#define STACK_LOW 0x3c68u
#define STACK_TOP 0x3f68u
#define PATCH_OFFSET 0x1519u
#define FIXTURE_STAGE (*(volatile uint8_t*)0x3c60u)

static const uint8_t palette[16] = {
   0x14,0x0b,0x17,0x13,0x16,0x00,0x0d,0x06,
   0x03,0x1c,0x05,0x0a,0x0e,0x07,0x1e,0x04
};
static const uint32_t crc32_nibble_table[16] = {
   0x00000000ul,0x1db71064ul,0x3b6e20c8ul,0x26d930acul,
   0x76dc4190ul,0x6b6b51f4ul,0x4db26158ul,0x5005713cul,
   0xedb88320ul,0xf00f9344ul,0xd6d6a3e8ul,0xcb61b38cul,
   0x9b64c2b0ul,0x86d3d2d4ul,0xa00ae278ul,0xbdbdf21cul
};
static RenderGSprite pitu_sprite;
static RenderGSprite alberto_sprite;
static uint8_t ram0_canary;
#define BACKGROUND ((volatile uint8_t*)0x4000u)

extern const uint8_t rg_pitu_stand_r_0[];
extern const uint8_t rg_pitu_stand_r_1[];
extern const uint8_t rg_pitu_stand_l_0[];
extern const uint8_t rg_pitu_stand_l_1[];
extern const uint8_t rg_pitu_walk_r_0[];
extern const uint8_t rg_pitu_walk_r_1[];
extern const uint8_t rg_pitu_walk_l_0[];
extern const uint8_t rg_pitu_walk_l_1[];
extern const uint8_t rg_alberto_r_0[];
extern const uint8_t rg_alberto_r_1[];
extern const uint8_t rg_alberto_l_0[];
extern const uint8_t rg_alberto_l_1[];

void render_test_main(void);

void main(void) __naked {
   __asm
      di
      ld sp, #0x3f68
      ld hl, #0x3c68
      ld (hl), #0xa5
      ld de, #0x3c69
      ld bc, #0x02ff
      ldir
      jp _render_test_main
   __endasm;
}

static uint8_t copy_variant(uint8_t bank, uint16_t offset,
                            const uint8_t* source, uint16_t bytes) {
   uint16_t i;
   volatile uint8_t* window = (volatile uint8_t*)BANK_WINDOW_BASE;
   if (bank_enter(bank) != BANK_OK) return 0;
   for (i = 0; i < bytes; ++i) window[offset + i] = source[i];
   return bank_leave() == BANK_OK;
}

static uint8_t load_all_variants(void) {
   uint8_t ok = 1;
   ok &= copy_variant(BANK_C4, RG_PITU_STAND_R_0_OFFSET, rg_pitu_stand_r_0, RG_PITU_STAND_R_0_BYTES);
   ok &= copy_variant(BANK_C4, RG_PITU_STAND_R_1_OFFSET, rg_pitu_stand_r_1, RG_PITU_STAND_R_1_BYTES);
   ok &= copy_variant(BANK_C4, RG_PITU_STAND_L_0_OFFSET, rg_pitu_stand_l_0, RG_PITU_STAND_L_0_BYTES);
   ok &= copy_variant(BANK_C4, RG_PITU_STAND_L_1_OFFSET, rg_pitu_stand_l_1, RG_PITU_STAND_L_1_BYTES);
   ok &= copy_variant(BANK_C4, RG_PITU_WALK_R_0_OFFSET, rg_pitu_walk_r_0, RG_PITU_WALK_R_0_BYTES);
   ok &= copy_variant(BANK_C4, RG_PITU_WALK_R_1_OFFSET, rg_pitu_walk_r_1, RG_PITU_WALK_R_1_BYTES);
   ok &= copy_variant(BANK_C4, RG_PITU_WALK_L_0_OFFSET, rg_pitu_walk_l_0, RG_PITU_WALK_L_0_BYTES);
   ok &= copy_variant(BANK_C4, RG_PITU_WALK_L_1_OFFSET, rg_pitu_walk_l_1, RG_PITU_WALK_L_1_BYTES);
   ok &= copy_variant(BANK_C6, RG_ALBERTO_R_0_OFFSET, rg_alberto_r_0, RG_ALBERTO_R_0_BYTES);
   ok &= copy_variant(BANK_C6, RG_ALBERTO_R_1_OFFSET, rg_alberto_r_1, RG_ALBERTO_R_1_BYTES);
   ok &= copy_variant(BANK_C6, RG_ALBERTO_L_0_OFFSET, rg_alberto_l_0, RG_ALBERTO_L_0_BYTES);
   ok &= copy_variant(BANK_C6, RG_ALBERTO_L_1_OFFSET, rg_alberto_l_1, RG_ALBERTO_L_1_BYTES);
   return ok;
}

static uint32_t screen_crc32(void) {
   uint32_t crc = 0xfffffffful;
   uint16_t i;
   volatile const uint8_t* screen =
      (volatile const uint8_t*)(uintptr_t)render_g_visible_base();
   for (i = 0; i < RENDER_G_SCREEN_BYTES; ++i) {
      crc ^= screen[i];
      crc = (crc >> 4) ^ crc32_nibble_table[crc & 0x0fu];
      crc = (crc >> 4) ^ crc32_nibble_table[crc & 0x0fu];
   }
   return crc ^ 0xfffffffful;
}

static uint8_t stack_guard_ok(void) {
   uint16_t address;
   for (address = STACK_LOW; address < (uint16_t)(STACK_LOW + 256u); ++address)
      if (*(volatile uint8_t*)address != 0xa5) return 0;
   return 1;
}

void render_test_main(void) {
   uint16_t i;
   uint8_t frame, pass = 1, patched = 0, first_bad_frame = 0;
   RenderGActor actors[2];
   FIXTURE_STAGE = 0x10;
   cpct_disableFirmware();
   cpct_setVideoMode(0);
   cpct_setPalette((uint8_t*)palette, 16);
   FIXTURE_STAGE = 0x11;
   cpct_memset(CPCT_VMEM_START, 0, RENDER_G_SCREEN_BYTES);
   ram0_canary = 0x69;
   bank_init();
   FIXTURE_STAGE = 0x12;
   if (render_g_init() != RENDER_G_OK) pass = 0;
   FIXTURE_STAGE = 0x13;

   for (i = 0; i < RENDER_G_SCREEN_BYTES; ++i)
      BACKGROUND[i] = (uint8_t)(i * 37u + (i >> 4) * 11u + 0x5au);
   FIXTURE_STAGE = 0x14;

   pitu_sprite.bank = BANK_C4;
   pitu_sprite.pose_count = 2;
   pitu_sprite.height = 32;
   pitu_sprite.variant_offset[0][0][0] = RG_PITU_STAND_R_0_OFFSET;
   pitu_sprite.variant_offset[0][0][1] = RG_PITU_STAND_R_1_OFFSET;
   pitu_sprite.variant_offset[0][1][0] = RG_PITU_STAND_L_0_OFFSET;
   pitu_sprite.variant_offset[0][1][1] = RG_PITU_STAND_L_1_OFFSET;
   pitu_sprite.variant_offset[1][0][0] = RG_PITU_WALK_R_0_OFFSET;
   pitu_sprite.variant_offset[1][0][1] = RG_PITU_WALK_R_1_OFFSET;
   pitu_sprite.variant_offset[1][1][0] = RG_PITU_WALK_L_0_OFFSET;
   pitu_sprite.variant_offset[1][1][1] = RG_PITU_WALK_L_1_OFFSET;
   alberto_sprite.bank = BANK_C6;
   alberto_sprite.pose_count = 1;
   alberto_sprite.height = 32;
   alberto_sprite.variant_offset[0][0][0] = RG_ALBERTO_R_0_OFFSET;
   alberto_sprite.variant_offset[0][0][1] = RG_ALBERTO_R_1_OFFSET;
   alberto_sprite.variant_offset[0][1][0] = RG_ALBERTO_L_0_OFFSET;
   alberto_sprite.variant_offset[0][1][1] = RG_ALBERTO_L_1_OFFSET;
   if (!load_all_variants()) pass = 0;
   FIXTURE_STAGE = 0x15;

#ifdef RENDER_REALTIME_CAPTURE
   /* A separate capture build cycles scenes at one presented frame per
    * VSYNC. It omits CRC calculation so the recorded renderer stays on the
    * same presentation path as a normal frame. */
   while (1) {
#endif
   for (frame = 0; frame < RENDER_TEST_FRAME_COUNT; ++frame) {
      const RenderTestFrame* test = &render_test_frames[frame];
      uint8_t actor;
      FIXTURE_STAGE = (uint8_t)(0x20u + frame);
      if (test->background && !patched) {
         if (render_g_background_write(PATCH_OFFSET, 0xa5) != RENDER_G_OK) pass = 0;
         patched = 1;
      }
      for (actor = 0; actor < test->count; ++actor) {
         const RenderTestActor* source = &test->actors[actor];
         RenderGActor* target = &actors[actor];
         target->sprite = source->sprite == RG_TEST_PITU ? &pitu_sprite : &alberto_sprite;
         target->x = source->x;
         target->y = source->y;
         target->pose = source->pose;
         target->facing_left = source->facing_left;
         target->layer = source->layer;
         target->id = source->id;
         target->visible = 1;
      }
      if (render_g_present(actors, test->count) != RENDER_G_OK) pass = 0;
      FIXTURE_STAGE = (uint8_t)(0x30u + frame);
#ifdef RENDER_REALTIME_CAPTURE
      cpct_waitVSYNC();
#else
      if (screen_crc32() != render_test_crc32[frame]) {
         pass = 0;
         if (!first_bad_frame) first_bad_frame = (uint8_t)(frame + 1u);
      }
      FIXTURE_STAGE = (uint8_t)(0x40u + frame);
#endif
   }
#ifdef RENDER_REALTIME_CAPTURE
   }
#else
   if (bank_current() != BANK_C0 || bank_depth() != 0 || ram0_canary != 0x69 ||
       !stack_guard_ok()) {
      pass = 0;
      first_bad_frame = 0x0fu;
   }
   FIXTURE_STAGE = 0x50;
   /* Distinguish frame-CRC failures (0xA1..A7) from manager/guard failures
    * (0xAF) in the physical RAM3 snapshot. */
   *(volatile uint8_t*)(uintptr_t)render_g_visible_base() =
      pass ? 0x55u : (uint8_t)(0xa0u | first_bad_frame);
   FIXTURE_STAGE = pass ? 0x55u : (uint8_t)(0xa0u | first_bad_frame);
   /* Reuse the instrumented Caprice fixture signature so the emulator can
    * capture the exact final VRAM at this stable, completed checkpoint. */
   {
      volatile uint8_t* trace = (volatile uint8_t*)0x3c00u;
      trace[0] = 0xb2; trace[1] = 0x4f; trace[2] = 0x30; trace[3] = 0x32;
      trace[4] = 0x26; trace[5] = 0x20; trace[6] = 0x02; trace[7] = 0xb2;
      trace[14] = 0xa5;
   }
   __asm
_render_case_done::
   __endasm;
   while (1) cpct_waitVSYNC();
#endif
}
