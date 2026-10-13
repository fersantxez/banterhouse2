#include "input_logic.h"

void input_derive(uint8_t held, uint8_t previous, InputFrame* frame) {
   frame->held = held;
   frame->pressed = (uint8_t)(held & (uint8_t)~previous);
   frame->released = (uint8_t)(previous & (uint8_t)~held);
}
