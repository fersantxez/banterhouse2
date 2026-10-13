#include "machine.h"
#include <assert.h>
#include <stdio.h>

static Machine machines[MACHINE_POOL_SIZE];
static Projectile papers[PROJECTILE_POOL_SIZE];

static void reset(void) {
   machine_pool_reset(machines, papers);
   machine_init(&machines[0], 42, 184, 0, 50, 15, 76);
}

static void test_cadence_and_next_tick_motion(void) {
   unsigned tick;
   uint8_t slot;
   int16_t x, trajectory[3];
   reset();
   for (tick = 1; tick <= 50; ++tick) {
      assert(machine_tick(&machines[0], papers) == MACHINE_EVENT_NONE);
      assert(machines[0].state == MACHINE_IDLE);
   }
   assert(machines[0].wait == 0);
   assert(machine_tick(&machines[0], papers) == MACHINE_EVENT_WARNING);
   assert(machines[0].state == MACHINE_WARNING);
   slot = machines[0].reserved_slot;
   assert(slot < PROJECTILE_POOL_SIZE && papers[slot].state == PROJECTILE_RESERVED);
   for (tick = 1; tick < 15; ++tick) {
      assert(machine_tick(&machines[0], papers) == MACHINE_EVENT_NONE);
      assert(machines[0].state == MACHINE_WARNING);
   }
   assert(machine_tick(&machines[0], papers) == MACHINE_EVENT_NONE);
   assert(machines[0].state == MACHINE_FIRE);
   assert(machine_tick(&machines[0], papers) == MACHINE_EVENT_FIRED);
   assert(papers[slot].state == PROJECTILE_HOSTILE && papers[slot].live);
   assert(papers[slot].xq == 84 && papers[slot].y == 172);
   x = papers[slot].xq;
   projectile_tick(&papers[slot], 3, 5); /* same presentation tick as spawn */
   assert(papers[slot].xq == x && papers[slot].born == 0);
   projectile_tick(&papers[slot], 3, 5);
   assert(papers[slot].xq == x - 3);
   trajectory[0] = papers[slot].xq;
   projectile_tick(&papers[slot], 3, 5);
   assert(papers[slot].xq == x - 6);
   trajectory[1] = papers[slot].xq;
   projectile_tick(&papers[slot], 3, 5);
   trajectory[2] = papers[slot].xq;
   assert(trajectory[0] == 81 && trajectory[1] == 78 && trajectory[2] == 75);
   printf("M01 projectile xq trace: %d,%d,%d\n",
          trajectory[0], trajectory[1], trajectory[2]);
}

static void test_saturation_defers_without_evicting(void) {
   uint8_t i;
   MachineEvent event;
   machine_pool_reset(machines, papers);
   for (i = 0; i < PROJECTILE_POOL_SIZE; ++i) {
      assert(projectile_reserve(papers) == i);
      papers[i].xq = (int16_t)(20 + i);
   }
   for (i = 0; i < MACHINE_POOL_SIZE; ++i)
      machine_init(&machines[i], (uint8_t)(20 + i * 20), 184, i & 1, 0, 15, 76);
   for (i = 0; i < MACHINE_POOL_SIZE; ++i) {
      event = machine_tick(&machines[i], papers);
      assert(event == MACHINE_EVENT_NONE);
      assert(machines[i].state == MACHINE_IDLE && machines[i].wait == 0);
   }
   for (i = 0; i < PROJECTILE_POOL_SIZE; ++i) {
      assert(papers[i].state == PROJECTILE_RESERVED);
      assert(papers[i].xq == 20 + i);
   }
   projectile_release(papers, 2);
   assert(machine_tick(&machines[1], papers) == MACHINE_EVENT_WARNING);
   assert(machines[1].reserved_slot == 2);
   assert(papers[0].state == PROJECTILE_RESERVED);
   assert(papers[1].state == PROJECTILE_RESERVED);
   assert(papers[2].state == PROJECTILE_RESERVED);
   assert(papers[3].state == PROJECTILE_RESERVED);
}

static void test_turn_off_and_restart_release_reservations(void) {
   uint8_t slot;
   reset();
   machines[0].wait = 0;
   assert(machine_tick(&machines[0], papers) == MACHINE_EVENT_WARNING);
   slot = machines[0].reserved_slot;
   assert(papers[slot].state == PROJECTILE_RESERVED);
   machine_turn_off(&machines[0], papers);
   assert(machines[0].state == MACHINE_OFF && !machines[0].live);
   assert(papers[slot].state == PROJECTILE_FREE && !papers[slot].live);
   assert(machine_tick(&machines[0], papers) == MACHINE_EVENT_NONE);
   machine_pool_reset(machines, papers);
   for (slot = 0; slot < PROJECTILE_POOL_SIZE; ++slot)
      assert(papers[slot].state == PROJECTILE_FREE && !papers[slot].live);
   for (slot = 0; slot < MACHINE_POOL_SIZE; ++slot)
      assert(machines[slot].state == MACHINE_OFF && !machines[slot].live);
   slot = projectile_reserve(papers);
   assert(slot == 0);
   projectile_fire(papers, slot, 1, 100, 1);
   projectile_release(papers, slot);
   assert(papers[slot].state == PROJECTILE_FREE);
   assert(projectile_reserve(papers) == slot);
}

int main(void) {
   test_cadence_and_next_tick_motion();
   test_saturation_defers_without_evicting();
   test_turn_off_and_restart_release_reservations();
   puts("PASS: T11 M01-M03, pool de cuatro, reserva, disparo y reinicio");
   return 0;
}
