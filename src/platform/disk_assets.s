; AMSDOS chapter background loader for a CPC 6128 disk build.
; CAS IN DIRECT reads a complete AMSDOS binary file into the supplied address.
; The four files are independent, checksummed disk entries, loaded only at
; boot or between arenas; BG_MEM is then reused for ZX0 output/background.
.module disk_assets
.area _CODE
.globl _disk_prepare, _disk_load_ch1, _disk_load_ch2, _disk_load_ch3, _disk_load_ch4
.globl _disk_cache_workspace_save, _disk_cache_workspace_restore
.globl _disk_load_error

; BASIC RUN uses MC BOOT PROGRAM, which shuts down extension ROMs/RSXs.
; Reinitialize CPC6128 AMSDOS with the classic RAM pool below the upper ROM.
; The 6128 AMSDOS ROM claims its workspace at the pool's high end (&A6FC..&ABFF);
; the chapter background page is disposable and is rebuilt immediately after.
_disk_prepare::
    ; KL INIT BACK resets the firmware stack pointer; preserve the caller's
    ; stack and SDCC frame pointer across its reinitialization.
    ld (_prepare_saved_sp), sp
    ld (_prepare_saved_ix), ix
    ld c, #7                   ; standard CPC 6128 AMSDOS ROM
    ld de, #0x0040             ; lowest usable byte in the standard CPC pool
    ld hl, #0xabff             ; below the upper-ROM window at &C000
    ; Graphics copies overwrite AMSDOS's old RAM workspace (&A6FC..&BFFF).
    ; Rebuild it directly; KL CHOKE OFF would follow the damaged lists first.
    call #0xbcce               ; KL INIT BACK
    ld hl, #_disc_command
    call #0xbcd4               ; KL FIND COMMAND: HL=name -> HL=proc, C=ROM cfg
    jr nc, _disk_prepare_fail
    xor a                      ; DISC takes no parameters
    call #0x001b               ; KL FAR PCHL (HL=proc, C=ROM cfg)
    ld hl, #1
    jr _disk_prepare_return
_disk_prepare_fail:
    ld hl, #0
_disk_prepare_return:
    ld sp, (_prepare_saved_sp)
    ld ix, (_prepare_saved_ix)
    ret

; Keep the firmware/AMSDOS working area (&A6FC..&BFFF) out of the chapter
; background underlay. The CPC6128's bank 7 provides an independent 16 KiB
; page at &C000 under config 1; the source remains in base RAM. This preserves
; the AMSDOS pool, ROM-state table and high-kernel jumpblock across backgrounds.
; Call only with upper ROM hidden; interrupts stay off across the map.
_disk_cache_workspace_save::
    di
    ld bc, #0x7f00
    ld a, #0xc1
    out (c), a
    ld hl, #0xa6fc
    ld de, #0xc000
    ld bc, #0x1904
    ldir
    ld bc, #0x7f00
    ld a, #0xc0
    out (c), a
    ei
    ret

_disk_cache_workspace_restore::
    di
    ld bc, #0x7f00
    ld a, #0xc1
    out (c), a
    ld hl, #0xc000
    ld de, #0xa6fc
    ld bc, #0x1904
    ldir
    ld bc, #0x7f00
    ld a, #0xc0
    out (c), a
    ei
    ret

_disk_load_ch1::
    ld hl, #_chapter1_name
    ld b, #8
    jp _load_chapter_file
_disk_load_ch2::
    ld hl, #_chapter2_name
    ld b, #8
    jp _load_chapter_file
_disk_load_ch3::
    ld hl, #_chapter3_name
    ld b, #8
    jp _load_chapter_file
_disk_load_ch4::
    ld hl, #_chapter4_name
    ld b, #8

_load_chapter_file:
    ; Firmware preserves other registers but explicitly corrupts IX. SDCC uses
    ; IX as the C frame pointer. Restore both SP and IX after the firmware read:
    ; AMSDOS must be allowed to use its workspace without altering the C frame.
    ld (_chapter_saved_sp), sp
    ld (_chapter_saved_ix), ix
    xor a
    ld (_disk_load_error), a
    ; CAS IN OPEN needs a real 2 KiB buffer even when followed by CAS IN
    ; DIRECT. Keep it past the compressed payload (max < &9000) and outside
    ; the firmware workspace at &A6FC-&BFFF. The background copy may reuse it.
    ld de, #0x9000
    call #0xbc77               ; CAS IN OPEN
    jr nc, _chapter_open_fail
    ld hl, #0x8000             ; compressed chapter data staging address
    call #0xbc83               ; CAS IN DIRECT
    jr nc, _chapter_close_fail
    call #0xbc7a               ; CAS IN CLOSE
    ld hl, #1
    jr _chapter_load_return
_chapter_close_fail:
    call #0xbc7a
    ld a, #2
    ld (_disk_load_error), a
    jr _chapter_load_fail
_chapter_open_fail:
    ld a, #1
    ld (_disk_load_error), a
    jr _chapter_load_fail
_chapter_load_fail:
    ld hl, #0
_chapter_load_return:
    ld sp, (_chapter_saved_sp)
    ld ix, (_chapter_saved_ix)
    ret

_chapter1_name:
    .ascii "CH01.BIN"
_chapter2_name:
    .ascii "CH02.BIN"
_chapter3_name:
    .ascii "CH03.BIN"
_chapter4_name:
    .ascii "CH04.BIN"
_disc_command:
    .db 'D','I','S','C'+0x80

_chapter_saved_sp:
    .dw 0
_chapter_saved_ix:
    .dw 0
_prepare_saved_sp:
    .dw 0
_prepare_saved_ix:
    .dw 0
