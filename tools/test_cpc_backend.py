#!/usr/bin/env python3
"""Positive and negative tests for SNA extraction and O02 timing evidence."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cpc_backend
import run_cpc_case


def require_error(fn, pattern):
    try:
        fn()
    except cpc_backend.BackendError as exc:
        assert pattern in str(exc), str(exc)
    else:
        raise AssertionError(f"expected BackendError containing {pattern!r}")


def main():
    with tempfile.TemporaryDirectory(prefix="bh2-o02-backend-") as temp:
        root = Path(temp)
        case = json.loads((ROOT / "tests/cpc/telemetry/case.json").read_text())
        profile = json.loads((ROOT / "cfg/emulator-timing.json").read_text())
        header = bytearray(256)
        header[:8] = cpc_backend.SNA_MAGIC
        header[16] = 3
        header[33:35] = (0x3ff0).to_bytes(2, "little")
        header[35:37] = (0x0180).to_bytes(2, "little")
        header[65] = 0xC0
        header[79] = 0x30
        header[107:109] = (128).to_bytes(2, "little")
        header[109] = 2
        ram = bytearray(128 * 1024)
        binary = bytes(range(64))
        ram[0x100:0x100 + len(binary)] = binary
        state = bytes.fromhex(case["expected_evidence_hex"])
        ram[0x3c00:0x3c00 + len(state)] = state
        ram[0x3e00:0x3e80] = bytes([0xa5]) * 128
        vram = cpc_backend.screen_pattern_v1()
        ram[3 * cpc_backend.PAGE_BYTES:4 * cpc_backend.PAGE_BYTES] = vram
        snap_path = root / "valid.sna"
        snap_path.write_bytes(header + ram)
        bin_path = root / "O02.bin"
        bin_path.write_bytes(binary)
        map_path = root / "O02.map"
        map_path.write_text(
            "     00000100  _main                              main\n"
            "     00000180  _o02_case_done                    probes\n"
            "     00003C00  _o02_evidence                     main\n"
            "     00000190  _o02_probe_short_begin            probes\n"
            "     000001A0  _o02_probe_short_end              probes\n"
            "     000001B0  _o02_probe_long_begin             probes\n"
            "     000001C0  _o02_probe_long_end               probes\n"
            "     000001D0  _o02_vsync8_begin                 probes\n"
            "     000001E0  _o02_vsync8_end                   probes\n"
        )

        result = cpc_backend.validate_snapshot(snap_path, case, bin_path, map_path)
        assert result["snapshot_sha256"] and result["visible_vram_bytes"] == 16384
        assert result["visible_ram_page"] == 3 and result["stack_guard"] == "PASS"

        wrong_build = bytearray(snap_path.read_bytes())
        wrong_build[256 + 0x3c00 + 4] ^= 0x01
        wrong_build_path = root / "wrong-build.sna"
        wrong_build_path.write_bytes(wrong_build)
        require_error(lambda: cpc_backend.validate_snapshot(wrong_build_path, case, bin_path, map_path),
                      "wrong build/state")

        short_path = root / "short.sna"
        short_path.write_bytes(snap_path.read_bytes()[:-1])
        require_error(lambda: cpc_backend.parse_snapshot(short_path), "incomplete SNA RAM dump")

        missing_map = root / "missing.map"
        missing_map.write_text("     00000100  _main main\n     00000180  _o02_case_done probes\n")
        require_error(lambda: cpc_backend.validate_snapshot(snap_path, case, bin_path, missing_map),
                      "required CPC map symbol missing")

        trace = root / "cycles.csv"
        trace.write_text(
            "cycles,pc,label\n"
            "10,0000,phase_08\n"
            "20,0000,phase_05\n"
            "30,0000,phase_06\n"
            "40,0000,phase_86\n"
            "50,0000,phase_85\n"
            "60,0000,phase_88\n"
            "100,0190,probe_short_begin\n"
            "104,01a0,probe_short_end\n"
            "500,01b0,probe_long_begin\n"
            "508,01c0,probe_long_end\n"
            "600,01c8,phase_probe_begin\n"
            "620,3fff,phase_01\n"
            "640,3fff,phase_81\n"
            "648,01d0,phase_probe_end\n"
            "2000,01d0,vsync8_begin\n"
            "642000,01e0,vsync8_end\n"
            "700000,0180,done\n"
            "snapshot,0,valid.sna\n"
        )
        timed = cpc_backend.parse_cycle_trace(trace, case["markers"], profile)
        assert timed["cycle_resolution_cycles"] == 1
        assert timed["known_sequence_deltas"] == {
            "probe_short": 4, "probe_long": 8, "phase_probe": 48,
        }
        assert timed["vsync_calibration"]["cycles_per_vsync"] == 80000
        phases = {span["phase"]: span for span in timed["phase_intervals"]}
        assert phases["restore"]["inclusive_cycles"] == 20
        assert phases["frame"]["inclusive_cycles"] == 50
        assert phases["frame"]["exclusive_cycles"] == 20
        assert phases["sim"]["inclusive_cycles"] == 30
        assert phases["sim"]["exclusive_cycles"] == 20
        assert phases["audio"]["inclusive_cycles"] == 10

        unbalanced = root / "unbalanced-phases.csv"
        unbalanced.write_text(
            "cycles,pc,label\n10,0000,phase_05\n20,0000,phase_88\n"
            "100,0190,probe_short_begin\n104,01a0,probe_short_end\n"
            "500,01b0,probe_long_begin\n508,01c0,probe_long_end\n"
            "600,01c8,phase_probe_begin\n620,3fff,phase_01\n"
            "640,3fff,phase_81\n648,01d0,phase_probe_end\n"
            "2000,01d0,vsync8_begin\n642000,01e0,vsync8_end\n"
            "700000,0180,done\nsnapshot,0,valid.sna\n"
        )
        require_error(lambda: cpc_backend.parse_cycle_trace(unbalanced, case["markers"], profile),
                      "unbalanced phase end")

        bad_trace = root / "short-trace.csv"
        bad_trace.write_text("cycles,pc,label\n0,0000,done\nsnapshot,0,valid.sna\n")
        require_error(lambda: cpc_backend.parse_cycle_trace(bad_trace, case["markers"], profile),
                      "cycle trace missing marker")

        cfg = root / "config.cfg"
        disk = root / "probe.dsk"
        sleeper = root / "sleep-emulator"
        cfg.write_text("cfg\n")
        disk.write_bytes(b"disk")
        sleeper.write_text("#!/usr/bin/env python3\nimport time\ntime.sleep(2)\n")
        sleeper.chmod(0o755)
        markers = root / "markers.tsv"
        output = root / "timeout"
        output.mkdir()
        code, elapsed, reason = run_cpc_case.run_caprice(
            sleeper, cfg, disk, "run\"x\"", markers, root / "timeout.csv",
            root / "timeout.sna", 0.05, output,
        )
        assert code == 124 and "timeout" in reason and elapsed < 1.0

    print("PASS: SNA/RAM/VRAM, build-id, timing, nested phases, and backend failure negatives")


if __name__ == "__main__":
    main()
