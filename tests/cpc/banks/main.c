#include <cpctelera.h>
#include <stdint.h>
#include "banks.h"
#include "clock.h"

#define TEST_BYTES 32u
#define COPY_BYTES 64u
#define TEST_OFFSET 0x0200u
#define SOURCE_OFFSET 0x1000u
#define DEST_OFFSET 0x1200u
#define STACK_LOW 0xbcf0u
#define STACK_TOP 0xbff0u

static const uint8_t palette[16] = {
   0x14,0x0b,0x17,0x13,0x16,0x00,0x0d,0x06,
   0x03,0x1c,0x05,0x0a,0x0e,0x07,0x1e,0x04
};
static const uint8_t glyphs[6][5] = {
   {6,5,6,5,6}, /* A */
   {7,4,6,4,7}, /* E */
   {7,4,6,4,4}, /* F */
   {5,5,7,5,5}, /* H */
   {5,5,5,5,7}, /* U */
   {3,4,2,1,6}  /* S */
};

static uint8_t saved_ram1[TEST_BYTES];
static uint8_t saved_banks[4][TEST_BYTES];
static uint8_t saved_src[COPY_BYTES];
static uint8_t saved_dst[COPY_BYTES];
static uint8_t saved_ram2[TEST_BYTES];
static uint8_t saved_screen[TEST_BYTES];
static uint8_t canary_ram0;
static volatile uint8_t* const window = (volatile uint8_t*)BANK_WINDOW_BASE;
static volatile uint8_t* const ram2 = (volatile uint8_t*)0x8000;
static volatile uint8_t* const screen_guard = (volatile uint8_t*)0xff00;
extern uint8_t bank_test_iff_enabled(void);

void bank_test_main(void);

void main(void) __naked {
   __asm
      ld sp, #0xbff0
      ld hl, #0xbcf0
      ld (hl), #0xa5
      ld de, #0xbcf1
      ld bc, #0x02ff
      ldir
      jp _bank_test_main
   __endasm;
}

static uint8_t config_for(uint8_t bank) { return bank; }

static void draw_result(uint8_t pass) {
   uint8_t i, row, col;
   for (i = 0; i < 4; ++i) {
      char letter;
      uint8_t glyph;
      if (pass) letter = i == 0 ? 'P' : i == 1 ? 'A' : 'S';
      else letter = i == 0 ? 'F' : i == 1 ? 'A' : i == 2 ? 'I' : 'L';
      glyph = letter == 'A' ? 0 : letter == 'E' ? 1 :
              letter == 'F' ? 2 : letter == 'H' ? 3 :
              letter == 'U' ? 4 : 5;
      for (row = 0; row < 5; ++row) {
         uint8_t bits = glyphs[glyph][row];
         if (letter == 'P') bits = (row == 0 || row == 1) ? 7 : (row == 2 ? 6 : 4);
         if (letter == 'I') bits = 2;
         if (letter == 'L') bits = row == 4 ? 7 : 4;
         for (col = 0; col < 3; ++col) {
            uint8_t ink = (bits & (uint8_t)(4u >> col)) ? (pass ? 11 : 3) : 0;
            uint8_t* dst = cpct_getScreenPtr(CPCT_VMEM_START,
               (uint8_t)(12 + i * 4 + col), (uint8_t)(24 + row));
            dst[0] = cpct_px2byteM0(ink, ink);
         }
      }
   }
}

static void draw_stage_marker(uint8_t stage, uint8_t pass) {
   uint8_t x, y, ink = pass ? 11 : 3;
   for (y = 0; y < 8; ++y) {
      for (x = 0; x < 8; ++x) {
         uint8_t* dst = cpct_getScreenPtr(CPCT_VMEM_START,
            (uint8_t)(24 + x), (uint8_t)(48 + stage * 12 + y));
         dst[0] = cpct_px2byteM0(ink, ink);
      }
   }
}

static uint8_t save_bank(uint8_t bank, uint8_t* out, uint16_t offset,
                         uint8_t count) {
   uint8_t i;
   if (bank_enter(config_for(bank)) != BANK_OK) return 0;
   for (i = 0; i < count; ++i) out[i] = window[offset + i];
   return bank_leave() == BANK_OK;
}

static uint8_t restore_bank(uint8_t bank, const uint8_t* in, uint16_t offset,
                            uint8_t count) {
   uint8_t i;
   if (bank_enter(config_for(bank)) != BANK_OK) return 0;
   for (i = 0; i < count; ++i) window[offset + i] = in[i];
   return bank_leave() == BANK_OK;
}

static uint8_t read_bank_equals(uint8_t bank, uint16_t offset,
                                const uint8_t* expected, uint8_t count) {
   uint8_t i, ok = 1;
   if (bank_enter(config_for(bank)) != BANK_OK) return 0;
   for (i = 0; i < count; ++i) if (window[offset + i] != expected[i]) ok = 0;
   if (bank_leave() != BANK_OK) ok = 0;
   return ok;
}

static uint8_t test_patterns(void) {
   uint8_t bank, i, ok = 1;
   for (i = 0; i < TEST_BYTES; ++i) {
      saved_ram1[i] = window[TEST_OFFSET + i];
      saved_ram2[i] = ram2[0x3a00u + i];
      saved_screen[i] = screen_guard[i];
      window[TEST_OFFSET + i] = 0x11;
      ram2[0x3a00u + i] = (uint8_t)(0x82u + i);
      screen_guard[i] = (uint8_t)(0xC3u ^ i);
   }
   for (bank = 4; bank <= 7; ++bank) {
      uint8_t* backup = saved_banks[bank - 4];
      for (i = 0; i < TEST_BYTES; ++i) backup[i] = 0;
      if (!save_bank(bank, backup, TEST_OFFSET, TEST_BYTES)) ok = 0;
   }
   for (bank = 4; bank <= 7; ++bank) {
      uint8_t pattern = (uint8_t)(bank * 0x11u);
      if (bank_enter(config_for(bank)) != BANK_OK) { ok = 0; continue; }
      for (i = 0; i < TEST_BYTES; ++i) window[TEST_OFFSET + i] = pattern;
      if (bank_leave() != BANK_OK) ok = 0;
   }
   for (bank = 4; bank <= 7; ++bank) {
      uint8_t pattern[TEST_BYTES];
      for (i = 0; i < TEST_BYTES; ++i) pattern[i] = (uint8_t)(bank * 0x11u);
      if (!read_bank_equals(bank, TEST_OFFSET, pattern, TEST_BYTES)) ok = 0;
   }
   if (bank_current() != BANK_C0 || bank_depth() != 0) ok = 0;
   if (window[TEST_OFFSET] != 0x11) ok = 0;
   for (i = 0; i < TEST_BYTES; ++i) {
      if (ram2[0x3a00u + i] != (uint8_t)(0x82u + i)) ok = 0;
      if (screen_guard[i] != (uint8_t)(0xC3u ^ i)) ok = 0;
   }
   for (bank = 4; bank <= 7; ++bank)
      if (!restore_bank(bank, saved_banks[bank - 4], TEST_OFFSET, TEST_BYTES)) ok = 0;
   for (i = 0; i < TEST_BYTES; ++i) {
      window[TEST_OFFSET + i] = saved_ram1[i];
      ram2[0x3a00u + i] = saved_ram2[i];
      screen_guard[i] = saved_screen[i];
   }
   return ok;
}

static uint8_t test_nested_and_interrupts(void) {
   uint16_t i;
   uint8_t ok = 1, enabled;
   uint16_t before, after;
   if (bank_enter(BANK_C4) != BANK_OK || bank_current() != BANK_C4) ok = 0;
   if (bank_enter(BANK_C7) != BANK_OK || bank_current() != BANK_C7) ok = 0;
   if (bank_leave() != BANK_OK || bank_current() != BANK_C4) ok = 0;
   if (bank_leave() != BANK_OK || bank_current() != BANK_C0) ok = 0;
   if (bank_leave() != BANK_ERR_UNBALANCED || bank_current() != BANK_C0) ok = 0;
   if (bank_enter(1) != BANK_ERR_CONFIG || bank_current() != BANK_C0) ok = 0;
   for (i = 0; i < BANK_MAX_DEPTH; ++i) if (bank_enter(BANK_C0) != BANK_OK) ok = 0;
   if (bank_enter(BANK_C4) != BANK_ERR_DEPTH) ok = 0;
   while (bank_depth()) if (bank_leave() != BANK_OK) ok = 0;

   __asm di __endasm;
   if (bank_enter(BANK_C6) != BANK_OK) ok = 0;
   enabled = (uint8_t)bank_test_iff_enabled();
   if (bank_leave() != BANK_OK) ok = 0;
   if (bank_test_iff_enabled()) ok = 0;
   __asm ei __endasm;
   if (enabled) ok = 0;

   before = clock_interrupts();
   for (i = 0; i < 10; ++i) {
      if (bank_enter(BANK_C4) != BANK_OK) { ok = 0; break; }
      if (!clock_wait_vsync_edge()) ok = 0;
      if (bank_leave() != BANK_OK) ok = 0;
   }
   after = clock_interrupts();
   if (after == before) ok = 0;

   for (i = 0; i < 10000u; ++i) {
      uint8_t outer = (uint8_t)(BANK_C4 + (i & 3u));
      if (bank_enter(outer) != BANK_OK) { ok = 0; break; }
      if ((i & 0x03ffu) == 0u && !clock_wait_vsync_edge()) ok = 0;
      if (bank_enter(BANK_C7) != BANK_OK) ok = 0;
      if (bank_leave() != BANK_OK || bank_current() != outer) ok = 0;
      if (bank_leave() != BANK_OK || bank_current() != BANK_C0) ok = 0;
   }
   if (bank_depth() != 0 || bank_current() != BANK_C0) ok = 0;
   return ok;
}

static uint8_t test_copy_and_guards(void) {
   BankHandle src, dst, stale, invalid;
   uint8_t i, ok = 1;
   for (i = 0; i < COPY_BYTES; ++i) {
      saved_src[i] = window[SOURCE_OFFSET + i];
      saved_dst[i] = window[DEST_OFFSET + i];
   }
   if (!save_bank(4, saved_src, SOURCE_OFFSET, COPY_BYTES)) ok = 0;
   if (!save_bank(7, saved_dst, DEST_OFFSET, COPY_BYTES)) ok = 0;
   if (bank_enter(BANK_C4) != BANK_OK) ok = 0;
   for (i = 0; i < COPY_BYTES; ++i)
      window[SOURCE_OFFSET + i] = (uint8_t)(i * 13u + 7u);
   if (bank_leave() != BANK_OK) ok = 0;
   if (bank_enter(BANK_C7) != BANK_OK) ok = 0;
   for (i = 0; i < COPY_BYTES; ++i) window[DEST_OFFSET + i] = 0x5a;
   if (bank_leave() != BANK_OK) ok = 0;

   if (bank_handle_make(4, SOURCE_OFFSET, COPY_BYTES, &src) != BANK_OK) ok = 0;
   if (bank_handle_make(7, DEST_OFFSET, COPY_BYTES, &dst) != BANK_OK) ok = 0;
   if (bank_copy(src, dst, COPY_BYTES) != BANK_OK) ok = 0;
   for (i = 0; i < COPY_BYTES; ++i) {
      if (bank_enter(BANK_C7) != BANK_OK) { ok = 0; break; }
      if (window[DEST_OFFSET + i] != (uint8_t)(i * 13u + 7u)) ok = 0;
      if (bank_leave() != BANK_OK) ok = 0;
   }

   if (bank_handle_make(4, 0x3ff0u, 32, &invalid) != BANK_ERR_RANGE) ok = 0;
   if (bank_handle_make(1, 0, 1, &invalid) != BANK_ERR_HANDLE) ok = 0;
   if (bank_handle_make(4, SOURCE_OFFSET, COPY_BYTES, &stale) != BANK_OK) ok = 0;
   if (bank_invalidate(4) != BANK_OK) ok = 0;
   if (bank_copy(stale, dst, 16) != BANK_ERR_STALE) ok = 0;
   for (i = 0; i < 16; ++i) {
      if (bank_enter(BANK_C7) != BANK_OK) { ok = 0; break; }
      if (window[DEST_OFFSET + i] != (uint8_t)(i * 13u + 7u)) ok = 0;
      if (bank_leave() != BANK_OK) ok = 0;
   }
   if (bank_handle_make(4, SOURCE_OFFSET, COPY_BYTES, &src) != BANK_OK) ok = 0;
   if (bank_copy(src, src, 1) != BANK_ERR_SAME_BANK) ok = 0;
   if (bank_current() != BANK_C0 || bank_depth() != 0) ok = 0;

   if (!restore_bank(4, saved_src, SOURCE_OFFSET, COPY_BYTES)) ok = 0;
   if (!restore_bank(7, saved_dst, DEST_OFFSET, COPY_BYTES)) ok = 0;
   if (bank_current() != BANK_C0 || bank_depth() != 0) ok = 0;
   return ok;
}

static uint8_t stack_guard_ok(void) {
   uint16_t address;
   for (address = STACK_LOW; address < (uint16_t)(STACK_LOW + 256u); ++address)
      if (*(volatile uint8_t*)address != 0xa5) return 0;
   return 1;
}

void bank_test_main(void) {
   uint8_t pass = 1, stage_ok;
   cpct_disableFirmware();
   cpct_setVideoMode(0);
   cpct_setPalette((uint8_t*)palette, 16);
   cpct_memset(CPCT_VMEM_START, 0, 0x4000);
   draw_result(0);
   canary_ram0 = 0x69;
   bank_init();
   clock_init();

   stage_ok = test_patterns();
   if (!stage_ok) pass = 0;
   draw_stage_marker(0, stage_ok);
   stage_ok = test_nested_and_interrupts();
   if (!stage_ok) pass = 0;
   draw_stage_marker(1, stage_ok);
   stage_ok = test_copy_and_guards();
   if (!stage_ok) pass = 0;
   draw_stage_marker(2, stage_ok);
   stage_ok = (bank_current() == BANK_C0 && bank_depth() == 0);
   if (!stage_ok) pass = 0;
   draw_stage_marker(3, stage_ok);
   stage_ok = (canary_ram0 == 0x69);
   if (!stage_ok) pass = 0;
   draw_stage_marker(4, stage_ok);
   stage_ok = stack_guard_ok();
   if (!stage_ok) pass = 0;
   draw_stage_marker(5, stage_ok);
   draw_result(pass);
   while (1) cpct_waitVSYNC();
}
