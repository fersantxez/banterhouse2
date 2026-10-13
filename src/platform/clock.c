#include <cpctelera.h>
#include <stdint.h>
#include "clock.h"

volatile uint16_t clock_tick_count;
volatile uint16_t clock_irq_count;
volatile uint8_t clock_irq_divider;
volatile uint8_t clock_pending_count;
static uint16_t previous_handler;

/* The CPC supplies six interrupt requests per 50 Hz frame. Keep the ISR short:
 * it only counts interrupts, makes one fixed tick, and queues it for the main loop.
 * It never touches PPI, AY, video, banks, or game state. */
void clock_irq(void) {
   ++clock_irq_count;
   if (++clock_irq_divider == 6) {
      clock_irq_divider = 0;
      ++clock_tick_count;
      if (clock_pending_count != 255) ++clock_pending_count;
   }
}

void clock_init(void) {
   clock_tick_count = 0;
   clock_irq_count = 0;
   clock_irq_divider = 0;
   clock_pending_count = 0;
   previous_handler = cpct_disableFirmware();
   cpct_setInterruptHandler(clock_irq);
}

void clock_stop(void) {
   cpct_reenableFirmware(previous_handler);
}

uint16_t clock_ticks(void) __naked {
   __asm
      ld   a, i
      di
      ld   hl, (_clock_tick_count)
      jp   po, 001$
      ei
001$: ret
   __endasm;
}

uint16_t clock_interrupts(void) __naked {
   __asm
      ld   a, i
      di
      ld   hl, (_clock_irq_count)
      jp   po, 009$
      ei
   009$: ret
   __endasm;
}

uint8_t clock_pending(void) __naked {
   __asm
      ld   a, i
      di
      ld   a, (_clock_pending_count)
      ld   l, a
      ld   h, #0
      jp   po, 002$
      ei
002$: ret
   __endasm;
}

uint8_t clock_pop_tick(void) __naked {
   __asm
      ld   a, i
      di
      push af
      ld   a, (_clock_pending_count)
      or   a
      jr   z, 003$
      dec  a
      ld   (_clock_pending_count), a
      ld   l, #1
      ld   h, #0
      jr   004$
003$: ld   l, #0
      ld   h, #0
004$: pop  af
      jp   po, 005$
      ei
005$: ret
   __endasm;
}

uint8_t clock_wait_vsync_edge(void) __naked {
   __asm
      ;; CPCtelera defines PPI port B high byte as &F5; bit 0 is VSYNC.
      push bc
      push de
      ld   bc, #0xf500
      ld   de, #0x4000
006$: in   a, (c)
      and  #1
      jr   z, 007$
      dec  de
      ld   a, d
      or   e
      jr   nz, 006$
      ld   l, #0
      pop  de
      pop  bc
      ret
007$: ld   de, #0x4000
008$: in   a, (c)
      and  #1
      jr   nz, 009$
      dec  de
      ld   a, d
      or   e
      jr   nz, 008$
      ld   l, #0
      pop  de
      pop  bc
      ret
009$: ld   l, #1
      pop  de
      pop  bc
      ret
   __endasm;
}
