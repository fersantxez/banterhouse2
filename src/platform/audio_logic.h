#ifndef BH2_AUDIO_LOGIC_H
#define BH2_AUDIO_LOGIC_H

#include <stdint.h>

#define AUDIO_QUEUE_CAPACITY 16u

typedef enum {
   AUDIO_EVENT_NONE = 0,
   AUDIO_EVENT_STEP,
   AUDIO_EVENT_JUMP,
   AUDIO_EVENT_SEAL,
   AUDIO_EVENT_LAND,
   AUDIO_EVENT_RETURN,
   AUDIO_EVENT_MACHINE,
   AUDIO_EVENT_DAMAGE,
   AUDIO_EVENT_ARENA_CLEAR
} AudioEvent;

typedef struct {
   uint8_t events[AUDIO_QUEUE_CAPACITY];
   uint8_t count;
   uint16_t overflow_count;
} AudioQueue;

void audio_queue_reset(AudioQueue *queue);
void audio_queue_clear(AudioQueue *queue);
uint8_t audio_queue_push(AudioQueue *queue, AudioEvent event);
AudioEvent audio_queue_take(AudioQueue *queue);
uint8_t audio_event_priority(AudioEvent event);

#endif
