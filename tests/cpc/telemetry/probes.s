.module o02_probes
.globl _o02_probe_short, _o02_probe_short_begin, _o02_probe_short_end
.globl _o02_probe_long, _o02_probe_long_begin, _o02_probe_long_end
.globl _o02_phase_probe, _o02_phase_probe_begin, _o02_phase_probe_end
.globl _o02_wait_edges, _o02_vsync8_begin, _o02_vsync8_end
.globl _o02_wait_edge, _o02_case_done

.area _CODE

_o02_probe_short:
_o02_probe_short_begin:
   nop
_o02_probe_short_end:
   ret

_o02_probe_long:
_o02_probe_long_begin:
   nop
   nop
_o02_probe_long_end:
   ret

_o02_phase_probe:
_o02_phase_probe_begin:
   ld a, #1
   ld (0x3fff), a
   ld a, #0x81
   ld (0x3fff), a
_o02_phase_probe_end:
   ret

_o02_wait_edge:
   ld bc, #0xf500
00003$:
   in a, (c)
   and #1
   jr nz, 00003$
00004$:
   in a, (c)
   and #1
   jr z, 00004$
   ret

_o02_wait_edges:
_o02_vsync8_begin:
   ld b, #8
00005$:
   push bc
   call _o02_wait_edge
   pop bc
   djnz 00005$
_o02_vsync8_end:
   ret

_o02_case_done:
   jr _o02_case_done
