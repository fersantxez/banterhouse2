#include "audio.h"

static AudioQueue queue;
static uint8_t tone_ticks;

extern void sfx_step(void), sfx_jump(void), sfx_seal(void), sfx_land(void);
extern void sfx_return(void), sfx_hit(void), sfx_machine(void), sfx_mute(void);
extern void sfx_init(void);
extern void music_init(void), music_tick(void), music_toggle(void);
extern void music_pause(void), music_resume(void);

void audio_init(void) {
   audio_queue_reset(&queue);
   tone_ticks = 0;
   sfx_init();
   music_init();
}

void audio_request(AudioEvent event) {
   (void)audio_queue_push(&queue, event);
}

static uint8_t duration(AudioEvent event) {
   switch (event) {
      case AUDIO_EVENT_STEP: return 2;
      case AUDIO_EVENT_SEAL: return 3;
      case AUDIO_EVENT_LAND: return 3;
      case AUDIO_EVENT_JUMP: return 5;
      case AUDIO_EVENT_RETURN: return 6;
      case AUDIO_EVENT_MACHINE: return 8;
      case AUDIO_EVENT_DAMAGE: return 10;
      default: return 0;
   }
}

static void play(AudioEvent event) {
   switch (event) {
      case AUDIO_EVENT_STEP: sfx_step(); break;
      case AUDIO_EVENT_SEAL: sfx_seal(); break;
      case AUDIO_EVENT_LAND: sfx_land(); break;
      case AUDIO_EVENT_JUMP: sfx_jump(); break;
      case AUDIO_EVENT_RETURN: sfx_return(); break;
      case AUDIO_EVENT_MACHINE: sfx_machine(); break;
      case AUDIO_EVENT_DAMAGE: sfx_hit(); break;
      case AUDIO_EVENT_ARENA_CLEAR: sfx_mute(); break;
      default: break;
   }
}

void audio_tick(void) {
   AudioEvent event = audio_queue_take(&queue);
   music_tick();
   if (event != AUDIO_EVENT_NONE) {
      play(event);
      tone_ticks = duration(event);
   } else if (tone_ticks && --tone_ticks == 0) {
      sfx_mute();
   }
}

void audio_cancel(void) {
   audio_queue_clear(&queue);
   tone_ticks = 0;
   sfx_mute();
}

void audio_music_toggle(void) { music_toggle(); }
void audio_music_pause(void) { music_pause(); }
void audio_music_resume(void) { music_resume(); }

uint16_t audio_overflows(void) { return queue.overflow_count; }
