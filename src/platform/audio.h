#ifndef BH2_AUDIO_H
#define BH2_AUDIO_H

#include "audio_logic.h"

void audio_init(void);
void audio_request(AudioEvent event);
void audio_tick(void);
void audio_cancel(void);
void audio_music_toggle(void);
void audio_music_pause(void);
void audio_music_resume(void);
uint16_t audio_overflows(void);

#endif
