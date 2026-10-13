#!/usr/bin/env python3
"""Generate the original 16-bar Banterhouse AY hook for CPC channels B/C."""
from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "src/platform/music.s"
AY_CLOCK_HZ = 1_000_000
STEPS_PER_BAR = 16
BARS = 16
STEPS = STEPS_PER_BAR * BARS
TICKS_PER_STEP = 6  # 125 BPM at the CPC 50 Hz simulation clock

# Eight eighth-note slots per bar, MIDI pitches, C major / A minor with
# syncopated answers. This is an original melody, not a transcription.
MELODY_BARS: tuple[tuple[int | None, ...], ...] = (
    (76, 79, 81, 79, 76, 74, 72, None),      # C
    (69, 72, 76, 72, 71, 72, 74, 76),        # Am
    (69, 72, 77, 76, 72, 69, 67, 69),        # F
    (71, 74, 79, None, 77, 74, 71, 67),      # G
    (76, 79, 84, 79, 81, 79, 76, 74),        # C, higher answer
    (69, 72, 76, 79, 76, 72, 74, 76),        # Am
    (69, 72, 77, 81, 79, 77, 72, 69),        # F
    (71, 74, 79, 83, 81, 79, 74, 71),        # G turnaround
    (74, 77, 81, 77, 74, 72, 69, 74),        # Dm
    (71, 74, 79, 74, 77, 74, 71, 67),        # G
    (76, 79, 83, 79, 76, 74, 71, 76),        # Em
    (69, 72, 76, 81, 79, 76, 72, 69),        # Am
    (69, 72, 77, 81, 84, 81, 77, 76),        # F
    (71, 74, 79, 83, 86, 83, 79, 77),        # G
    (76, 79, 84, 83, 81, 79, 76, 74),        # C
    (72, 76, 79, 84, 81, 79, 76, 72),        # C resolution
)

CHORDS: tuple[tuple[int, int, int, int], ...] = (
    (36, 48, 43, 52),  # C, root / octave / fifth / third
    (33, 45, 40, 48),  # Am
    (41, 53, 48, 57),  # F
    (43, 55, 50, 59),  # G
    (36, 48, 43, 52),
    (33, 45, 40, 48),
    (41, 53, 48, 57),
    (43, 55, 50, 59),
    (38, 50, 45, 53),  # Dm
    (43, 55, 50, 59),
    (40, 52, 47, 55),  # Em
    (45, 57, 52, 60),  # Am
    (41, 53, 48, 57),
    (43, 55, 50, 59),
    (36, 48, 43, 52),
    (36, 48, 43, 52),
)


def ay_period(midi_pitch: int) -> int:
    frequency = 440.0 * (2.0 ** ((midi_pitch - 69) / 12.0))
    return max(1, min(0x0FFF, round(AY_CLOCK_HZ / (16 * frequency))))


def build_tables() -> tuple[list[int], list[int], list[int], list[int]]:
    melody: list[int] = []
    melody_volume: list[int] = []
    bass_arp: list[int] = []
    bass_arp_volume: list[int] = []
    for bar, notes in enumerate(MELODY_BARS):
        for eighth, pitch in enumerate(notes):
            melody.extend((ay_period(pitch), 0) if pitch is not None else (0, 0))
            # Strong beat accents plus a clipped offbeat answer.
            if pitch is None:
                melody_volume.extend((0, 0))
            else:
                accent = 13 if eighth in (0, 4) else 11
                melody_volume.extend((accent, 0))

        root, octave, fifth, third = CHORDS[bar]
        chord_pitches = (root, None, fifth, None, root, None, third, None,
                         root, None, fifth, None, root, None, octave, None)
        for step, pitch in enumerate(chord_pitches):
            bass_arp.append(ay_period(pitch) if pitch is not None else 0)
            bass_arp_volume.append((13 if step in (0, 8) else 11) if pitch is not None and step % 4 == 0
                                   else (8 if pitch is not None else 0))
    return melody, melody_volume, bass_arp, bass_arp_volume


def emit_table(label: str, values: list[int], word: bool) -> list[str]:
    lines = [f"{label}:"]
    for start in range(0, len(values), 8):
        row = values[start : start + 8]
        directive = ".dw" if word else ".db"
        if word:
            body = ",".join(f"0x{x:04x}" for x in row)
        else:
            body = ",".join(str(x) for x in row)
        lines.append(f"    {directive} {body}")
    return lines


def generate() -> str:
    melody, melody_volume, bass_arp, bass_arp_volume = build_tables()
    if any(len(table) != STEPS for table in (melody, melody_volume, bass_arp, bass_arp_volume)):
        raise AssertionError("bad generated table length")
    lines = [
        ".module music",
        ".globl _music_init, _music_tick, _music_toggle, _music_pause, _music_resume",
        "",
        ".area _DATA",
        "music_enabled: .db 1",
        "music_paused:  .db 0",
        "music_step:    .db 0",
        "music_wait:    .db 0",
        "",
        ".area _CODE",
        ";; Original 16-bar pop/funk hook for Banterhouse 2.",
        ";; AY B carries the melody; AY C alternates bass roots and chord arpeggios.",
        ";; AY A remains available for priority SFX; six 50 Hz ticks per sixteenth.",
    ]
    lines += emit_table("pop_melody_periods", melody, True)
    lines += emit_table("pop_melody_volumes", melody_volume, False)
    lines += emit_table("pop_bass_arp_periods", bass_arp, True)
    lines += emit_table("pop_bass_arp_volumes", bass_arp_volume, False)
    lines += [
        "",
        "_music_init::",
        "    ld a, #1",
        "    ld (music_enabled), a",
        "    xor a",
        "    ld (music_paused), a",
        "    ld (music_step), a",
        "    ld (music_wait), a",
        "    ld d, #7",
        "    ld e, #0x38       ;; tones B/C enabled; noise disabled",
        "    call _ay_write",
        "    ld d, #9",
        "    ld e, #0",
        "    call _ay_write",
        "    ld d, #10",
        "    ld e, #0",
        "    jp _ay_write",
        "",
        "_music_tick::",
        "    push af",
        "    push bc",
        "    push de",
        "    push hl",
        "    ld a, (music_enabled)",
        "    or a",
        "    jr z, music_done",
        "    ld a, (music_paused)",
        "    or a",
        "    jr nz, music_done",
        "    ld a, (music_wait)",
        "    inc a",
        "    cp #6",
        "    jr c, music_store_wait",
        "    xor a",
        "music_store_wait:",
        "    ld (music_wait), a",
        "    or a",
        "    jr nz, music_done",
        "",
        "    ;; Melody: AY channel B.",
        "    ld a, (music_step)",
        "    add a, a",
        "    ld l, a",
        "    ld a, #0",
        "    adc a, #0",
        "    ld h, a",
        "    ld bc, #pop_melody_periods",
        "    add hl, bc",
        "    ld e, (hl)",
        "    inc hl",
        "    ld d, (hl)",
        "    push de",
        "    ld d, #2",
        "    pop hl",
        "    ld e, l",
        "    call _ay_write",
        "    ld d, #3",
        "    ld e, h",
        "    call _ay_write",
        "    ld a, (music_step)",
        "    ld l, a",
        "    ld h, #0",
        "    ld bc, #pop_melody_volumes",
        "    add hl, bc",
        "    ld d, #9",
        "    ld e, (hl)",
        "    call _ay_write",
        "",
        "    ;; Bass roots and clipped chord arpeggios: AY channel C.",
        "    ld a, (music_step)",
        "    add a, a",
        "    ld l, a",
        "    ld a, #0",
        "    adc a, #0",
        "    ld h, a",
        "    ld bc, #pop_bass_arp_periods",
        "    add hl, bc",
        "    ld e, (hl)",
        "    inc hl",
        "    ld d, (hl)",
        "    push de",
        "    ld d, #4",
        "    pop hl",
        "    ld e, l",
        "    call _ay_write",
        "    ld d, #5",
        "    ld e, h",
        "    call _ay_write",
        "    ld a, (music_step)",
        "    ld l, a",
        "    ld h, #0",
        "    ld bc, #pop_bass_arp_volumes",
        "    add hl, bc",
        "    ld d, #10",
        "    ld e, (hl)",
        "    call _ay_write",
        "",
        "    ld a, (music_step)",
        "    inc a                 ;; byte wrap loops all 256 sixteenths",
        "    ld (music_step), a",
        "music_done:",
        "    pop hl",
        "    pop de",
        "    pop bc",
        "    pop af",
        "    ret",
        "",
        "_music_toggle::",
        "    ld a, (music_enabled)",
        "    xor #1",
        "    ld (music_enabled), a",
        "    or a",
        "    jr z, music_toggle_off",
        "    ld d, #7",
        "    ld e, #0x38",
        "    call _ay_write",
        "    ret",
        "music_toggle_off:",
        "    ;; Preserve SFX channel A and silence only music-owned channels.",
        "    ld d, #9",
        "    ld e, #0",
        "    call _ay_write",
        "    ld d, #10",
        "    ld e, #0",
        "    call _ay_write",
        "    ld d, #7",
        "    ld e, #0x38",
        "    call _ay_write",
        "    ret",
        "",
        ";; Pause silences only the music-owned channels and freezes the sequencer.",
        "_music_pause::",
        "    ld a, #1",
        "    ld (music_paused), a",
        "    ld d, #9",
        "    ld e, #0",
        "    call _ay_write",
        "    ld d, #10",
        "    ld e, #0",
        "    jp _ay_write",
        "",
        ";; Restore the currently sounding step without advancing the song position.",
        "_music_resume::",
        "    xor a",
        "    ld (music_paused), a",
        "    ld a, (music_enabled)",
        "    or a",
        "    ret z",
        "    ld a, (music_step)",
        "    or a",
        "    ret z",
        "    dec a",
        "    ld l, a",
        "    ld h, #0",
        "    ld bc, #pop_melody_volumes",
        "    add hl, bc",
        "    ld d, #9",
        "    ld e, (hl)",
        "    call _ay_write",
        "    ld a, (music_step)",
        "    dec a",
        "    ld l, a",
        "    ld h, #0",
        "    ld bc, #pop_bass_arp_volumes",
        "    add hl, bc",
        "    ld d, #10",
        "    ld e, (hl)",
        "    jp _ay_write",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true", help="check generated output without writing")
    args = parser.parse_args()
    content = generate()
    if args.check:
        if not args.output.exists() or args.output.read_text() != content:
            raise SystemExit(f"FAIL: {args.output} no coincide con la partitura determinista")
        print(f"PASS: {args.output} coincide; {STEPS} pasos, {BARS} compases, {TICKS_PER_STEP} ticks/paso")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content)
        print(f"PASS: generado {args.output}; {STEPS} pasos, {BARS} compases, {TICKS_PER_STEP} ticks/paso")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
