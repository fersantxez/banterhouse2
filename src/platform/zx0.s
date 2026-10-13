;; ZX0 decoder copyright (c) 2021 Einar Saukas.
;; BSD-3-Clause: see LICENSES/ZX0-BSD-3-Clause.txt.
.module zx0
.globl _zx0_from_c

;; SDCC --sdcccall 0 wrapper: arguments are source then destination.
_zx0_from_c::
    pop af
    pop hl
    pop de
    push de
    push hl
    push af
    call dzx0_standard
    ret

;; ZX0 standard forward decoder by Einar Saukas and Urusergi (68 bytes).
dzx0_standard:
        ld      bc, #0xffff
        push    bc
        inc     bc
        ld      a, #0x80
dzx0s_literals:
        call    dzx0s_elias
        ldir
        add     a, a
        jr      c, dzx0s_new_offset
        call    dzx0s_elias
dzx0s_copy:
        ex      (sp), hl
        push    hl
        add     hl, de
        ldir
        pop     hl
        ex      (sp), hl
        add     a, a
        jr      nc, dzx0s_literals
dzx0s_new_offset:
        pop     bc
        ld      c, #0xfe
        call    dzx0s_elias_loop
        inc     c
        ret     z
        ld      b, c
        ld      c, (hl)
        inc     hl
        rr      b
        rr      c
        push    bc
        ld      bc, #1
        call    nc, dzx0s_elias_backtrack
        inc     bc
        jr      dzx0s_copy
dzx0s_elias:
        inc     c
dzx0s_elias_loop:
        add     a, a
        jr      nz, dzx0s_elias_skip
        ld      a, (hl)
        inc     hl
        rla
dzx0s_elias_skip:
        ret     c
dzx0s_elias_backtrack:
        add     a, a
        rl      c
        rl      b
        jr      dzx0s_elias_loop
