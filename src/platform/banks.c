#include <cpctelera.h>
#include <stdint.h>
#include "banks.h"

/* This shadow and all manager state must be linked to fixed RAM. The isolated
 * CPC fixture enforces that rule; the current full-game linker layout cannot
 * page &4000 safely and is recorded as an architecture integration risk. */
volatile uint8_t bank_current_config;
static uint8_t bank_saved_config[BANK_MAX_DEPTH];
static uint8_t bank_depth_value;
static uint16_t bank_generation[4];
static uint8_t bank_generation_exhausted[4];
static uint8_t bank_scratch[BANK_COPY_CHUNK];

extern void bank_apply_config(uint8_t config) __z88dk_fastcall;

static int8_t bank_index(uint8_t bank) {
   if (bank < 4 || bank > 7) return -1;
   return (int8_t)(bank - 4);
}

static uint8_t config_for_bank(uint8_t bank) {
   return bank;
}

static BankResult handle_validate(BankHandle handle) {
   int8_t index = bank_index(handle.bank);
   if (index < 0 || handle.length == 0 || handle.offset >= BANK_WINDOW_SIZE ||
       handle.length > (uint16_t)(BANK_WINDOW_SIZE - handle.offset))
      return BANK_ERR_HANDLE;
   if (bank_generation_exhausted[(uint8_t)index] ||
       handle.generation != bank_generation[(uint8_t)index])
      return BANK_ERR_STALE;
   return BANK_OK;
}

void bank_init(void) {
   uint8_t i;
   bank_depth_value = 0;
   for (i = 0; i < 4; ++i) {
      bank_generation[i] = 1;
      bank_generation_exhausted[i] = 0;
   }
   bank_apply_config(BANK_C0);
}

BankResult bank_enter(uint8_t config) {
   if (config != BANK_C0 && config != BANK_C4 && config != BANK_C5 &&
       config != BANK_C6 && config != BANK_C7)
      return BANK_ERR_CONFIG;
   if (bank_depth_value >= BANK_MAX_DEPTH) return BANK_ERR_DEPTH;
   bank_saved_config[bank_depth_value] = bank_current_config;
   ++bank_depth_value;
   bank_apply_config(config);
   return BANK_OK;
}

BankResult bank_leave(void) {
   uint8_t next_depth;
   uint8_t config;
   if (bank_depth_value == 0) return BANK_ERR_UNBALANCED;
   next_depth = (uint8_t)(bank_depth_value - 1);
   config = bank_saved_config[next_depth];
   bank_apply_config(config);
   bank_depth_value = next_depth;
   return BANK_OK;
}

uint8_t bank_current(void) { return bank_current_config; }
uint8_t bank_depth(void) { return bank_depth_value; }

BankResult bank_handle_make(uint8_t bank, uint16_t offset, uint16_t length,
                            BankHandle* out) {
   int8_t index = bank_index(bank);
   if (!out) return BANK_ERR_HANDLE;
   out->bank = 0;
   out->offset = 0;
   out->length = 0;
   out->generation = 0;
   if (index < 0) return BANK_ERR_HANDLE;
   if (length == 0 || offset >= BANK_WINDOW_SIZE ||
       length > (uint16_t)(BANK_WINDOW_SIZE - offset))
      return BANK_ERR_RANGE;
   if (bank_generation_exhausted[(uint8_t)index])
      return BANK_ERR_GENERATION_EXHAUSTED;
   out->bank = bank;
   out->offset = offset;
   out->length = length;
   out->generation = bank_generation[(uint8_t)index];
   return BANK_OK;
}

BankResult bank_invalidate(uint8_t bank) {
   int8_t index = bank_index(bank);
   if (index < 0) return BANK_ERR_HANDLE;
   if (bank_generation_exhausted[(uint8_t)index])
      return BANK_ERR_GENERATION_EXHAUSTED;
   if (bank_generation[(uint8_t)index] == 0xFFFFu) {
      bank_generation_exhausted[(uint8_t)index] = 1;
      return BANK_ERR_GENERATION_EXHAUSTED;
   }
   ++bank_generation[(uint8_t)index];
   return BANK_OK;
}

BankResult bank_copy(BankHandle src, BankHandle dst, uint16_t length) {
   uint16_t copied = 0;
   BankResult result;
   if (length == 0) return BANK_OK;
   result = handle_validate(src);
   if (result != BANK_OK) return result;
   result = handle_validate(dst);
   if (result != BANK_OK) return result;
   if (src.bank == dst.bank) return BANK_ERR_SAME_BANK;
   if (length > src.length || length > dst.length) return BANK_ERR_RANGE;

   while (copied < length) {
      uint16_t remaining = (uint16_t)(length - copied);
      uint8_t count = remaining > BANK_COPY_CHUNK ?
                      BANK_COPY_CHUNK : (uint8_t)remaining;
      uint8_t i;
      volatile uint8_t* window = (volatile uint8_t*)BANK_WINDOW_BASE;

      result = bank_enter(config_for_bank(src.bank));
      if (result != BANK_OK) return result;
      for (i = 0; i < count; ++i)
         bank_scratch[i] = window[src.offset + copied + i];
      result = bank_leave();
      if (result != BANK_OK) return result;

      result = bank_enter(config_for_bank(dst.bank));
      if (result != BANK_OK) return result;
      for (i = 0; i < count; ++i)
         window[dst.offset + copied + i] = bank_scratch[i];
      result = bank_leave();
      if (result != BANK_OK) return result;
      copied = (uint16_t)(copied + count);
   }
   return BANK_OK;
}
