#include <cpctelera.h>
#include "input.h"

static uint8_t previous_held;

void input_reset(void) { previous_held = 0; }

void input_sample(InputFrame* frame) {
   uint8_t held = 0;
   cpct_scanKeyboard_f();
   if (cpct_isKeyPressed(Key_CursorLeft) || cpct_isKeyPressed(Joy0_Left)) held |= INPUT_LEFT;
   if (cpct_isKeyPressed(Key_CursorRight) || cpct_isKeyPressed(Joy0_Right)) held |= INPUT_RIGHT;
   if (cpct_isKeyPressed(Key_CursorUp) || cpct_isKeyPressed(Joy0_Up)) held |= INPUT_JUMP;
   if (cpct_isKeyPressed(Key_CursorDown) || cpct_isKeyPressed(Joy0_Down)) held |= INPUT_DOWN;
   if (cpct_isKeyPressed(Key_Space) || cpct_isKeyPressed(Key_X) ||
       cpct_isKeyPressed(Joy0_Fire1)) held |= INPUT_ACTION;
   if (cpct_isKeyPressed(Key_P)) held |= INPUT_PAUSE;
   if (cpct_isKeyPressed(Key_R)) held |= INPUT_RESTART;
   input_derive(held, previous_held, frame);
   previous_held = held;
}
