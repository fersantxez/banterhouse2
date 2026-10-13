#!/usr/bin/env python3
"""Read Caprice32 CPC6128 snapshots and O02 cycle traces without guessing."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SNA_HEADER_BYTES = 256
PAGE_BYTES = 0x4000
SNA_MAGIC = b"MV - SNA"
RAM_CONFIG_MAPS = (
    (0, 1, 2, 3),
    (0, 1, 2, 7),
    (4, 5, 6, 7),
    (0, 3, 2, 7),
    (0, 4, 2, 3),
    (0, 5, 2, 3),
    (0, 6, 2, 3),
    (0, 7, 2, 3),
)
PHASE_NAMES = {
    1: "restore", 2: "persistent", 3: "sprites", 4: "hud",
    5: "sim", 6: "audio", 7: "banks", 8: "frame",
}


class BackendError(ValueError):
    """Evidence is malformed, incomplete, or belongs to a different build."""


@dataclass(frozen=True)
class CPCSnapshot:
    path: Path
    raw: bytes
    header: bytes
    physical_ram: bytes
    ram_kib: int
    model_id: int
    pc: int
    sp: int
    gate_array_ram_config: int
    crtc_registers: bytes
    logical_to_physical_page: tuple[int, int, int, int]

    def read_logical(self, address: int, size: int) -> bytes:
        if address < 0 or size < 0 or address + size > 0x10000:
            raise BackendError(f"logical range outside CPC memory: {address:04X}+{size}")
        out = bytearray()
        for logical in range(address, address + size):
            logical_page, offset = divmod(logical, PAGE_BYTES)
            physical_page = self.logical_to_physical_page[logical_page]
            start = physical_page * PAGE_BYTES + offset
            out.append(self.physical_ram[start])
        return bytes(out)

    def visible_vram(self) -> tuple[int, int, bytes]:
        r12 = self.crtc_registers[12]
        logical_start = (r12 & 0x30) << 10
        logical_page = (logical_start >> 14) & 3
        physical_page = self.logical_to_physical_page[logical_page]
        start = physical_page * PAGE_BYTES
        return logical_start, physical_page, self.physical_ram[start:start + PAGE_BYTES]


def parse_snapshot(path: Path | str) -> CPCSnapshot:
    path = Path(path)
    raw = path.read_bytes()
    if len(raw) < SNA_HEADER_BYTES or raw[:8] != SNA_MAGIC:
        raise BackendError(f"not a Caprice32/Arnold SNA snapshot: {path}")
    header = raw[:SNA_HEADER_BYTES]
    if header[16] != 3:
        raise BackendError(f"unsupported SNA version {header[16]} (expected 3)")
    ram_kib = int.from_bytes(header[107:109], "little")
    if ram_kib < 64 or ram_kib % 16:
        raise BackendError(f"invalid SNA RAM size {ram_kib} KiB")
    physical_ram = raw[SNA_HEADER_BYTES:]
    if len(physical_ram) != ram_kib * 1024:
        raise BackendError(
            f"incomplete SNA RAM dump: expected {ram_kib * 1024} bytes, got {len(physical_ram)}"
        )
    if ram_kib != 128:
        raise BackendError(f"O02 profile requires CPC6128 128 KiB, got {ram_kib} KiB")

    ga_ram = header[65]
    ram_bank = (ga_ram >> 3) & 7
    if ((ram_bank + 2) * 64) > ram_kib:
        ram_bank = 0
    extension_page_base = (ram_bank + 1) * 4
    logical_map = tuple(
        extension_page_base + (page - 4) if page >= 4 else page
        for page in RAM_CONFIG_MAPS[ga_ram & 7]
    )
    if any(page * PAGE_BYTES + PAGE_BYTES > len(physical_ram) for page in logical_map):
        raise BackendError(f"Gate Array RAM map references absent page(s): {logical_map}")
    crtc = header[67:85]
    return CPCSnapshot(
        path=path,
        raw=raw,
        header=header,
        physical_ram=physical_ram,
        ram_kib=ram_kib,
        model_id=header[109],
        pc=int.from_bytes(header[35:37], "little"),
        sp=int.from_bytes(header[33:35], "little"),
        gate_array_ram_config=ga_ram,
        crtc_registers=crtc,
        logical_to_physical_page=logical_map,
    )


def parse_map_symbols(path: Path | str) -> dict[str, int]:
    symbols: dict[str, int] = {}
    pattern = re.compile(r"^\s*([0-9A-Fa-f]{8})\s+(\S+)\s", re.M)
    for address, name in pattern.findall(Path(path).read_text(errors="replace")):
        symbols[name] = int(address, 16) & 0xFFFF
    return symbols


def require_symbol(symbols: dict[str, int], name: str) -> int:
    if name not in symbols:
        raise BackendError(f"required CPC map symbol missing: {name}")
    return symbols[name]


def screen_pattern_v1() -> bytes:
    return bytes(((i * 37 + (i >> 4) * 11 + 0x5A) & 0xFF) for i in range(PAGE_BYTES))


def validate_snapshot(snapshot_path: Path | str, case: dict[str, Any],
                      binary_path: Path | str, map_path: Path | str) -> dict[str, Any]:
    snap = parse_snapshot(snapshot_path)
    symbols = parse_map_symbols(map_path)
    evidence_address = require_symbol(symbols, case["evidence_symbol"])
    if evidence_address != case["evidence_address"]:
        raise BackendError(
            f"evidence symbol moved: expected {case['evidence_address']:04X}, got {evidence_address:04X}"
        )
    expected_state = bytes.fromhex(case["expected_evidence_hex"])
    if len(expected_state) != case["evidence_size"]:
        raise BackendError("manifest evidence size does not match expected byte string")
    actual_state = snap.read_logical(evidence_address, len(expected_state))
    if actual_state != expected_state:
        mismatch = next(i for i, (actual, expected) in enumerate(zip(actual_state, expected_state))
                        if actual != expected)
        raise BackendError(
            f"wrong build/state at {evidence_address + mismatch:04X}: "
            f"{actual_state[mismatch]:02X}!={expected_state[mismatch]:02X}"
        )

    done_pc = require_symbol(symbols, "_o02_case_done")
    if snap.pc != done_pc:
        raise BackendError(f"snapshot PC {snap.pc:04X} is not the terminal marker {done_pc:04X}")
    if snap.model_id != 2 or snap.ram_kib != 128:
        raise BackendError(f"wrong CPC profile: model={snap.model_id}, RAM={snap.ram_kib} KiB")
    if not 0x3F00 <= snap.sp <= 0x3FF0:
        raise BackendError(f"stack outside reserved range: SP={snap.sp:04X}")

    guard_spec = case["stack_guard"]
    guard = snap.read_logical(guard_spec["address"], guard_spec["size"])
    bad = next((i for i, value in enumerate(guard) if value != guard_spec["fill"]), None)
    if bad is not None:
        raise BackendError(f"stack canary changed at {guard_spec['address'] + bad:04X}")

    for start_symbol, data_offset, length in (("_main", 0, 64),):
        start = require_symbol(symbols, start_symbol)
        actual_code = snap.read_logical(start, length)
        expected_code = Path(binary_path).read_bytes()[data_offset:data_offset + length]
        if len(expected_code) != length or actual_code != expected_code:
            raise BackendError(f"running code does not match {Path(binary_path).name} at {start:04X}")

    logical_start, visible_page, vram = snap.visible_vram()
    expected_vram = screen_pattern_v1()
    if vram != expected_vram:
        mismatch = next(i for i, (actual, expected) in enumerate(zip(vram, expected_vram))
                        if actual != expected)
        raise BackendError(
            f"visible VRAM RAM{visible_page} differs at {mismatch:04X}: "
            f"{vram[mismatch]:02X}!={expected_vram[mismatch]:02X}"
        )
    return {
        "snapshot": str(Path(snapshot_path)),
        "snapshot_sha256": hashlib.sha256(snap.raw).hexdigest(),
        "ram_sha256": hashlib.sha256(snap.physical_ram).hexdigest(),
        "evidence_address": f"0x{evidence_address:04X}",
        "evidence_hex": actual_state.hex(),
        "pc": f"0x{snap.pc:04X}",
        "sp": f"0x{snap.sp:04X}",
        "model_id": snap.model_id,
        "ram_kib": snap.ram_kib,
        "gate_array_ram_config": f"0x{snap.gate_array_ram_config:02X}",
        "logical_to_physical_page": list(snap.logical_to_physical_page),
        "crtc_r12": f"0x{snap.crtc_registers[12]:02X}",
        "visible_logical_start": f"0x{logical_start:04X}",
        "visible_ram_page": visible_page,
        "visible_vram_bytes": len(vram),
        "visible_vram_sha256": hashlib.sha256(vram).hexdigest(),
        "stack_guard_bytes": len(guard),
        "stack_guard": "PASS",
        "running_binary_signature": "PASS",
    }


def parse_cycle_trace(path: Path | str, marker_specs: list[dict[str, Any]], profile: dict[str, Any]) -> dict[str, Any]:
    lines = Path(path).read_text().splitlines()
    if not lines or lines[0] != "cycles,pc,label":
        raise BackendError("cycle trace has a missing or invalid header")
    events: list[dict[str, Any]] = []
    snapshot_status: int | None = None
    for line_no, line in enumerate(lines[1:], 2):
        fields = line.split(",", 2)
        if fields[0] == "snapshot":
            if len(fields) < 2:
                raise BackendError(f"incomplete snapshot status at trace line {line_no}")
            try:
                snapshot_status = int(fields[1], 10)
            except ValueError as exc:
                raise BackendError(f"invalid snapshot status at trace line {line_no}") from exc
            continue
        if len(fields) != 3:
            raise BackendError(f"incomplete cycle trace row at line {line_no}")
        try:
            cycles = int(fields[0], 10)
            pc = int(fields[1], 16)
        except ValueError as exc:
            raise BackendError(f"invalid cycle count or PC at trace line {line_no}") from exc
        if events and cycles < events[-1]["cycles"]:
            raise BackendError(f"cycle counter went backwards at line {line_no}")
        events.append({"cycles": cycles, "pc": pc, "label": fields[2]})
    if snapshot_status != 0:
        raise BackendError(f"Caprice snapshot was not saved successfully (status={snapshot_status})")

    by_label: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        by_label.setdefault(event["label"], []).append(event)
    expected = {item["label"] for item in marker_specs}
    missing = sorted(label for label in expected if label not in by_label)
    if missing:
        raise BackendError(f"cycle trace missing marker(s): {', '.join(missing)}")

    deltas: dict[str, int] = {}
    for item in marker_specs:
        label = item["label"]
        if "expected_delta_cycles" not in item:
            continue
        end = by_label[label][0]
        start_label = label.replace("_end", "_begin")
        if start_label == label or start_label not in by_label:
            raise BackendError(f"no matching start marker for {label}")
        start = by_label[start_label][0]
        delta = end["cycles"] - start["cycles"]
        deltas[label.removesuffix("_end")] = delta
        if delta != item["expected_delta_cycles"]:
            raise BackendError(
                f"{label} measured {delta} cycles, expected {item['expected_delta_cycles']}"
            )

    vsync_spec = next((item for item in marker_specs if "vsync_intervals" in item), None)
    vsync = None
    if vsync_spec:
        start = by_label[vsync_spec["label"].replace("_end", "_begin")][0]
        end = by_label[vsync_spec["label"]][0]
        intervals = vsync_spec["vsync_intervals"]
        elapsed = end["cycles"] - start["cycles"]
        per_vsync = elapsed / intervals
        expected_cycles = profile["machine"]["nominal_cycles_per_frame"]
        tolerance_percent = profile["measurement"]["vsync_tolerance_percent"]
        error_percent = abs(per_vsync - expected_cycles) * 100 / expected_cycles
        if error_percent > tolerance_percent:
            raise BackendError(
                f"VSYNC calibration {per_vsync:.2f} cycles/edge differs from "
                f"{expected_cycles} by {error_percent:.3f}% (limit {tolerance_percent}%)"
            )
        vsync = {
            "intervals": intervals,
            "total_cycles": elapsed,
            "cycles_per_vsync": per_vsync,
            "nominal_cycles_per_frame": expected_cycles,
            "error_percent": error_percent,
        }
    phase_stack: list[dict[str, Any]] = []
    phase_intervals: list[dict[str, Any]] = []
    for event in events:
        match = re.fullmatch(r"phase_([0-9a-fA-F]{2})", event["label"])
        if not match:
            continue
        marker = int(match.group(1), 16)
        if marker == 0:  # zero clears the reserved marker byte; it is not a phase.
            continue
        phase_id = marker & 0x7f
        if phase_id not in PHASE_NAMES:
            raise BackendError(f"unknown phase marker 0x{marker:02X}")
        if marker & 0x80:
            if not phase_stack or phase_stack[-1]["phase_id"] != phase_id:
                raise BackendError(f"unbalanced phase end for {PHASE_NAMES[phase_id]}")
            opened = phase_stack.pop()
            duration = event["cycles"] - opened["start_cycles"]
            opened["end_cycles"] = event["cycles"]
            opened["inclusive_cycles"] = duration
            opened["exclusive_cycles"] = duration - opened.pop("child_cycles")
            phase_intervals.append(opened)
            if phase_stack:
                phase_stack[-1]["child_cycles"] += duration
        else:
            phase_stack.append({
                "phase_id": phase_id,
                "phase": PHASE_NAMES[phase_id],
                "start_cycles": event["cycles"],
                "child_cycles": 0,
            })
    if phase_stack:
        raise BackendError(f"unterminated phase {phase_stack[-1]['phase']}")
    return {
        "rows": len(events),
        "events": events,
        "cycle_resolution_cycles": 1,
        "known_sequence_deltas": deltas,
        "vsync_calibration": vsync,
        "phase_intervals": sorted(phase_intervals, key=lambda span: span["start_cycles"]),
        "snapshot_status": snapshot_status,
    }


def write_dumps(snapshot_path: Path | str, out: Path | str) -> dict[str, str]:
    snap = parse_snapshot(snapshot_path)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    physical = out / "ram-physical-128k.bin"
    physical.write_bytes(snap.physical_ram)
    visible = out / "vram-visible-16k.bin"
    visible.write_bytes(snap.visible_vram()[2])
    header = out / "sna-header-256.bin"
    header.write_bytes(snap.header)
    return {
        "physical_ram": str(physical),
        "visible_vram": str(visible),
        "sna_header": str(header),
    }
