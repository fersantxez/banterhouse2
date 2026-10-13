#include <assert.h>
#include <stdio.h>
#include "audio.h"

static AudioEvent played[64];
static unsigned played_count;
static int music_paused;

void sfx_init(void) {}
void sfx_mute(void) {}
void music_init(void) {}
void music_tick(void) {}
void music_toggle(void) {}
void music_pause(void) { music_paused = 1; }
void music_resume(void) { music_paused = 0; }
static void record(AudioEvent event) { assert(played_count < 64); played[played_count++] = event; }
void sfx_step(void) { record(AUDIO_EVENT_STEP); }
void sfx_jump(void) { record(AUDIO_EVENT_JUMP); }
void sfx_seal(void) { record(AUDIO_EVENT_SEAL); }
void sfx_land(void) { record(AUDIO_EVENT_LAND); }
void sfx_return(void) { record(AUDIO_EVENT_RETURN); }
void sfx_hit(void) { record(AUDIO_EVENT_DAMAGE); }
void sfx_machine(void) { record(AUDIO_EVENT_MACHINE); }

static unsigned run_cadence(unsigned presentation_period, AudioEvent *out) {
   unsigned tick, presents = 0, count;
   played_count = 0;
   audio_init();
   for (tick = 0; tick < 120; ++tick) {
      if (tick == 5) audio_request(AUDIO_EVENT_JUMP);
      if (tick == 20) audio_request(AUDIO_EVENT_STEP);
      if (tick == 21) audio_request(AUDIO_EVENT_STEP);
      if (tick == 40) {
         audio_request(AUDIO_EVENT_STEP);
         audio_request(AUDIO_EVENT_RETURN);
         audio_request(AUDIO_EVENT_DAMAGE);
      }
      audio_tick();
      if ((tick + 1) % presentation_period == 0) ++presents;
   }
   assert(presents == 120 / presentation_period);
   count = played_count;
   for (tick = 0; tick < count; ++tick) out[tick] = played[tick];
   return count;
}

int main(void) {
   AudioQueue queue;
   AudioEvent at_50hz[64], at_25hz[64];
   unsigned n50, n25, i;

   audio_queue_reset(&queue);
   assert(audio_queue_push(&queue, AUDIO_EVENT_STEP));
   assert(audio_queue_push(&queue, AUDIO_EVENT_RETURN));
   assert(audio_queue_push(&queue, AUDIO_EVENT_DAMAGE));
   assert(audio_queue_take(&queue) == AUDIO_EVENT_DAMAGE);
   assert(queue.count == 0);

   audio_queue_reset(&queue);
   for (i = 0; i < AUDIO_QUEUE_CAPACITY; ++i)
      assert(audio_queue_push(&queue, AUDIO_EVENT_STEP));
   assert(audio_queue_push(&queue, AUDIO_EVENT_DAMAGE));
   assert(queue.overflow_count == 1);
   assert(audio_queue_take(&queue) == AUDIO_EVENT_DAMAGE);
   assert(queue.overflow_count == 1);

   audio_init();
   assert(!music_paused);
   audio_music_pause();
   assert(music_paused);
   audio_music_resume();
   assert(!music_paused);
   audio_request(AUDIO_EVENT_JUMP);
   audio_cancel();
   played_count = 0;
   audio_tick();
   assert(played_count == 0);
   for (i = 0; i < AUDIO_QUEUE_CAPACITY; ++i) audio_request(AUDIO_EVENT_STEP);
   audio_request(AUDIO_EVENT_DAMAGE);
   assert(audio_overflows() == 1);
   audio_cancel();
   assert(audio_overflows() == 1);

   n50 = run_cadence(1, at_50hz);
   n25 = run_cadence(2, at_25hz);
   assert(n50 == n25);
   for (i = 0; i < n50; ++i) assert(at_50hz[i] == at_25hz[i]);
   assert(n50 == 4);
   assert(at_50hz[0] == AUDIO_EVENT_JUMP);
   assert(at_50hz[1] == AUDIO_EVENT_STEP);
   assert(at_50hz[2] == AUDIO_EVENT_STEP);
   assert(at_50hz[3] == AUDIO_EVENT_DAMAGE);
   puts("PASS AY event priority, bounded overflow, retry cancellation and identical 50/25-present audio traces");
   return 0;
}
