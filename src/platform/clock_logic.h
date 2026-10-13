#ifndef BH2_CLOCK_LOGIC_H
#define BH2_CLOCK_LOGIC_H
#include <stdint.h>
uint8_t clock_is_overrun(uint8_t pending);
uint16_t clock_elapsed(uint16_t newer, uint16_t older);
#endif
