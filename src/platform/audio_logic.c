#include "audio_logic.h"

uint8_t audio_event_priority(AudioEvent event) {
   switch (event) {
      case AUDIO_EVENT_STEP: return 1;
      case AUDIO_EVENT_SEAL: return 2;
      case AUDIO_EVENT_LAND: return 3;
      case AUDIO_EVENT_JUMP: return 4;
      case AUDIO_EVENT_RETURN: return 5;
      case AUDIO_EVENT_MACHINE: return 6;
      case AUDIO_EVENT_DAMAGE: return 7;
      case AUDIO_EVENT_ARENA_CLEAR: return 8;
      default: return 0;
   }
}

void audio_queue_reset(AudioQueue *queue) {
   uint8_t i;
   if (!queue) return;
   queue->count = 0;
   queue->overflow_count = 0;
   for (i = 0; i < AUDIO_QUEUE_CAPACITY; ++i) queue->events[i] = AUDIO_EVENT_NONE;
}

void audio_queue_clear(AudioQueue *queue) {
   uint8_t i;
   if (!queue) return;
   queue->count = 0;
   for (i = 0; i < AUDIO_QUEUE_CAPACITY; ++i) queue->events[i] = AUDIO_EVENT_NONE;
}

uint8_t audio_queue_push(AudioQueue *queue, AudioEvent event) {
   uint8_t i, lowest = 0, lowest_priority = 255;
   if (!queue || event <= AUDIO_EVENT_NONE || event > AUDIO_EVENT_ARENA_CLEAR)
      return 0;
   if (queue->count >= AUDIO_QUEUE_CAPACITY) {
      if (queue->overflow_count != 0xffffu) ++queue->overflow_count;
      for (i = 0; i < queue->count; ++i) {
         uint8_t priority = audio_event_priority((AudioEvent)queue->events[i]);
         if (priority < lowest_priority) { lowest = i; lowest_priority = priority; }
      }
      /* A full low-priority queue cannot suppress an incoming critical event. */
      if (audio_event_priority(event) <= lowest_priority) return 0;
      queue->events[lowest] = (uint8_t)event;
      return 1;
   }
   queue->events[queue->count++] = (uint8_t)event;
   return 1;
}

AudioEvent audio_queue_take(AudioQueue *queue) {
   uint8_t i, winner = 0, winner_priority = 0;
   AudioEvent result;
   if (!queue) return AUDIO_EVENT_NONE;
   for (i = 0; i < queue->count; ++i) {
      uint8_t priority = audio_event_priority((AudioEvent)queue->events[i]);
      /* Strict greater-than keeps the first request stable on a tie. */
      if (priority > winner_priority) {
         winner = i;
         winner_priority = priority;
      }
   }
   result = winner_priority ? (AudioEvent)queue->events[winner] : AUDIO_EVENT_NONE;
   audio_queue_clear(queue);
   return result;
}
