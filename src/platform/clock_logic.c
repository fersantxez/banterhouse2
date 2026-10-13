#include "clock_logic.h"

uint8_t clock_is_overrun(uint8_t pending) { return (uint8_t)(pending > 2); }
uint16_t clock_elapsed(uint16_t newer, uint16_t older) {
   return (uint16_t)(newer - older);
}
