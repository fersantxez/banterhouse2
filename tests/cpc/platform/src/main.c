#include <cpctelera.h>
#include <stdint.h>
#include "clock.h"
#include "input.h"
#include "telemetry.h"
#include "clock_logic.h"

#define PLATFORM_TEST_FRAMES 3000
#define PLATFORM_OVERRUN_TARGET 32

/* CPC-side wrap fixture: this program is the sole owner of these ISR counters. */
extern volatile uint16_t clock_tick_count;
extern volatile uint8_t clock_irq_divider;
extern volatile uint8_t clock_pending_count;

static InputFrame input_frame;
static Telemetry telemetry;
static uint8_t probe_held, probe_pressed, probe_released;
static uint8_t probe_press_edges, probe_release_edges;
/* Bit 0: left+right, bit 1: jump+down, bit 2: left+up diagonal. */
static uint8_t probe_chords;
static const u8 diagnostic_palette[16] = {
   0x14, 0x0b, 0x17, 0x13, 0x16, 0x00, 0x0d, 0x06,
   0x03, 0x1c, 0x05, 0x0a, 0x0e, 0x07, 0x1e, 0x04
};

void platform_main(void);

/* AMSDOS starts at the first linked byte. Keep this jump first even when helper
 * functions are added later; the production entry follows the same invariant. */
void main(void) __naked {
   __asm
      ld sp, #0x7ff0
      jp _platform_main
   __endasm;
}

/* Do not use cpct_drawStringM0 here: its implementation enables the lower ROM
 * and must itself live above &4000. This small diagnostic font writes Mode 0
 * pixels directly, so the diagnostic remains safe in the low-memory profile. */
static const uint8_t font3x5[38][5] = {
   {2,5,7,5,5}, {6,5,6,5,6}, {3,4,4,4,3}, {6,5,5,5,6}, {7,4,6,4,7},
   {7,4,6,4,4}, {3,4,5,5,3}, {5,5,7,5,5}, {7,2,2,2,7}, {1,1,1,5,2},
   {5,5,6,5,5}, {4,4,4,4,7}, {5,7,7,5,5}, {6,5,5,5,5}, {2,5,5,5,2},
   {6,5,6,4,4}, {2,5,5,3,1}, {6,5,6,5,5}, {3,4,2,1,6}, {7,2,2,2,2},
   {5,5,5,5,7}, {5,5,5,5,2}, {5,5,7,7,5}, {5,5,2,5,5}, {5,5,2,2,2},
   {7,1,2,4,7},
   {7,5,5,5,7}, {2,6,2,2,7}, {6,1,2,4,7}, {6,1,2,1,6}, {5,5,7,1,1},
   {7,4,6,1,6}, {3,4,6,5,2}, {7,1,2,2,2}, {2,5,2,5,2}, {2,5,3,1,6},
   {7,2,7,4,7}, /* plus */
   {0,0,0,0,0}  /* space / unsupported punctuation */
};

static uint8_t glyph_index(char ch) {
   if (ch >= 'A' && ch <= 'Z') return (uint8_t)(ch - 'A');
   if (ch >= '0' && ch <= '9') return (uint8_t)(26 + ch - '0');
   if (ch == '+') return 36;
   return 37; /* blank for spaces and unsupported punctuation */
}

static void draw_text(uint8_t xbyte, uint8_t y, const char* text, uint8_t ink) {
   uint8_t i = 0, row;
   while (text[i]) {
      uint8_t index = glyph_index(text[i++]);
      for (row = 0; row < 5; ++row) {
         uint8_t bits = font3x5[index][row];
         uint8_t p0 = (bits & 4) ? ink : 0;
         uint8_t p1 = (bits & 2) ? ink : 0;
         uint8_t p2 = (bits & 1) ? ink : 0;
         uint8_t* dst = cpct_getScreenPtr(CPCT_VMEM_START,
                                          (uint8_t)(xbyte + (uint8_t)(i - 1) * 2),
                                          (uint8_t)(y + row));
         dst[0] = cpct_px2byteM0(p0, p1);
         dst[1] = cpct_px2byteM0(p2, 0);
      }
   }
}

static void draw_u16(uint8_t xbyte, uint8_t y, uint16_t value, uint8_t ink) {
   static const uint16_t divisors[5] = {10000, 1000, 100, 10, 1};
   uint8_t i;
   for (i = 0; i < 5; ++i) {
      char one[2];
      uint8_t digit = 0;
      while (value >= divisors[i]) {
         value = (uint16_t)(value - divisors[i]);
         ++digit;
      }
      one[0] = (char)('0' + digit);
      one[1] = 0;
      draw_text((uint8_t)(xbyte + i * 2), y, one, ink);
   }
}

/* Result digits are deliberately larger than the continuously refreshed HUD:
 * the 3x5 font is doubled in both axes so a Caprice capture can be transcribed
 * without relying on its FPS overlay or on enlarging a tiny screenshot. */
static void draw_big(uint8_t xbyte, uint8_t y, const char* text, uint8_t ink) {
   uint8_t i = 0, row, dy, col;
   while (text[i]) {
      uint8_t index = glyph_index(text[i++]);
      for (row = 0; row < 5; ++row) {
         uint8_t bits = font3x5[index][row];
         for (dy = 0; dy < 2; ++dy) {
            for (col = 0; col < 3; ++col) {
               uint8_t pixel = (bits & (uint8_t)(4u >> col)) ? ink : 0;
               uint8_t* dst = cpct_getScreenPtr(CPCT_VMEM_START,
                     (uint8_t)(xbyte + (uint8_t)(i - 1) * 4 + col),
                     (uint8_t)(y + row * 2 + dy));
               dst[0] = cpct_px2byteM0(pixel, pixel);
            }
         }
      }
   }
}

static void draw_big_u16(uint8_t xbyte, uint8_t y, uint16_t value,
                         uint8_t digits, uint8_t ink) {
   static const uint16_t divisors[5] = {10000, 1000, 100, 10, 1};
   char text[6];
   uint8_t i, first = (uint8_t)(5 - digits);
   for (i = 0; i < 5; ++i) {
      uint8_t digit = 0;
      while (value >= divisors[i]) {
         value = (uint16_t)(value - divisors[i]);
         ++digit;
      }
      text[i] = (char)('0' + digit);
   }
   text[5] = 0;
   draw_big(xbyte, y, text + first, ink);
}

static void print_result(uint16_t delta, uint16_t irq_delta,
                         uint8_t irq_min, uint8_t irq_max, uint8_t good) {
   uint8_t y, x;
   for (y = 0; y < 108; ++y) {
      uint8_t* row = cpct_getScreenPtr(CPCT_VMEM_START, 0, y);
      for (x = 0; x < 80; ++x) row[x] = 0;
   }
   draw_text(4, 4, "3000 VSYNC RESULTS", 11);
   draw_big(4, 20, good ? "PASS" : "FAIL", good ? 11 : 3);
   draw_big(28, 20, "TICKS", 11);
   draw_big_u16(52, 20, delta, 4, 11);
   draw_big(4, 44, "IRQS", 11);
   draw_big_u16(24, 44, irq_delta, 5, 11);
   draw_big(4, 68, "MIN", 11);
   draw_big_u16(20, 68, irq_min, 2, 11);
   draw_big(40, 68, "MAX", 11);
   draw_big_u16(56, 68, irq_max, 2, 11);
   draw_text(4, 92, "3000 VSYNC EDGES", 11);
   draw_text(4, 104, "KEYS ARROWS SPACE X P R", 11);
   /* Keep the live input panel on the same small-font path as the stable
    * static labels. Repainting individual doubled glyphs during keyboard
    * scanning made the CPC display intermittently blank in Caprice. */
   draw_text(4, 120, "HELD", 11);
   draw_u16(16, 120, 0, 11);
   draw_text(4, 136, "PRESS", 11);
   draw_u16(20, 136, 0, 11);
   draw_text(4, 152, "RELEASE", 11);
   draw_u16(24, 152, 0, 11);
   draw_text(52, 120, "PC", 11);
   draw_u16(58, 120, 0, 11);
   draw_text(52, 136, "RC", 11);
   draw_u16(58, 136, 0, 11);
   draw_text(52, 152, "CH", 11);
   draw_u16(58, 152, 0, 11);
}

void platform_main(void) {
   uint16_t start_tick, delta, start_irq, previous_irq, irq_delta;
   uint16_t irq_min = 0xFFFF, irq_max = 0;
   uint16_t i;
   uint8_t irq_frame;
   uint16_t now_irq;
   uint8_t good, sync_ok = 1;
   uint8_t overrun_wait_ok = 1, overrun_pending, drained_pending;
   uint8_t probe_dirty = 0;
   uint16_t wrap_start, wrap_delta;
   uint8_t wrap_ok = 1;
   cpct_disableFirmware();
   cpct_setVideoMode(0);
   cpct_setPalette((u8*)diagnostic_palette, 16);
   cpct_memset(CPCT_VMEM_START, 0, 0x4000);
   cpct_waitVSYNC();
   clock_init();
   input_reset();
   telemetry_reset();
   draw_text(4, 8, "BANTERHOUSE 2 PLATFORM DIAGNOSTIC", 11);
   draw_text(4, 16, "WAITING FOR 3000 RUN", 11);

   if (!clock_wait_vsync_edge()) {
      draw_text(4, 24, "VSYNC START TIMEOUT", 3);
      while (1) { }
   }
   start_tick = clock_ticks();
   start_irq = previous_irq = clock_interrupts();
   for (i = 0; i < PLATFORM_TEST_FRAMES; ++i) {
      if (!clock_wait_vsync_edge()) {
         draw_text(4, 36, "VSYNC EDGE TIMEOUT", 3);
         sync_ok = 0;
         break;
      }
      /* Keep the timed interval free of rendering work. Earlier versions
       * redrew this counter every 256 frames; any time spent drawing could
       * add IRQ-derived ticks and contaminate the VSYNC comparison. */
      now_irq = clock_interrupts();
      irq_frame = (uint8_t)clock_elapsed(now_irq, previous_irq);
      previous_irq = now_irq;
      if (irq_frame < irq_min) irq_min = irq_frame;
      if (irq_frame > irq_max) irq_max = irq_frame;
      while (clock_pop_tick()) { }
   }
   delta = clock_elapsed(clock_ticks(), start_tick);
   irq_delta = clock_elapsed(clock_interrupts(), start_irq);
   good = (sync_ok && i == PLATFORM_TEST_FRAMES &&
           delta >= PLATFORM_TEST_FRAMES - 1 && delta <= PLATFORM_TEST_FRAMES + 1 &&
           irq_delta >= PLATFORM_TEST_FRAMES * 6 - 6 &&
           irq_delta <= PLATFORM_TEST_FRAMES * 6 + 6 && irq_min >= 5 && irq_max <= 7);
   print_result(delta, irq_delta, (uint8_t)irq_min, (uint8_t)irq_max, good);

   /* Produce one bounded, intentional overrun to verify that diagnostics record
    * it and that the pending queue can still be drained afterwards. */
   while (clock_pop_tick()) { }
   while (clock_pending() < PLATFORM_OVERRUN_TARGET) {
      if (!clock_wait_vsync_edge()) {
         overrun_wait_ok = 0;
         break;
      }
   }
   overrun_pending = (uint8_t)clock_pending();
   telemetry_overrun(overrun_pending);
   /* Snapshot queue recovery immediately. Drawing even this tiny panel takes
    * long enough for new CPC ticks to arrive and would contaminate the result. */
   while (clock_pop_tick()) { }
   drained_pending = (uint8_t)clock_pending();
   draw_big(4, 176, overrun_wait_ok ? "OVERRUN" : "TIMEOUT", 11);
   draw_big_u16(40, 176, overrun_pending, 2, 11);
   draw_big(4, 188, "DRAINED", 11);
   draw_big_u16(40, 188, drained_pending, 2, 11);

   /* Seed the real ISR tick at &FFFA, then count eight VSYNC intervals.
    * The expected modulo-16-bit result is &0002. Interrupts are enabled before
    * and after this short test-only critical section. */
   __asm di __endasm;
   clock_tick_count = 0xFFFA;
   clock_irq_divider = 0;
   clock_pending_count = 0;
   __asm ei __endasm;
   wrap_start = clock_ticks();
   for (i = 0; i < 10 && clock_elapsed(clock_ticks(), wrap_start) < 8; ++i) {
      if (!clock_wait_vsync_edge()) {
         wrap_ok = 0;
         break;
      }
   }
   wrap_delta = clock_elapsed(clock_ticks(), wrap_start);
   while (clock_pop_tick()) { }
   if (wrap_delta != 8) wrap_ok = 0;
   draw_big(44, 176, "WRAP", 11);
   draw_big_u16(64, 176, wrap_delta, 2, 11);
   draw_big(44, 188, wrap_ok ? "PASS" : "FAIL", wrap_ok ? 11 : 3);
   telemetry_read(&telemetry);

   while (1) {
      uint8_t pending = clock_pending();
      if (clock_is_overrun(pending)) telemetry_overrun(pending);
      if (clock_pop_tick()) {
         input_sample(&input_frame);
         if (probe_held != input_frame.held) probe_dirty = 1;
         probe_held = input_frame.held;
         probe_pressed |= input_frame.pressed;
         probe_released |= input_frame.released;
         if (input_frame.pressed) { ++probe_press_edges; probe_dirty = 1; }
         if (input_frame.released) { ++probe_release_edges; probe_dirty = 1; }
         if (!(probe_chords & 1) &&
             (input_frame.held & (INPUT_LEFT | INPUT_RIGHT)) ==
             (INPUT_LEFT | INPUT_RIGHT)) { probe_chords |= 1; probe_dirty = 1; }
         if (!(probe_chords & 2) &&
             (input_frame.held & (INPUT_JUMP | INPUT_DOWN)) ==
             (INPUT_JUMP | INPUT_DOWN)) { probe_chords |= 2; probe_dirty = 1; }
         if (!(probe_chords & 4) &&
             (input_frame.held & (INPUT_LEFT | INPUT_JUMP)) ==
             (INPUT_LEFT | INPUT_JUMP)) { probe_chords |= 4; probe_dirty = 1; }
         telemetry_present(clock_pending());
         if (probe_dirty) {
            draw_u16(16, 120, probe_held, 11);
            draw_u16(20, 136, probe_pressed, 11);
            draw_u16(24, 152, probe_released, 11);
            draw_u16(58, 120, probe_press_edges, 11);
            draw_u16(58, 136, probe_release_edges, 11);
            draw_u16(58, 152, probe_chords, 11);
            probe_dirty = 0;
         }
      }
      if (clock_pop_tick()) {
         /* The second pending tick consumes one input sample, not a repeated edge. */
         input_sample(&input_frame);
         if (probe_held != input_frame.held) probe_dirty = 1;
         probe_held = input_frame.held;
         probe_pressed |= input_frame.pressed;
         probe_released |= input_frame.released;
         if (input_frame.pressed) { ++probe_press_edges; probe_dirty = 1; }
         if (input_frame.released) { ++probe_release_edges; probe_dirty = 1; }
         if (!(probe_chords & 1) &&
             (input_frame.held & (INPUT_LEFT | INPUT_RIGHT)) ==
             (INPUT_LEFT | INPUT_RIGHT)) { probe_chords |= 1; probe_dirty = 1; }
         if (!(probe_chords & 2) &&
             (input_frame.held & (INPUT_JUMP | INPUT_DOWN)) ==
             (INPUT_JUMP | INPUT_DOWN)) { probe_chords |= 2; probe_dirty = 1; }
         if (!(probe_chords & 4) &&
             (input_frame.held & (INPUT_LEFT | INPUT_JUMP)) ==
             (INPUT_LEFT | INPUT_JUMP)) { probe_chords |= 4; probe_dirty = 1; }
         telemetry_present(clock_pending());
         if (probe_dirty) {
            draw_u16(16, 120, probe_held, 11);
            draw_u16(20, 136, probe_pressed, 11);
            draw_u16(24, 152, probe_released, 11);
            draw_u16(58, 120, probe_press_edges, 11);
            draw_u16(58, 136, probe_release_edges, 11);
            draw_u16(58, 152, probe_chords, 11);
            probe_dirty = 0;
         }
      }
      /* Reading telemetry on every idle poll adds stack traffic without
       * changing the key fields or the snapshot captured above. Keep the
       * interactive probe focused on one input sample per logical tick. */
   }
}
