#include <assert.h>
#include <stdint.h>
#include "../src/platform/input_logic.h"
#include "../src/platform/clock_logic.h"

int main(void) {
   InputFrame f;
   const uint8_t sequence[] = {0, INPUT_LEFT, INPUT_LEFT, 0, INPUT_LEFT, 0};
   uint8_t previous = 0;
   uint8_t i;
   for (i = 0; i < sizeof(sequence); ++i) {
      input_derive(sequence[i], previous, &f);
      if (i == 1) assert(f.pressed == INPUT_LEFT && f.released == 0);
      if (i == 2) assert(f.pressed == 0 && f.released == 0);
      if (i == 3) assert(f.pressed == 0 && f.released == INPUT_LEFT);
      if (i == 4) assert(f.pressed == INPUT_LEFT && f.released == 0);
      if (i == 5) assert(f.pressed == 0 && f.released == INPUT_LEFT);
      assert(f.held == sequence[i]);
      previous = sequence[i];
   }
   input_derive(INPUT_LEFT | INPUT_RIGHT, 0, &f);
   assert(f.pressed == (INPUT_LEFT | INPUT_RIGHT));
   assert(f.held == (INPUT_LEFT | INPUT_RIGHT) && f.released == 0);
   input_derive(INPUT_LEFT | INPUT_RIGHT, INPUT_LEFT | INPUT_RIGHT, &f);
   assert(f.held == (INPUT_LEFT | INPUT_RIGHT) && f.pressed == 0 && f.released == 0);
   input_derive(0, INPUT_LEFT | INPUT_RIGHT, &f);
   assert(f.held == 0 && f.pressed == 0 && f.released == (INPUT_LEFT | INPUT_RIGHT));
   input_derive(INPUT_JUMP | INPUT_DOWN, 0, &f);
   assert(f.held == (INPUT_JUMP | INPUT_DOWN) &&
          f.pressed == (INPUT_JUMP | INPUT_DOWN) && f.released == 0);
   assert(clock_is_overrun(0) == 0 && clock_is_overrun(2) == 0);
   assert(clock_is_overrun(3) == 1 && clock_is_overrun(255) == 1);
   assert(clock_elapsed(1, 65535) == 2);
   assert(clock_elapsed(100, 99) == 1);
   return 0;
}
