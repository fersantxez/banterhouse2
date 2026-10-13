#ifndef BH2_BANKS_H
#define BH2_BANKS_H

#include <stdint.h>

#define BANK_WINDOW_BASE 0x4000u
#define BANK_WINDOW_SIZE 0x4000u
#define BANK_COPY_CHUNK 32u
#define BANK_MAX_DEPTH 4u

typedef enum {
   BANK_C0 = 0,
   BANK_C4 = 4,
   BANK_C5 = 5,
   BANK_C6 = 6,
   BANK_C7 = 7
} BankConfig;

typedef enum {
   BANK_OK = 0,
   BANK_ERR_CONFIG,
   BANK_ERR_DEPTH,
   BANK_ERR_UNBALANCED,
   BANK_ERR_HANDLE,
   BANK_ERR_RANGE,
   BANK_ERR_STALE,
   BANK_ERR_SAME_BANK,
   BANK_ERR_GENERATION_EXHAUSTED
} BankResult;

/* Offsets are relative to the 16 KiB bank window at &4000. */
typedef struct {
   uint8_t bank;
   uint16_t offset;
   uint16_t length;
   uint16_t generation;
} BankHandle;

void bank_init(void);
BankResult bank_enter(uint8_t config);
BankResult bank_leave(void);
uint8_t bank_current(void);
uint8_t bank_depth(void);

BankResult bank_handle_make(uint8_t bank, uint16_t offset, uint16_t length,
                            BankHandle* out);
BankResult bank_invalidate(uint8_t bank);
BankResult bank_copy(BankHandle src, BankHandle dst, uint16_t length);

#endif
