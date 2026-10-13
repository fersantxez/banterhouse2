#include <cpctelera.h>

extern const u8 gallery_screen[];
extern const u8 gallery_palette[];

void main(void) {
   u16 i;
   volatile const u8* vram = (volatile const u8*)CPCT_VMEM_START;
   cpct_disableFirmware();
   cpct_setStackLocation((void*)0x7ff0);
   cpct_setVideoMode(0);
   cpct_setPalette((u8*)gallery_palette, 16);
   cpct_memcpy(CPCT_VMEM_START, gallery_screen, 0x4000);
   /* Any VRAM mismatch becomes an unmistakable solid failure screen. */
   for (i = 0; i < 0x4000; ++i) {
      if (vram[i] != gallery_screen[i]) {
         cpct_drawSolidBox(CPCT_VMEM_START, 0xff, 80, 200);
         while (1) cpct_waitVSYNC();
      }
   }
   while (1) cpct_waitVSYNC();
}
