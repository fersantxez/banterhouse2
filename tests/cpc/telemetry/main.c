#include <cpctelera.h>
#include <stdint.h>

typedef struct {
   uint8_t magic[4];
   uint8_t build_id[4];
   uint16_t counter;
   uint8_t sentinels[4];
   uint8_t done;
   uint8_t error;
} O02Evidence;

/* The data linker starts this only global at &3C00; the map is checked before
 * any snapshot is accepted, so a changed layout cannot silently pass.
 */
volatile O02Evidence o02_evidence;

extern void o02_probe_short(void);
extern void o02_probe_long(void);
extern void o02_phase_probe(void);
extern void o02_wait_edge(void);
extern void o02_wait_edges(void);
extern void o02_case_done(void);

void o02_probe_main(void);

void main(void) __naked {
   __asm
      di
      ld sp, #0x3ff0
      jp _o02_probe_main
   __endasm;
}

void o02_probe_main(void) {
   uint16_t i;
   volatile uint8_t* video = (volatile uint8_t*)0xc000u;
   volatile uint8_t* stack_guard = (volatile uint8_t*)0x3e00u;

   cpct_disableFirmware();
   cpct_setVideoMode(0);
   cpct_memset((void*)0xc000u, 0, 0x4000u);
   for (i = 0; i < 0x4000u; ++i)
      video[i] = (uint8_t)(i * 37u + (i >> 4) * 11u + 0x5au);

   o02_evidence.magic[0] = 0xb2;
   o02_evidence.magic[1] = 0x4f;
   o02_evidence.magic[2] = 0x30;
   o02_evidence.magic[3] = 0x32;
   o02_evidence.build_id[0] = 0x26;
   o02_evidence.build_id[1] = 0x20;
   o02_evidence.build_id[2] = 0x02;
   o02_evidence.build_id[3] = 0xb2;
   o02_evidence.counter = 0;
   o02_evidence.sentinels[0] = 0x00;
   o02_evidence.sentinels[1] = 0x55;
   o02_evidence.sentinels[2] = 0xaa;
   o02_evidence.sentinels[3] = 0xff;
   o02_evidence.done = 0;
   o02_evidence.error = 0;
   for (i = 0; i < 128u; ++i) stack_guard[i] = 0xa5;

   o02_probe_short();
   o02_probe_long();
   o02_phase_probe();
   o02_wait_edge();
   o02_wait_edges();

   o02_evidence.counter = 42;
   o02_evidence.done = 0xa5;
   o02_case_done();
}
