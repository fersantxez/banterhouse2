.module banks
.globl _bank_apply_config
.globl _bank_current_config

;; BankConfig is passed in L (__z88dk_fastcall). The mode bits, GA port and
;; mapping values match the pinned CPCTelera cpct_pageMemory implementation.
;; Save IFF2 with LD A,I and restore that exact state; never unconditional EI.
;; The caller, stack and shadow are required to reside in fixed RAM.
_bank_apply_config::
    ld a, i
    di
    push af
    ld a, l
    ld (_bank_current_config), a
    or #0xc0
    ld bc, #0x7f00
    out (c), a
    pop af
    jp po, 001$
    ei
001$:
    ret
