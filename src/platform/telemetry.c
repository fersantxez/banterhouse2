#include <cpctelera.h>
#include "clock.h"
#include "telemetry.h"

#if defined(BH2_TELEMETRY_PHASE_MARKERS)
/* Reserved only in dedicated timing builds. The instrumented Caprice backend
 * watches this address and timestamps the phase byte without a screen dump.
 */
#ifndef BH2_TELEMETRY_MARKER_ADDRESS
#define BH2_TELEMETRY_MARKER_ADDRESS 0x3fffu
#endif
void telemetry_phase_mark(uint8_t phase) {
   *(volatile uint8_t*)BH2_TELEMETRY_MARKER_ADDRESS = phase;
}
#endif

static volatile uint16_t presents;
static volatile uint16_t overruns;
static volatile uint8_t pending_max;

void telemetry_reset(void) {
   presents = 0;
   overruns = 0;
   pending_max = 0;
}

void telemetry_present(uint8_t pending) {
   ++presents;
   if (pending > pending_max) pending_max = pending;
}

void telemetry_overrun(uint8_t pending) {
   ++overruns;
   if (pending > pending_max) pending_max = pending;
}

void telemetry_read(Telemetry* out) __naked {
   /* Keep the whole critical section in ASM. Mixing PUSH/POP with following C
    * makes SDCC address the argument from the wrong SP and can overwrite the
    * return address. The pointer is at SP+4 after saving AF. */
   __asm
      ld a, i
      di
      push af
      ld hl, #4
      add hl, sp
      ld e, (hl)
      inc hl
      ld d, (hl)
      ex de, hl
      ld de, (_clock_tick_count)
      ld (hl), e
      inc hl
      ld (hl), d
      inc hl
      ld de, (_presents)
      ld (hl), e
      inc hl
      ld (hl), d
      inc hl
      ld de, (_overruns)
      ld (hl), e
      inc hl
      ld (hl), d
      inc hl
      ld a, (_pending_max)
      ld (hl), a
      pop af
      jp po, 008$
      ei
   008$:
      ret
   __endasm;
}
