include cfg/build_config.mk
ifneq ($(wildcard $(SRCDIR)/generated/loading_assets.s),)
Z80CCLINKARGS += -Wl-b_LOADING=0x8000
endif
ifeq ($(M1_ONLY),1)
Z80CCFLAGS += -DBH2_M1_ONLY
M1_SEAL_WINDOW ?= 6
M1_SEAL_RECOVERY ?= 8
Z80CCFLAGS += -DBH2_SEAL_WINDOW_TICKS=$(M1_SEAL_WINDOW) -DBH2_SEAL_RECOVERY_TICKS=$(M1_SEAL_RECOVERY)
endif
ifeq ($(STREAM_CAMPAIGN),1)
Z80CCFLAGS += -DBH2_STREAM_CHAPTERS
endif
include $(CPCT_PATH)cfg/global_main_makefile.mk

# These are isolated experiments, not part of the shipping game. Exclude them
# for canonical, M1, and generated campaign source trees alike.
OBJFILES := $(filter-out $(OBJDIR)/core/state.rel $(OBJDIR)/platform/banks.rel $(OBJDIR)/platform/bank_page.rel $(OBJDIR)/render/render_g.rel,$(OBJFILES))

# The SDK sets these variables only when binaryAddresses.log is rebuilt.
# Re-read them for standalone tape builds; otherwise an up-to-date BIN can
# silently produce a CDT with LOAD=0 and EXEC=0.
%.cdt: $(BINFILE) $(BINADDRLOG)
	@$(call GETLOADADDRESS,LOADADDR,$(<).log)
	@$(call GETRUNADDRESS,RUNADDR,$(<:.bin=.map))
	@$(call CHECKVARIABLEISSET,LOADADDR)
	@$(call CHECKVARIABLEISSET,RUNADDR)
	@$(call CREATECDT,$<,$(notdir $<),$@,$(LOADADDR),$(RUNADDR))

# CPCtelera's original rules only track .c files. Headers change physics, ABI,
# generated levels and replay data, so all C objects must depend on them.
PROJECT_HEADERS := $(shell find $(SRCDIR) -name '*.h') $(wildcard src/platform/*.h)
$(C_OBJFILES): $(PROJECT_HEADERS) cfg/build_config.mk project.mk
