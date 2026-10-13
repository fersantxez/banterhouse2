#include <cpctelera.h>
#include <stdint.h>

extern uint16_t boot_abi_probe(uint16_t a, uint16_t b);
extern void boot_stack_fill(void);
extern uint16_t boot_stack_free(void);

volatile uint16_t stack_probe_limit;

void main(void) {
   u8 ok;
   cpct_disableFirmware();
   cpct_setStackLocation((void*)0x7ff0);
   boot_stack_fill();
   cpct_setVideoMode(0);

   /* The two geometries are a visible pass/fail marker in every palette. */
   ok = (boot_abi_probe(0x1234, 0x6f08) == 0x7d3c && boot_stack_free() >= 256);
   cpct_drawSolidBox(CPCT_VMEM_START + (ok ? 0x1800 : 0x2800),
      cpct_px2byteM0(ok ? 11 : 3, ok ? 11 : 3), ok ? 8 : 32, ok ? 8 : 16);
   while (1) cpct_waitVSYNC();
}
