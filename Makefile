CPCT_PATH := $(abspath tmp/cpctelera/cpctelera)/

.PHONY: all assets assets-check assets-freeze levels levels-check campaign-check physics-plan-check test-physics-compat test-physics-host test-physics-cpc test-jump-reachability test-physics-campaign test-physics-campaign-cpc test-sim test-audio test-audio-pcm test-capture-audio test-pop-music pop-music test-machine test-sweep build campaign-disk check-map smoke-boot smoke-resets smoke-gallery test-gallery-snapshots test-platform platform-input platform-joystick test-banks test-render test-render-snapshot test-render-capture test-render-pageflip-probe platform-logic test-platform-replay-cpc test-o02-probe test-o02-backend repro test test-run-session test-run-game clean run run-m0 run-m1 doctor package
all: campaign-disk

ASSET_INPUTS := $(wildcard assets/source/canonical/*.background.scr assets/source/canonical/*.background.scr.zx0 assets/source/canonical/*.fwpal assets/source/canonical/*.hwpal assets/source/canonical/*.tiles.bin assets/source/canonical/*.map.bin assets/source/canonical/*.masked.bin)

assets: src/generated/runtime_assets.s src/generated/loading_assets.s

LOADING_ART := assets/loading

$(LOADING_ART)/banterhouse2-loading.scr: tools/build_vazquez_loading.py tools/build_cpc_screen_studies.py $(LOADING_ART)/banterhouse2-portada-vazquez.png
	python3 tools/build_vazquez_loading.py

$(LOADING_ART)/banterhouse2-loading.hwpal: $(LOADING_ART)/banterhouse2-loading.scr
	@test -f $@ || python3 tools/build_vazquez_loading.py

src/generated/loading_assets.s: tools/build_loading_assets.py $(LOADING_ART)/banterhouse2-loading.scr $(LOADING_ART)/banterhouse2-loading.hwpal
	python3 tools/build_loading_assets.py

src/generated/runtime_assets.s: tools/build_runtime_assets.py tools/build_machine_cleanup.py tools/build_cpc_screen_studies.py $(ASSET_INPUTS)
	python3 tools/build_runtime_assets.py

assets-check: assets
	python3 tools/check_canonical_assets.py
	python3 tools/test_asset_rejections.py
	python3 tools/test_runtime_assets.py

assets-freeze:
	python3 tools/freeze_canonical_assets.py

levels: src/generated/level_data.h src/generated/m0_level.h

src/generated/level_data.h: $(wildcard assets/levels/*.json assets/levels/geometries/*.json) tools/build_levels.py
	python3 tools/build_levels.py

src/generated/m0_level.h: assets/levels/m0.json tools/build_m0_level.py
	python3 tools/build_m0_level.py

levels-check: levels
	python3 tools/build_levels.py --check
	python3 tools/test_levels.py

campaign-check:
	python3 tools/check_playable_campaign.py

physics-plan-check:
	python3 tools/check_implementation_plan.py

test-physics-compat:
	python3 tools/test_player_compat.py

test-physics-host:
	mkdir -p build/tests
	$(CC) -std=c99 -Wall -Wextra -Werror -fsanitize=address,undefined -Isrc/core tests/host/test_physics.c src/core/player.c src/core/collision.c src/core/state.c -o build/tests/test_physics
	./build/tests/test_physics

test-jump-reachability:
	python3 tools/test_jump_reachability.py

test-physics-campaign:
	python3 tools/test_physics_campaign.py

test-physics-campaign-cpc: test-physics-campaign
	rm -rf build/physics-campaign/src
	mkdir -p build/physics-campaign/src/core
	cp tests/cpc/physics/campaign.c build/physics-campaign/src/main.c
	cp src/core/player.c src/core/player.h src/core/collision.c src/core/collision.h src/core/state.c src/core/state.h src/core/tuning.h build/physics-campaign/src/core/
	$(MAKE) -f project.mk all SRCDIR=build/physics-campaign/src OBJDIR=build/physics-campaign/obj BINFILE=build/physics-campaign/CAMPAIGN.bin IHXFILE=build/physics-campaign/CAMPAIGN.ihx CDT=build/physics-campaign/CAMPAIGN.cdt DSK=build/physics-campaign/CAMPAIGN.dsk TARGET=build/physics-campaign/CAMPAIGN.dsk PROJNAME=CAMPAIGN
	python3 tools/check_physics_campaign_cpc.py

test-physics-cpc:
	rm -rf build/physics/src
	mkdir -p build/physics/src/core
	cp tests/cpc/physics/main.c build/physics/src/main.c
	cp src/core/player.c src/core/player.h src/core/collision.c src/core/collision.h src/core/state.c src/core/state.h src/core/tuning.h build/physics/src/core/
	$(MAKE) -f project.mk all SRCDIR=build/physics/src OBJDIR=build/physics/obj BINFILE=build/physics/PHYSICS.bin IHXFILE=build/physics/PHYSICS.ihx CDT=build/physics/PHYSICS.cdt DSK=build/physics/PHYSICS.dsk TARGET=build/physics/PHYSICS.dsk PROJNAME=PHYSICS
	python3 tools/check_physics_cpc.py

test-sim: levels
	python3 tools/build_m0_level.py --check
	python3 tools/test_m0_level.py
	mkdir -p build/tests
	$(CC) -std=c99 -Wall -Wextra -Werror -fsanitize=address,undefined -Isrc tests/host/test_m0_level.c src/core/player.c src/core/collision.c -o build/tests/test_m0_level
	./build/tests/test_m0_level
	$(MAKE) test-physics-host
	$(MAKE) test-physics-cpc
	$(MAKE) test-physics-campaign

test-game:
	mkdir -p build/tests
	$(CC) -std=c99 -Wall -Wextra -Wno-unused-function -Wno-unused-variable -O2 -fsanitize=address,undefined -Itests/host/cpc_stub -Isrc/platform tests/host/game_harness.c src/core/player.c src/core/collision.c src/core/machine.c src/core/projectile.c src/game/flow.c src/platform/input_logic.c src/platform/audio.c src/platform/audio_logic.c -o build/tests/game_harness
	./build/tests/game_harness
	$(CC) -std=c99 -Wall -Wextra -Wno-unused-function -Wno-unused-variable -O2 -fsanitize=address,undefined -DBH2_SEAL_WINDOW_TICKS=8 -DBH2_SEAL_RECOVERY_TICKS=8 -Itests/host/cpc_stub -Isrc/platform tests/host/game_harness.c src/core/player.c src/core/collision.c src/core/machine.c src/core/projectile.c src/game/flow.c src/platform/input_logic.c src/platform/audio.c src/platform/audio_logic.c -o build/tests/game_harness_h1b
	./build/tests/game_harness_h1b

test-machine:
	mkdir -p build/tests
	python3 tools/check_m1_level.py
	$(CC) -std=c99 -Wall -Wextra -Werror -fsanitize=address,undefined -Isrc/core tests/host/test_machine_projectile.c src/core/machine.c src/core/projectile.c -o build/tests/test_machine_projectile
	./build/tests/test_machine_projectile

test-sweep:
	mkdir -p build/tests
	$(CC) -std=c99 -Wall -Wextra -Werror -fsanitize=address,undefined -Isrc/core tests/host/test_swept_collision.c src/core/collision.c -o build/tests/test_swept_collision
	./build/tests/test_swept_collision

test-audio:
	mkdir -p build/tests
	$(CC) -std=c99 -Wall -Wextra -Werror -fsanitize=address,undefined -Isrc/platform tests/host/test_audio.c src/platform/audio.c src/platform/audio_logic.c -o build/tests/test_audio
	./build/tests/test_audio

test-audio-pcm:
	python3 tools/test_analyze_ay_pcm.py
	python3 tools/test_analyze_ay_events.py
	python3 tools/test_capture_audio.py

pop-music:
	python3 tools/build_pop_ay.py

test-pop-music:
	python3 tools/test_pop_ay.py
	python3 tools/build_pop_ay.py --check

test-run-session:
	python3 tools/test_run_session.py

test-run-game:
	python3 tools/test_run_game.py

.PHONY: test-loading
test-loading: build
	python3 tools/test_loading_assets.py
	python3 tools/check_memory_map.py
	python3 tools/check_disk.py

solve-game: test-game
	./build/tests/game_harness solve
	python3 tools/build_campaign_replay.py


TAPE_TOOL := $(CPCT_PATH)tools/2cdt/bin/2cdt

$(TAPE_TOOL): tools/2cdt_compat.h
	mkdir -p $(CPCT_PATH)tools/2cdt/bin
	$(MAKE) -B -C $(CPCT_PATH)tools/2cdt CFLAGS="-O3 -fsigned-char -DUNIX -Isrc -include $(abspath tools/2cdt_compat.h)" LFLAGS2=

build: assets levels $(TAPE_TOOL) pop-music
	python3 tools/build_m1_source.py --output build/m1/src
	$(MAKE) -f project.mk all SRCDIR=build/m1/src OBJDIR=build/m1/obj M1_ONLY=1
	$(MAKE) -f project.mk build/DEVUELTO.cdt SRCDIR=build/m1/src OBJDIR=build/m1/obj M1_ONLY=1
	python3 tools/check_tape.py

check-map: build
	python3 tools/check_memory_map.py

# Full 24-arena CPC 6128 disk candidate. Chapter images are AMSDOS files and
# load only at stage boundaries; M1 remains an isolated diagnostic build.
campaign-disk: assets levels
	python3 tools/build_m1_source.py --campaign --output build/campaign/src
	$(MAKE) -f project.mk all STREAM_CAMPAIGN=1 SRCDIR=build/campaign/src OBJDIR=build/campaign/obj BINFILE=build/campaign/DEVUELTO.bin IHXFILE=build/campaign/DEVUELTO.ihx CDT=build/campaign/DEVUELTO.cdt DSK=build/campaign/DEVUELTO.dsk TARGET=build/campaign/DEVUELTO.dsk PROJNAME=DEVUELTO_CAMPAIGN
	python3 tools/attach_chapter_assets.py build/campaign/DEVUELTO.dsk
	python3 tools/check_campaign_dsk.py build/campaign/DEVUELTO.dsk build/campaign/DEVUELTO.bin build/campaign/DEVUELTO.map

smoke-boot:
	$(MAKE) -f project.mk all SRCDIR=tests/cpc/smoke/src OBJDIR=build/smoke/obj BINFILE=build/smoke/SMOKE.bin IHXFILE=build/smoke/SMOKE.ihx CDT=build/smoke/SMOKE.cdt DSK=build/smoke/SMOKE.dsk TARGET=build/smoke/SMOKE.dsk PROJNAME=SMOKE
	python3 tools/check_link_map.py build/smoke/SMOKE.map
	python3 tools/test_link_map.py
	python3 tools/check_smoke_disk.py

smoke-resets: smoke-boot
	python3 tools/test_smoke_resets.py --count 10

smoke-gallery: assets-check
	@set -e; index=1; for scene in 01-copias 02-produccion 03-calle 04-purple; do \
	  out=build/gallery/$$scene; stem=$$(printf 'GAL%02d' $$index); mkdir -p $$out/src/platform; \
	  cp tests/cpc/gallery/src/main.c $$out/src/main.c; \
	  cp tests/cpc/gallery/src/platform/gallery.s $$out/src/platform/gallery.s; \
	  python3 tools/build_gallery_assets.py $$scene --out $$out/src/platform; \
	  $(MAKE) -f project.mk all SRCDIR=$$out/src OBJDIR=$$out/obj BINFILE=$$out/$$stem.bin IHXFILE=$$out/$$stem.ihx CDT=$$out/$$stem.cdt DSK=$$out/$$stem.dsk TARGET=$$out/$$stem.dsk PROJNAME=$$stem; \
	  python3 tools/check_link_map.py $$out/$$stem.map; index=$$((index + 1)); \
	done
	python3 tools/check_gallery_profiles.py

test-gallery-snapshots:
	python3 tools/check_gallery_snapshots.py
	python3 tools/test_caprice_snapshot_palette.py

test-platform:
	rm -rf build/platform/src
	mkdir -p build/platform/src/platform
	cp tests/cpc/platform/src/main.c build/platform/src/main.c
	cp src/platform/clock.c src/platform/input.c src/platform/input_logic.c src/platform/clock_logic.c src/platform/telemetry.c build/platform/src/platform/
	$(MAKE) -f project.mk all SRCDIR=build/platform/src OBJDIR=build/platform/obj BINFILE=build/platform/PLATFORM.bin IHXFILE=build/platform/PLATFORM.ihx CDT=build/platform/PLATFORM.cdt DSK=build/platform/PLATFORM.dsk TARGET=build/platform/PLATFORM.dsk PROJNAME=PLATFORM
	python3 tools/check_link_map.py build/platform/PLATFORM.map
	python3 tools/check_platform_disk.py

# One-VSYNC derivative for interactive keyboard probing; it intentionally does
# not replace P01's separate 3000-VSYNC CPC run.
platform-input:
	rm -rf build/platform-input/src
	mkdir -p build/platform-input/src/platform
	sed 's/^#define PLATFORM_TEST_FRAMES 3000$$/#define PLATFORM_TEST_FRAMES 1/' tests/cpc/platform/src/main.c > build/platform-input/src/main.c
	cp src/platform/clock.c src/platform/input.c src/platform/input_logic.c src/platform/clock_logic.c src/platform/telemetry.c build/platform-input/src/platform/
	$(MAKE) -f project.mk all SRCDIR=build/platform-input/src OBJDIR=build/platform-input/obj BINFILE=build/platform-input/PLATFORM.bin IHXFILE=build/platform-input/PLATFORM.ihx CDT=build/platform-input/PLATFORM.cdt DSK=build/platform-input/PLATFORM.dsk TARGET=build/platform-input/PLATFORM.dsk PROJNAME=PLATFORM_INPUT
	python3 tools/check_link_map.py build/platform-input/PLATFORM.map
	python3 tools/check_platform_disk.py build/platform-input/PLATFORM.dsk

# Test-only diagnostic that ignores keyboard keys and reads Joy0 exclusively.
# Run with a Caprice profile that maps host arrows/X/Z to its emulated joystick.
platform-joystick:
	rm -rf build/platform-joystick/src
	mkdir -p build/platform-joystick/src/platform
	cp tests/cpc/platform/src/main.c build/platform-joystick/src/main.c
	cp src/platform/clock.c src/platform/input_logic.c src/platform/clock_logic.c src/platform/telemetry.c build/platform-joystick/src/platform/
	python3 tools/build_joystick_input_probe.py src/platform/input.c build/platform-joystick/src/platform/input.c
	$(MAKE) -f project.mk all SRCDIR=build/platform-joystick/src OBJDIR=build/platform-joystick/obj BINFILE=build/platform-joystick/PLATFORM.bin IHXFILE=build/platform-joystick/PLATFORM.ihx CDT=build/platform-joystick/PLATFORM.cdt DSK=build/platform-joystick/PLATFORM.dsk TARGET=build/platform-joystick/PLATFORM.dsk PROJNAME=PLATFORM_JOYSTICK
	python3 tools/check_link_map.py build/platform-joystick/PLATFORM.map
	python3 tools/check_platform_disk.py build/platform-joystick/PLATFORM.dsk

test-banks:
	rm -rf build/banks/src
	mkdir -p build/banks/src/platform
	cp tests/cpc/banks/main.c build/banks/src/main.c
	cp tests/cpc/banks/irq_probe.s build/banks/src/platform/irq_probe.s
	cp src/platform/banks.c src/platform/banks.h src/platform/bank_page.s src/platform/clock.c src/platform/clock.h build/banks/src/platform/
	$(MAKE) -f project.mk all SRCDIR=build/banks/src OBJDIR=build/banks/obj BINFILE=build/banks/BANKS.bin IHXFILE=build/banks/BANKS.ihx CDT=build/banks/BANKS.cdt DSK=build/banks/BANKS.dsk TARGET=build/banks/BANKS.dsk PROJNAME=BANKS Z80CCLINKARGS="-mz80 --sdcccall 0 --no-std-crt0 -Wl-u --code-loc 0x0100 --data-loc 0x3000 -l$(CPCT_PATH)cpctelera.lib"
	python3 tools/check_banks_map.py build/banks/BANKS.map
	python3 tools/check_banks_disk.py

test-render:
	python3 tools/build_render_assets.py
	python3 tools/build_render_fixture.py $(RENDER_FRAME_ARGS)
	python3 tools/test_render_reference.py
	rm -rf build/render-cpc/src
	mkdir -p build/render-cpc/src/platform build/render-cpc/src/render
	cp tests/cpc/render/main.c build/render-cpc/src/main.c
	cp src/render/render_g.c src/render/render_g.h build/render-cpc/src/render/
	cp src/platform/banks.c src/platform/banks.h src/platform/bank_page.s build/render-cpc/src/platform/
	cp build/render-assets/render_assets.s build/render-cpc/src/platform/
	cp build/render-assets/render_asset_layout.h build/render-cpc/src/
	cp build/render-cpc/render_scenarios.h build/render-cpc/src/
	$(MAKE) -f project.mk all SRCDIR=build/render-cpc/src OBJDIR=build/render-cpc/obj BINFILE=build/render-cpc/RENDER.bin IHXFILE=build/render-cpc/RENDER.ihx CDT=build/render-cpc/RENDER.cdt DSK=build/render-cpc/RENDER.dsk TARGET=build/render-cpc/RENDER.dsk PROJNAME=RENDER Z80CCLINKARGS="-mz80 --sdcccall 0 --no-std-crt0 -Wl-u --code-loc 0x0100 --data-loc 0x3C00 -l$(CPCT_PATH)cpctelera.lib"
	python3 tools/check_render_map.py build/render-cpc/RENDER.map
	python3 tools/check_render_disk.py build/render-cpc/RENDER.dsk

RENDER_SNAPSHOT ?= research/runs/20261013T-T06-render/cpc-pass.sna
test-render-snapshot:
	python3 tools/check_render_snapshot.py $(RENDER_SNAPSHOT)


test-render-capture:
	python3 tools/build_render_assets.py
	python3 tools/build_render_fixture.py
	rm -rf build/render-capture/src
	mkdir -p build/render-capture/src/platform build/render-capture/src/render
	cp tests/cpc/render/main.c build/render-capture/src/main.c
	cp src/render/render_g.c src/render/render_g.h build/render-capture/src/render/
	cp src/platform/banks.c src/platform/banks.h src/platform/bank_page.s build/render-capture/src/platform/
	cp build/render-assets/render_assets.s build/render-capture/src/platform/
	cp build/render-assets/render_asset_layout.h build/render-capture/src/
	cp build/render-cpc/render_scenarios.h build/render-capture/src/
	$(MAKE) -f project.mk all SRCDIR=build/render-capture/src OBJDIR=build/render-capture/obj BINFILE=build/render-capture/RENDER.bin IHXFILE=build/render-capture/RENDER.ihx CDT=build/render-capture/RENDER.cdt DSK=build/render-capture/RENDER.dsk TARGET=build/render-capture/RENDER.dsk PROJNAME=RENDERCAP Z80CCFLAGS="--sdcccall 0 --opt-code-size -DRENDER_REALTIME_CAPTURE" Z80CCLINKARGS="-mz80 --sdcccall 0 --no-std-crt0 -Wl-u --code-loc 0x0100 --data-loc 0x3C00 -l$(CPCT_PATH)cpctelera.lib"
	python3 tools/check_render_map.py build/render-capture/RENDER.map
	python3 tools/check_render_disk.py build/render-capture/RENDER.dsk

test-render-pageflip-probe:
	rm -rf build/render-pageflip/src
	mkdir -p build/render-pageflip/src
	cp tests/cpc/render/pageflip_probe.c build/render-pageflip/src/main.c
	$(MAKE) -f project.mk all SRCDIR=build/render-pageflip/src OBJDIR=build/render-pageflip/obj BINFILE=build/render-pageflip/PROBE.bin IHXFILE=build/render-pageflip/PROBE.ihx CDT=build/render-pageflip/PROBE.cdt DSK=build/render-pageflip/PROBE.dsk TARGET=build/render-pageflip/PROBE.dsk PROJNAME=PROBE Z80CCLINKARGS="-mz80 --sdcccall 0 --no-std-crt0 -Wl-u --code-loc 0x0100 --data-loc 0x3C00 -l$(CPCT_PATH)cpctelera.lib"

platform-logic:
	mkdir -p build
	$(CC) -std=c99 -Wall -Wextra -Werror -fsanitize=address,undefined -Isrc/platform tools/test_platform_logic.c src/platform/input_logic.c src/platform/clock_logic.c -o build/platform_logic_test
	./build/platform_logic_test

test-o02-probe:
	mkdir -p build/o02-probe/src/platform
	cp tests/cpc/telemetry/main.c build/o02-probe/src/main.c
	cp tests/cpc/telemetry/probes.s build/o02-probe/src/platform/probes.s
	$(MAKE) -f project.mk all SRCDIR=build/o02-probe/src OBJDIR=build/o02-probe/obj BINFILE=build/o02-probe/O02.bin IHXFILE=build/o02-probe/O02.ihx CDT=build/o02-probe/O02.cdt DSK=build/o02-probe/O02.dsk TARGET=build/o02-probe/O02.dsk PROJNAME=O02 Z80CCLINKARGS="-mz80 --sdcccall 0 --no-std-crt0 -Wl-u --code-loc 0x0100 --data-loc 0x3C00 -l$(CPCT_PATH)cpctelera.lib"
	python3 tools/check_link_map.py build/o02-probe/O02.map --regions cfg/o02-memory.json

test-o02-backend:
	python3 tools/test_cpc_backend.py

test-platform-replay-cpc:
	rm -rf build/cadence/src
	mkdir -p build/cadence/src/core
	cp tests/cpc/physics/cadence.c build/cadence/src/main.c
	cp src/core/player.c src/core/player.h src/core/collision.c src/core/collision.h src/core/state.c src/core/state.h src/core/tuning.h build/cadence/src/core/
	$(MAKE) -f project.mk all SRCDIR=build/cadence/src OBJDIR=build/cadence/obj BINFILE=build/cadence/CADENCE.bin IHXFILE=build/cadence/CADENCE.ihx CDT=build/cadence/CADENCE.cdt DSK=build/cadence/CADENCE.dsk TARGET=build/cadence/CADENCE.dsk PROJNAME=CADENCE
	python3 tools/check_link_map.py build/cadence/CADENCE.map
	python3 tools/check_cadence_cpc.py

test-game-build: build
	python3 tools/test_game_build.py

repro: smoke-boot
	python3 tools/test_reproducible_build.py

test-lab: test-game test-audio test-pop-music test-machine test-sweep test-game-build assets-check levels-check campaign-check build check-map smoke-boot smoke-gallery test-gallery-snapshots test-platform test-banks test-render platform-logic test-platform-replay-cpc test-sim test-jump-reachability repro
	python3 tools/check_disk.py

run:
	python3 tools/run_game.py

run-m0: build
	python3 tools/run_game.py build/DEVUELTO.dsk

run-m1: build test-machine
	python3 tools/run_game.py build/DEVUELTO.dsk

run-candidate: campaign-disk
	python3 tools/run_game.py build/campaign/DEVUELTO.dsk

doctor:
	python3 tools/doctor.py

# Portable entry points: no emulator, ROM or archived session is required.
.PHONY: bootstrap test-host public-check test-lab
test: public-check test-host

bootstrap:
	python3 tools/bootstrap_toolchain.py

test-host: test-game test-audio test-pop-music test-machine test-sweep platform-logic test-physics-host test-physics-campaign test-jump-reachability levels-check campaign-check
	python3 tools/check_canonical_assets.py
	python3 tools/test_asset_rejections.py
	python3 tools/test_run_session.py
	python3 tools/test_run_game.py

public-check:
	python3 tools/check_public_repo.py
	python3 tools/test_public_repo.py

package: test-lab
	python3 tools/package_release.py

clean:
	rm -rf build
