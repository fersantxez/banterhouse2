.module smoke_boot
.globl _boot_abi_probe
.globl _boot_stack_fill
.globl _boot_stack_free
.globl _stack_probe_limit

;; T01/T02 ABI smoke: call0 stack order is return, first arg, second arg.
;; Return arg0 XOR arg1 in HL, restore return address and caller's stack.
_boot_abi_probe::
    pop af
    pop hl
    pop de
    push de
    push hl
    push af
    ld a, l
    xor e
    ld l, a
    ld a, h
    xor d
    ld h, a
    ret

;; Fill the unoccupied lower stack with an alternating canary. The current
;; call's return address and 32 bytes above it are deliberately left untouched.
_boot_stack_fill::
    ld hl, #0xffe0
    add hl, sp
    ld (_stack_probe_limit), hl
    ld de, (_stack_probe_limit)
    ld hl, #0x7cf0
    ld b, #0xa5
001$:
    ld (hl), b
    ld a, b
    xor #0xff
    ld b, a
    inc hl
    ld a, h
    cp d
    jr nz, 001$
    ld a, l
    cp e
    jr nz, 001$
    ret

;; Return the untouched contiguous bytes at the bottom of the reserved stack.
_boot_stack_free::
    ld de, #0x7cf0
    ld hl, (_stack_probe_limit)
    ld b, #0xa5
002$:
    ld a, (de)
    cp b
    jr nz, 003$
    ld a, b
    xor #0xff
    ld b, a
    inc de
    ld a, d
    cp h
    jr nz, 002$
    ld a, e
    cp l
    jr nz, 002$
003$:
    ld hl, #0x7cf0
    ex de, hl
    or a
    sbc hl, de
    ret
