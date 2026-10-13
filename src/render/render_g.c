#include "render_g.h"
#include "../platform/banks.h"

#define cpct_pageC0 0x30u
#define cpct_page80 0x20u
#ifdef __SDCC
extern void cpct_waitVSYNC(void);
extern void cpct_setVideoMemoryPage(uint8_t page) __z88dk_fastcall;
#else
extern void cpct_waitVSYNC(void);
extern void cpct_setVideoMemoryPage(uint8_t page);
#endif

#define RENDER_G_BACKGROUND_BASE 0x4000u
#define RENDER_G_VIDEO_BASE 0xc000u
#define RENDER_G_ROW_BYTES 80u
#define RENDER_G_VARIANTS_PER_ROW 2u

/* Render in the RAM2 back page and switch the CRTC between RAM2 and RAM3 at
 * VSYNC. Keep code, manager state and stack in fixed RAM0. */
static uint16_t render_front_base;
static uint16_t render_back_base;

static uint8_t sprite_variant_width(uint8_t x_odd) {
   return (uint8_t)(8u + x_odd);
}

static uint8_t actor_valid(const RenderGActor* actor) {
   const RenderGSprite* sprite;
   uint8_t x_odd, facing, pose;
   if (!actor || !actor->sprite || !actor->visible) return 1;
   sprite = actor->sprite;
   if (sprite->bank < 4 || sprite->bank > 7 || sprite->pose_count == 0 ||
       sprite->pose_count > 2 || sprite->height == 0 || sprite->height > 32 ||
       actor->pose >= sprite->pose_count || actor->facing_left > 1)
      return 0;
   for (pose = 0; pose < sprite->pose_count; ++pose) {
      for (facing = 0; facing < 2; ++facing) {
         for (x_odd = 0; x_odd < 2; ++x_odd) {
            uint16_t offset = sprite->variant_offset[pose][facing][x_odd];
            uint16_t bytes = (uint16_t)sprite_variant_width(x_odd) *
                             (uint16_t)sprite->height * 2u;
            if (offset >= BANK_WINDOW_SIZE ||
                bytes > (uint16_t)(BANK_WINDOW_SIZE - offset))
               return 0;
         }
      }
   }
   return 1;
}

static RenderGResult draw_actor(const RenderGActor* actor,
                                volatile uint8_t* screen) {
   const RenderGSprite* sprite = actor->sprite;
   volatile const uint8_t* source;
   uint8_t x_odd, width;
   uint16_t source_offset;
   BankResult bank_result;

   x_odd = (uint8_t)(actor->x & 1);
   width = sprite_variant_width(x_odd);
   source_offset = sprite->variant_offset[actor->pose][actor->facing_left][x_odd];
   bank_result = bank_enter(sprite->bank);
   if (bank_result != BANK_OK) return RENDER_G_ERR_BANK;
   source = (volatile const uint8_t*)(uintptr_t)(BANK_WINDOW_BASE + source_offset);
   if (render_g_blit_masked(source, width, sprite->height,
                            actor->x, actor->y, screen) != RENDER_G_OK) {
      (void)bank_leave();
      return RENDER_G_ERR_SPRITE;
   }
   if (bank_leave() != BANK_OK) return RENDER_G_ERR_BANK;
   return RENDER_G_OK;
}

RenderGResult render_g_blit_masked(const volatile uint8_t* source,
                                  uint8_t width_bytes, uint8_t height,
                                  int16_t x, int16_t y,
                                  volatile uint8_t* screen) {
   int16_t byte_x = (int16_t)(x >> 1);
   uint8_t row;
   if (!source || !screen || width_bytes == 0 || width_bytes > 9 ||
       height == 0 || height > 32)
      return RENDER_G_ERR_ARGUMENT;
   for (row = 0; row < height; ++row) {
      int16_t dest_y = (int16_t)(y + row);
      uint8_t col;
      if (dest_y < 0 || dest_y >= RENDER_G_HEIGHT) continue;
      for (col = 0; col < width_bytes; ++col) {
         int16_t dest_x = (int16_t)(byte_x + col);
         uint16_t address, source_index;
         uint8_t mask, pixels;
         if (dest_x < 0 || dest_x >= (int16_t)RENDER_G_ROW_BYTES) continue;
         address = (uint16_t)((uint16_t)(dest_y & 7) * 0x0800u +
                   (uint16_t)(dest_y >> 3) * RENDER_G_ROW_BYTES +
                   (uint16_t)dest_x);
         source_index = (uint16_t)row * width_bytes * RENDER_G_VARIANTS_PER_ROW +
                        (uint16_t)col * RENDER_G_VARIANTS_PER_ROW;
         mask = source[source_index];
         pixels = source[(uint16_t)(source_index + 1u)];
         screen[address] = (uint8_t)((screen[address] & mask) | pixels);
      }
   }
   return RENDER_G_OK;
}

RenderGResult render_g_background_write(uint16_t screen_offset, uint8_t value) {
   volatile uint8_t* background = (volatile uint8_t*)RENDER_G_BACKGROUND_BASE;
   if (screen_offset >= RENDER_G_SCREEN_BYTES) return RENDER_G_ERR_ARGUMENT;
   if (bank_current() != BANK_C0 || bank_depth() != 0) return RENDER_G_ERR_STATE;
   background[screen_offset] = value;
   return RENDER_G_OK;
}

RenderGResult render_g_init(void) {
   if (bank_current() != BANK_C0 || bank_depth() != 0)
      return RENDER_G_ERR_STATE;
   render_front_base = RENDER_G_VIDEO_BASE;
   render_back_base = 0x8000u;
   cpct_setVideoMemoryPage(cpct_pageC0);
   return RENDER_G_OK;
}

RenderGResult render_g_present(const RenderGActor* actors, uint8_t count) {
   volatile const uint8_t* background = (volatile const uint8_t*)RENDER_G_BACKGROUND_BASE;
   volatile uint8_t* screen = (volatile uint8_t*)(uintptr_t)render_back_base;
   uint8_t order[RENDER_G_MAX_ACTORS];
   uint8_t i, j;
   uint16_t offset;

   if ((count && !actors) || count > RENDER_G_MAX_ACTORS)
      return RENDER_G_ERR_ARGUMENT;
   if (bank_current() != BANK_C0 || bank_depth() != 0)
      return RENDER_G_ERR_STATE;
   for (i = 0; i < count; ++i) {
      if (actors[i].visible && !actor_valid(&actors[i]))
         return RENDER_G_ERR_SPRITE;
      order[i] = i;
   }
   /* Stable insertion sort: lower layer first, then stable actor ID; ties
    * retain caller order. Restoration is the full background copy above, so
    * overlapping old boxes cannot erase a current actor. */
   for (i = 1; i < count; ++i) {
      uint8_t current = order[i];
      j = i;
      while (j > 0) {
         const RenderGActor* left = &actors[order[j - 1u]];
         const RenderGActor* right = &actors[current];
         if (left->layer < right->layer ||
             (left->layer == right->layer && left->id <= right->id))
            break;
         order[j] = order[j - 1u];
         --j;
      }
      order[j] = current;
   }
   for (offset = 0; offset < RENDER_G_SCREEN_BYTES; ++offset)
      screen[offset] = background[offset];
   for (i = 0; i < count; ++i) {
      const RenderGActor* actor = &actors[order[i]];
      RenderGResult result;
      if (!actor->visible) continue;
      result = draw_actor(actor, (volatile uint8_t*)screen);
      if (result != RENDER_G_OK) return result;
   }
   cpct_waitVSYNC();
   cpct_setVideoMemoryPage(render_back_base == 0x8000u ? cpct_page80 : cpct_pageC0);
   render_front_base = render_back_base;
   render_back_base = render_front_base == 0x8000u ? RENDER_G_VIDEO_BASE : 0x8000u;
   return RENDER_G_OK;
}

uint16_t render_g_visible_base(void) {
   return render_front_base;
}
