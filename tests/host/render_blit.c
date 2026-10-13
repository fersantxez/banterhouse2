#include "../../src/render/render_g.h"
#include "../../src/platform/banks.h"
#include <stdio.h>

static uint8_t screen[RENDER_G_SCREEN_BYTES];
static uint8_t backgrounds[RENDER_G_SCREEN_BYTES * 8u];
static uint8_t sprites[RENDER_G_MAX_ACTORS][576];

/* render_g_present is not called by this host adapter; these stubs satisfy
 * its CPC bank boundary while exercising the same pixel blitter. */
uint8_t bank_current(void) { return BANK_C0; }
uint8_t bank_depth(void) { return 0; }
BankResult bank_enter(uint8_t config) { (void)config; return BANK_OK; }
BankResult bank_leave(void) { return BANK_OK; }
void cpct_waitVSYNC(void) {}
void cpct_setVideoMemoryPage(uint8_t page) { (void)page; }

static int read_exact(FILE* file, void* data, size_t bytes) {
   return fread(data, 1, bytes, file) == bytes;
}

static uint16_t read_u16(FILE* file, int* ok) {
   uint8_t bytes[2];
   if (!read_exact(file, bytes, 2)) { *ok = 0; return 0; }
   return (uint16_t)(bytes[0] | ((uint16_t)bytes[1] << 8));
}

int main(int argc, char** argv) {
   FILE *inputs, *vectors, *output;
   uint16_t frame_count, frame;
   int ok = 1;
   if (argc != 4) return 2;
   inputs = fopen(argv[1], "rb");
   vectors = fopen(argv[2], "rb");
   output = fopen(argv[3], "wb");
   if (!inputs || !vectors || !output) return 3;
   if (!read_exact(inputs, backgrounds, sizeof(backgrounds))) return 4;
   frame_count = read_u16(vectors, &ok);
   if (!ok || frame_count == 0) return 5;
   for (frame = 0; frame < frame_count; ++frame) {
      uint8_t bg_index, count, actor;
      uint8_t widths[RENDER_G_MAX_ACTORS];
      uint8_t heights[RENDER_G_MAX_ACTORS];
      int16_t xs[RENDER_G_MAX_ACTORS], ys[RENDER_G_MAX_ACTORS];
      if (!read_exact(vectors, &bg_index, 1) || bg_index > 7 ||
          !read_exact(vectors, &count, 1) || count > RENDER_G_MAX_ACTORS)
         return 6;
      for (actor = 0; actor < count; ++actor) {
         uint8_t header[6], width, height;
         uint16_t bytes;
         if (!read_exact(vectors, header, sizeof(header))) return 7;
         xs[actor] = (int16_t)(header[0] | ((uint16_t)header[1] << 8));
         ys[actor] = (int16_t)(header[2] | ((uint16_t)header[3] << 8));
         width = header[4];
         height = header[5];
         if (width == 0 || width > 9 || height == 0 || height > 32) return 8;
         widths[actor] = width;
         heights[actor] = height;
         bytes = (uint16_t)width * height * 2u;
         if (!read_exact(vectors, sprites[actor], bytes)) return 9;
      }
      {
         const uint8_t* background = backgrounds + (uint16_t)bg_index * RENDER_G_SCREEN_BYTES;
         uint16_t i;
         for (i = 0; i < RENDER_G_SCREEN_BYTES; ++i) screen[i] = background[i];
      }
      for (actor = 0; actor < count; ++actor) {
         if (render_g_blit_masked(sprites[actor], widths[actor], heights[actor],
                                  xs[actor], ys[actor], screen) != RENDER_G_OK)
            return 10;
      }
      if (fwrite(screen, 1, sizeof(screen), output) != sizeof(screen)) return 11;
   }
   fclose(inputs); fclose(vectors); fclose(output);
   return 0;
}
