#ifndef BH2_RENDER_G_H
#define BH2_RENDER_G_H

#include <stdint.h>

#define RENDER_G_MAX_ACTORS 4u
#define RENDER_G_WIDTH 160
#define RENDER_G_HEIGHT 200
#define RENDER_G_SCREEN_BYTES 0x4000u

typedef enum {
   RENDER_G_OK = 0,
   RENDER_G_ERR_ARGUMENT,
   RENDER_G_ERR_STATE,
   RENDER_G_ERR_SPRITE,
   RENDER_G_ERR_BANK
} RenderGResult;

/* Variant order is [pose][facing-left?][x-odd?]. Offsets refer to the
 * selected expansion bank's 16 KiB window, never to a retained pointer. */
typedef struct {
   uint8_t bank;
   uint8_t pose_count;
   uint8_t height;
   uint16_t variant_offset[2][2][2];
} RenderGSprite;

typedef struct {
   const RenderGSprite* sprite;
   int16_t x;
   int16_t y;
   uint8_t pose;
   uint8_t facing_left;
   uint8_t layer;
   uint8_t id;
   uint8_t visible;
} RenderGActor;

/* Full-background baseline G: RAM1 is restored to the RAM2 back page, then
 * every visible actor is drawn in stable (layer,id,input-index) order. The
 * CRTC flips RAM2/RAM3 at VSYNC when the complete frame is ready. */
RenderGResult render_g_init(void);
RenderGResult render_g_present(const RenderGActor* actors, uint8_t count);
uint16_t render_g_visible_base(void);

/* Shared pixel compositor used by the CPC bank adapter and host differential
 * tests. source points to exactly one precomputed masked variant. */
RenderGResult render_g_blit_masked(const volatile uint8_t* source,
                                  uint8_t width_bytes, uint8_t height,
                                  int16_t x, int16_t y,
                                  volatile uint8_t* screen);

/* Persistent byte update in the clean RAM1 background image. */
RenderGResult render_g_background_write(uint16_t screen_offset, uint8_t value);

#endif
