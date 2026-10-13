.module audio
.globl _sfx_init, _sfx_step, _sfx_jump, _sfx_seal, _sfx_land
.globl _sfx_return, _sfx_hit, _sfx_machine, _sfx_mute, _ay_write

;; AY-3-8912 register write through the CPC 8255 PPI.
;; D = AY register, E = value. Keep SDCC's callee-saved registers intact.
_ay_write:
    push af
    push bc
    push de
    ld bc, #0xf782
    out (c), c
    ld bc, #0xf400
    ld a, d
    out (c), a
    ld bc, #0xf6c0
    out (c), c
    ld bc, #0xf600
    out (c), c
    ld bc, #0xf400
    ld a, e
    out (c), a
    ld bc, #0xf680
    out (c), c
    ld bc, #0xf600
    out (c), c
    pop de
    pop bc
    pop af
    ret

_sfx_init::
    ld d, #7
    ld e, #0x38
    call _ay_write
_sfx_mute::
    ld d, #8
    ld e, #0
    call _ay_write
    ret

_sfx_step::
    ld d, #0
    ld e, #0xe0
    call _ay_write
    ld d, #1
    ld e, #0
    call _ay_write
    ld d, #7
    ld e, #0x38
    call _ay_write
    ld d, #8
    ld e, #0x03
    jp _ay_write

_sfx_seal::
    ld d, #0
    ld e, #0x38
    call _ay_write
    ld d, #1
    ld e, #0
    call _ay_write
    ld d, #7
    ld e, #0x38
    call _ay_write
    ld d, #8
    ld e, #0x08
    jp _ay_write

_sfx_land::
    ld d, #0
    ld e, #0x98
    call _ay_write
    ld d, #1
    ld e, #0
    call _ay_write
    ld d, #7
    ld e, #0x38
    call _ay_write
    ld d, #8
    ld e, #0x05
    jp _ay_write

_sfx_jump::
    ld d, #0
    ld e, #0x70
    call _ay_write
    ld d, #1
    ld e, #0
    call _ay_write
    ld d, #7
    ld e, #0x38
    call _ay_write
    ld d, #8
    ld e, #0x0c
    jp _ay_write

_sfx_return::
    ld d, #0
    ld e, #0x28
    call _ay_write
    ld d, #1
    ld e, #0
    call _ay_write
    ld d, #7
    ld e, #0x38
    call _ay_write
    ld d, #8
    ld e, #0x0f
    jp _ay_write

_sfx_hit::
    ld d, #0
    ld e, #0xb0
    call _ay_write
    ld d, #1
    ld e, #0
    call _ay_write
    ld d, #7
    ld e, #0x38
    call _ay_write
    ld d, #8
    ld e, #0x0e
    jp _ay_write

_sfx_machine::
    ld d, #0
    ld e, #0x18
    call _ay_write
    ld d, #1
    ld e, #0
    call _ay_write
    ld d, #7
    ld e, #0x38
    call _ay_write
    ld d, #8
    ld e, #0x0f
    jp _ay_write
