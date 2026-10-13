#!/usr/bin/env python3
"""Apply the local, runtime-opt-in O02 cycle trace patch to pinned Caprice32."""
from pathlib import Path


TRACE_HEADER = r'''#ifndef BH2_CYCLE_TRACE_H
#define BH2_CYCLE_TRACE_H
#include "types.h"
void bh2_cycle_trace_cycles(int cycles);
void bh2_cycle_trace_pc(word pc, bool guest_ready, byte guest_done);
void bh2_cycle_trace_memory(word address, byte value, int current_instruction_cycles);
#endif
'''

TRACE_SOURCE = r'''#include "bh2_cycle_trace.h"
#include <SDL.h>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <map>
#include <sstream>
#include <string>

int snapshot_save(const std::string& filename);

static std::map<word, std::string> markers;
static std::ofstream trace;
static std::string snapshot_path;
static unsigned long long total_cycles = 0;
static bool initialized = false;
static bool enabled = false;

static void initialize_trace() {
  initialized = true;
  const char* marker_path = std::getenv("BH2_TRACE_MARKERS");
  const char* trace_path = std::getenv("BH2_CYCLE_TRACE");
  const char* sna_path = std::getenv("BH2_SNAPSHOT_OUT");
  if (!marker_path || !trace_path || !sna_path) return;
  std::ifstream input(marker_path);
  if (!input) return;
  std::string line;
  while (std::getline(input, line)) {
    std::istringstream fields(line);
    unsigned address;
    std::string label;
    if (!(fields >> std::hex >> address >> label) || address > 0xffff || label.empty()) {
      markers.clear();
      return;
    }
    if (!markers.emplace(static_cast<word>(address), label).second) {
      markers.clear();
      return;
    }
  }
  if (markers.empty()) return;
  trace.open(trace_path, std::ios::out | std::ios::trunc);
  if (!trace) return;
  snapshot_path = sna_path;
  enabled = true;
  trace << "cycles,pc,label\n";
  trace.flush();
}

void bh2_cycle_trace_cycles(int cycles) {
  if (enabled && cycles > 0) total_cycles += static_cast<unsigned>(cycles);
}

void bh2_cycle_trace_pc(word pc, bool guest_ready, byte guest_done) {
  if (!initialized) initialize_trace();
  if (!enabled || !guest_ready) return;
  const auto found = markers.find(pc);
  if (found == markers.end()) return;
  if (found->second == "done" && guest_done != 0xa5) return;
  trace << total_cycles << ',' << std::hex << std::setw(4) << std::setfill('0')
        << pc << ',' << found->second << std::dec << '\n';
  trace.flush();
  if (found->second == "done") {
    const int result = snapshot_save(snapshot_path);
    trace << "snapshot," << result << ',' << snapshot_path << '\n';
    trace.flush();
    trace.close();
    enabled = false;
    SDL_Event event{};
    event.type = SDL_QUIT;
    SDL_PushEvent(&event);
  }
}

void bh2_cycle_trace_memory(word address, byte value, int current_instruction_cycles) {
  if (!enabled || address != 0x3fff) return;
  trace << (total_cycles + (current_instruction_cycles > 0 ? static_cast<unsigned>(current_instruction_cycles) : 0u))
        << ",3fff,phase_" << std::hex << std::setw(2) << std::setfill('0')
        << static_cast<unsigned>(value) << std::dec << '\n';
  trace.flush();
}
'''


def patch(source: Path) -> list[str]:
    z80 = source / "src/z80.cpp"
    text = z80.read_text()
    argparse = source / "src/argparse.cpp"
    argparse_text = argparse.read_text()
    snapshot_alias = '    { "CAP32_SNAPSHOT", cap32_keystroke(CAP32_SNAPSHOT) },'
    if snapshot_alias not in argparse_text:
        delay_alias = '    { "CAP32_DELAY", cap32_keystroke(CAP32_DELAY) },'
        if argparse_text.count(delay_alias) != 1:
            raise ValueError("Caprice autocmd key table no longer has its pinned CAP32_DELAY anchor")
        argparse_text = argparse_text.replace(delay_alias, snapshot_alias + "\n" + delay_alias, 1)
        argparse.write_text(argparse_text)
    header_include = '#include "bh2_cycle_trace.h"'
    old_pc_hook = '      bh2_cycle_trace_pc(_PC);'
    new_pc_hook = ('      bh2_cycle_trace_pc(_PC, read_mem(0x3c00) == 0xb2 && read_mem(0x3c01) == 0x4f && '
                    'read_mem(0x3c02) == 0x30 && read_mem(0x3c03) == 0x32 && '
                    'read_mem(0x3c04) == 0x26 && read_mem(0x3c05) == 0x20 && '
                    'read_mem(0x3c06) == 0x02 && read_mem(0x3c07) == 0xb2, read_mem(0x3c0e));')
    if header_include in text:
        if text.count(old_pc_hook) == 1:
            text = text.replace(old_pc_hook, new_pc_hook, 1)
            z80.write_text(text)
        elif text.count(new_pc_hook) != 1:
            raise ValueError("Instrumented Caprice source has an unrecognized O02 PC hook")
        (source / "src/bh2_cycle_trace.h").write_text(TRACE_HEADER)
        (source / "src/bh2_cycle_trace.cpp").write_text(TRACE_SOURCE)
        return ["src/argparse.cpp", "src/z80.cpp", "src/bh2_cycle_trace.h", "src/bh2_cycle_trace.cpp"]
    anchors = {
        '#include "z80_macros.h"': '#include "z80_macros.h"\n#include "bh2_cycle_trace.h"',
        'while (_PCdword != z80.break_point) { // loop until break point':
            'while (_PCdword != z80.break_point) { // loop until break point\n' + new_pc_hook,
        '      CPC.cycle_count -= iCycleCount; \\':
            '      CPC.cycle_count -= iCycleCount; \\\n      bh2_cycle_trace_cycles(iCycleCount); \\',
    }
    for old, new in anchors.items():
        if text.count(old) != 1:
            raise ValueError(f"Expected exactly one Caprice patch anchor, found {text.count(old)}: {old!r}")
        text = text.replace(old, new, 1)
    write_start = text.index("inline void write_mem(word addr, byte val) {")
    write_end = text.index("\n}", write_start)
    write_body = text[write_start:write_end]
    write_call = "  write_mem_no_watchpoint(addr, val);"
    if write_body.count(write_call) != 1:
        raise ValueError("Caprice CPU memory-write function no longer matches the pinned patch")
    write_body = write_body.replace(
        write_call,
        write_call + "\n  if (addr == 0x3fff) bh2_cycle_trace_memory(addr, val, iCycleCount);",
        1,
    )
    text = text[:write_start] + write_body + text[write_end:]
    z80.write_text(text)
    (source / "src/bh2_cycle_trace.h").write_text(TRACE_HEADER)
    (source / "src/bh2_cycle_trace.cpp").write_text(TRACE_SOURCE)
    return ["src/argparse.cpp", "src/z80.cpp", "src/bh2_cycle_trace.h", "src/bh2_cycle_trace.cpp"]
