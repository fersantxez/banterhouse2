THIS_FILE_PATH := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
CPCT_PATH := $(abspath $(THIS_FILE_PATH)../tmp/cpctelera/cpctelera)/
PROJNAME := DEVUELTO
Z80CODELOC := 0x0100
SRCDIR := src
OBJDIR := build/obj
BINFILE := build/DEVUELTO.bin
IHXFILE := build/DEVUELTO.ihx
CDT := build/DEVUELTO.cdt
DSK := build/DEVUELTO.dsk
TARGET := $(DSK)
C_EXT := c
ASM_EXT := s
OBJ_EXT := rel

include $(CPCT_PATH)cfg/global_paths.mk
# Use the caller's PATH; command-line overrides still take precedence.
Z80CC := sdcc
Z80ASM := sdasz80
Z80LNK := sdar
HEX2BIN := $(CPCT_PATH)tools/hex2bin-2.0/bin/hex2bin
IDSK := $(CPCT_PATH)tools/iDSK-0.13/bin/iDSK
Z80CCFLAGS := --sdcccall 0 --opt-code-size
Z80ASMFLAGS := -plosgff
Z80CCINCLUDE := -I$(CPCT_PATH)src -I$(abspath src/platform)
# The 24-arena executable uses the measured gap above resident globals. The
# enlarged global reservation still ends before the existing stack guard.
Z80CCLINKARGS := -mz80 --sdcccall 0 --no-std-crt0 -Wl-u --code-loc $(Z80CODELOC) --data-loc 0x7C50 -l$(CPCT_PATH)cpctelera.lib
include $(CPCT_PATH)cfg/global_functions.mk

SUBDIRS := $(filter-out ., $(shell find $(SRCDIR) -type d -print))
OBJSUBDIRS := $(foreach DIR,$(SUBDIRS),$(patsubst $(SRCDIR)%, $(OBJDIR)%, $(DIR)))
CFILES := $(foreach DIR,$(SUBDIRS),$(wildcard $(DIR)/*.$(C_EXT)))
ASMFILES := $(foreach DIR,$(SUBDIRS),$(wildcard $(DIR)/*.$(ASM_EXT)))
C_OBJFILES := $(patsubst $(SRCDIR)%, $(OBJDIR)%, $(patsubst %.$(C_EXT), %.$(OBJ_EXT), $(CFILES)))
ASM_OBJFILES := $(patsubst $(SRCDIR)%, $(OBJDIR)%, $(patsubst %.$(ASM_EXT), %.$(OBJ_EXT), $(ASMFILES)))
OBJFILES := $(C_OBJFILES) $(ASM_OBJFILES)
# Isolated bank/renderer experiments are built by their own fixture targets.
# Do not spend resident game RAM on implementations the game never calls.
ifeq ($(SRCDIR),src)
OBJFILES := $(filter-out $(OBJDIR)/core/state.rel $(OBJDIR)/platform/banks.rel $(OBJDIR)/platform/bank_page.rel $(OBJDIR)/render/render_g.rel,$(OBJFILES))
endif
ifeq ($(M1_ONLY),1)
OBJFILES := $(filter-out $(OBJDIR)/core/state.rel $(OBJDIR)/platform/banks.rel $(OBJDIR)/platform/bank_page.rel $(OBJDIR)/render/render_g.rel,$(OBJFILES))
endif
GENOBJFILES :=
BIN_OBJFILES :=
GENC_OBJFILES :=
GENASM_OBJFILES :=
OBJS2CLEAN :=
