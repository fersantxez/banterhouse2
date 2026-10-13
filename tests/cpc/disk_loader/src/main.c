#include <cpctelera.h>
#include <stdint.h>

extern uint16_t disk_load_ch1(void);
extern void sfx_init(void);
extern void music_init(void);

void main(void) {
   /* Mirror the production splash's firmware/stack handoff. An automatic
      local would be lost when SP is moved, so preserve the handler in RAM. */
   static uint16_t firmware_handler;
   firmware_handler = cpct_disableFirmware();
   cpct_setStackLocation((void*)0x7ff0);
   cpct_setVideoMode(0);
   cpct_reenableFirmware(firmware_handler);
   /* Keep the real title's AY setup before its first CAS file read. */
   sfx_init();
   music_init();
   if (!disk_load_ch1() ||
       ((const volatile uint8_t*)0x8000)[0] != 0x81 ||
       ((const volatile uint8_t*)0x8000)[1] != 0x00 ||
       ((const volatile uint8_t*)0x8000)[2] != 0x55) {
      cpct_disableFirmware();
      cpct_setPALColour(0, 0x04);
      cpct_memset((void*)0xc000, cpct_px2byteM0(0, 0), 0x4000);
   } else {
      cpct_disableFirmware();
      cpct_setPALColour(1, 0x1a);
      cpct_memset((void*)0xc000, cpct_px2byteM0(1, 1), 0x4000);
   }
   for (;;) { }
}
