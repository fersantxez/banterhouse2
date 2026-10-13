#ifndef BH2_INPUT_LOGIC_H
#define BH2_INPUT_LOGIC_H
#include <stdint.h>

enum {
   INPUT_LEFT = 1, INPUT_RIGHT = 2, INPUT_JUMP = 4, INPUT_DOWN = 8,
   INPUT_ACTION = 16, INPUT_PAUSE = 32, INPUT_RESTART = 64
};

typedef struct {
   uint8_t held;
   uint8_t pressed;
   uint8_t released;
} InputFrame;

void input_derive(uint8_t held, uint8_t previous, InputFrame* frame);

#endif
