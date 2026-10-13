#ifndef BH2_TELEMETRY_H
#define BH2_TELEMETRY_H
#include <stdint.h>

typedef struct {
   uint16_t ticks;
   uint16_t presentations;
   uint16_t overruns;
   uint8_t max_pending;
} Telemetry;

/* Phase labels for the opt-in CPC timing build. Calls compile to no code in
 * the release game; the timing emulator observes the debug marker externally.
 */
typedef enum {
   TELEMETRY_PHASE_RESTORE = 1,
   TELEMETRY_PHASE_PERSISTENT = 2,
   TELEMETRY_PHASE_SPRITES = 3,
   TELEMETRY_PHASE_HUD = 4,
   TELEMETRY_PHASE_SIM = 5,
   TELEMETRY_PHASE_AUDIO = 6,
   TELEMETRY_PHASE_BANKS = 7,
   TELEMETRY_PHASE_FRAME = 8
} TelemetryPhase;

#define TELEMETRY_PHASE_END_FLAG 0x80u

#if defined(BH2_TELEMETRY_PHASE_MARKERS)
void telemetry_phase_mark(uint8_t phase);
#define TELEMETRY_PHASE_BEGIN(phase) telemetry_phase_mark((uint8_t)(phase))
#define TELEMETRY_PHASE_END(phase) telemetry_phase_mark((uint8_t)(phase) | TELEMETRY_PHASE_END_FLAG)
#else
#define TELEMETRY_PHASE_BEGIN(phase) ((void)0)
#define TELEMETRY_PHASE_END(phase) ((void)0)
#endif

void telemetry_reset(void);
void telemetry_present(uint8_t pending);
void telemetry_overrun(uint8_t pending);
void telemetry_read(Telemetry* out);

#endif
