.module bank_irq_probe
.globl _bank_test_iff_enabled

;; Test-only IFF2 observer. LD A,I reports the state without modifying it.
_bank_test_iff_enabled::
    ld a, i
    jp po, 001$
    ld l, #1
    ret
001$:
    ld l, #0
    ret
