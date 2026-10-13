#ifndef BH2_CLOCK_H
#define BH2_CLOCK_H
#include <stdint.h>

typedef struct {
   uint16_t ticks;
   uint8_t pending;
} ClockSnapshot;

extern volatile uint16_t clock_tick_count;
extern volatile uint16_t clock_irq_count;

void clock_init(void);
void clock_stop(void);
uint16_t clock_ticks(void);
uint16_t clock_interrupts(void);
uint8_t clock_pending(void);
uint8_t clock_pop_tick(void);
uint8_t clock_wait_vsync_edge(void);

#endif
