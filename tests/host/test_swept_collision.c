#include "collision.h"
#include <assert.h>
#include <stdio.h>

static void test_sweep(void) {
   uint16_t t;
   assert(collision_sweep_aabb(-4, 0, 4, 0, 1, 1,
                               0, 0, 0, 0, 1, 1, &t));
   assert(t >= 24575 && t <= 24577); /* first contact at 3/8 */
   assert(collision_sweep_aabb(0, 0, 10, 0, 1, 1,
                               10, 0, 0, 0, 1, 1, &t));
   assert(t >= 29490 && t <= 29492); /* relative movement: 9/20 */
   assert(collision_sweep_aabb(0, 0, 0, 0, 2, 2,
                               2, 2, 2, 2, 2, 2, &t) && t == 0);
   assert(!collision_sweep_aabb(-4, 4, 4, 4, 1, 1,
                                0, 0, 0, 0, 1, 1, &t));
}

int main(void) {
   test_sweep();
   puts("PASS: relative swept AABB, exact edge start, crossing and vertical miss");
   return 0;
}
