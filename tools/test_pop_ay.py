#!/usr/bin/env python3
"""Host assertions for the deterministic original AY pop arrangement."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_pop_ay", ROOT / "tools/build_pop_ay.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def main() -> int:
    melody, melody_volume, bass_arp, bass_arp_volume = module.build_tables()
    assert all(len(table) == 256 for table in (melody, melody_volume, bass_arp, bass_arp_volume))
    assert melody[0] > 0 and melody_volume[0] >= 11
    assert len({p for p in melody if p}) >= 12, "melody needs distinct pitches"
    assert len({p for p in bass_arp if p}) >= 16, "bass/arp needs distinct pitches"
    assert min(p for p in melody if p) > 40 and max(melody) < 250, "melody range should stay audible"
    assert max(bass_arp) > 900 and min(p for p in bass_arp if p) < 500, "bass and arpeggio must differ by register"
    assert all(0 <= value <= 15 for table in (melody_volume, bass_arp_volume) for value in table)
    assert sum(v > 0 for v in melody_volume) >= 100
    assert sum(v > 0 for v in bass_arp_volume) >= 100
    assert melody[:64] != melody[64:128]
    assert melody[128:192] != melody[192:256]
    source = module.generate()
    assert "pop_melody_periods:" in source and "pop_bass_arp_periods:" in source
    assert source.count("adc a, #0") == 2, "16-bit indexing must cover all 256 period entries"
    assert "inc a                 ;; byte wrap loops all 256 sixteenths" in source
    assert "AY channel C" in source and "priority SFX" in source
    mute = (ROOT / "src/platform/audio_ay.s").read_text().split("_sfx_mute::", 1)[1].split("_sfx_step::", 1)[0]
    assert "ld d, #8" in mute and "ld d, #9" not in mute, "SFX cleanup must not mute AY melody B"
    assert "music_paused" in source and "_music_pause::" in source and "_music_resume::" in source
    assert source.index("ld a, (music_paused)") < source.index("ld a, (music_wait)"), "pause must freeze the sequencer"
    audio_c = (ROOT / "src/platform/audio.c").read_text()
    main_c = (ROOT / "src/main.c").read_text()
    assert "void audio_music_pause(void)" in audio_c and "void audio_music_resume(void)" in audio_c
    assert "audio_music_pause();" in main_c and "audio_music_resume();" in main_c
    print("PASS pop AY: 16-bar melody/bass, deterministic tables, independent SFX mute and frozen/resumed music pause")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
