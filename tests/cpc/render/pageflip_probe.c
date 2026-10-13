#include <cpctelera.h>
#include <stdint.h>

static void probe_main(void) {
   volatile uint8_t* buffer = (volatile uint8_t*)0x8000;
   uint16_t i;
   cpct_disableFirmware();
   cpct_setVideoMode(0);
   for (i = 0; i < 0x4000u; ++i) buffer[i] = 0xff;
   cpct_setVideoMemoryPage(cpct_page80);
   while (1) cpct_waitVSYNC();
}

void main(void) __naked {
   __asm
      ld sp, #0x3f00
      jp _probe_main
   __endasm;
}
