#include <cpctelera.h>
#include <stdint.h>

extern uint16_t disk_prepare(void);
extern uint16_t disk_load_ch1(void);
extern uint16_t disk_load_ch2(void);
extern void disk_cache_workspace_save(void);
extern void disk_cache_workspace_restore(void);
extern void zx0_from_c(const uint8_t* source, uint8_t* destination);
uint8_t disk_load_error;

static uint16_t firmware_handler;
static uint8_t jumpblock_cached;
static uint8_t init_attempts;
static uint8_t result;

static void mark(uint8_t colour) { cpct_setBorder(colour); }

static uint8_t reinitialize_amsdos(void) {
   uint8_t ready;
   if (jumpblock_cached) disk_cache_workspace_restore();
   mark(0x0C);
   cpct_enableUpperROM();
   mark(0x05);
   cpct_reenableFirmware(firmware_handler);
   mark(++init_attempts == 1 ? 0x06 : 0x13);
   ready = disk_prepare() != 0;
   mark(0x12);
   firmware_handler = cpct_disableFirmware();
   cpct_disableUpperROM();
   if (ready) {
      disk_cache_workspace_save();
      jumpblock_cached = 1;
      mark(0x13);
   }
   return ready;
}

static uint16_t load_chapter(uint8_t chapter) {
   uint16_t loaded;
   cpct_enableUpperROM();
   cpct_reenableFirmware(firmware_handler);
   mark(0x14);
   loaded = chapter == 1 ? disk_load_ch1() : disk_load_ch2();
   mark(0x15);
   firmware_handler = cpct_disableFirmware();
   cpct_disableUpperROM();
   return loaded;
}

void main(void) {
   firmware_handler = cpct_disableFirmware();
   cpct_setStackLocation((void*)0x7ff0);
   cpct_setVideoMode(0);
   mark(0x01);
   /* The production BIN has no CRT to clear static/BSS storage. */
   jumpblock_cached = 0;
   init_attempts = 0;
   result = 0;
   if (reinitialize_amsdos() && load_chapter(1)) {
      /* Production's expanded background copy overwrites &A6FC..&BFFF. */
      cpct_memcpy((void*)0x8000, (void*)0xc000, 0x4000);
      if (reinitialize_amsdos() && load_chapter(2) &&
          ((volatile uint8_t*)0x8000)[4] == 0xCF &&
          ((volatile uint8_t*)0x8000)[5] == 0x04) {
         zx0_from_c((const uint8_t*)0x8000, (uint8_t*)0xc000);
         result = (((volatile uint8_t*)0xc000)[0] == 0x00 &&
                   ((volatile uint8_t*)0xc000)[1] == 0x00) ? 1 : 2;
      }
   }

   /* Green = CH02 reloaded and decoded; red = AMSDOS/read/check failed;
      cyan = read succeeded but decoded screen signature mismatched. */
   if (result == 1) cpct_setPALColour(9, 0x12);
   else if (result == 2) cpct_setPALColour(10, 0x13);
   else cpct_setPALColour(6, 0x0C);
   cpct_memset((void*)0xc000,
      cpct_px2byteM0(result == 1 ? 9 : result == 2 ? 10 : 6,
                     result == 1 ? 9 : result == 2 ? 10 : 6), 0x4000);
   for (;;) { }
}
