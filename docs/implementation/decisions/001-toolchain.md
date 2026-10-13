# 001 — Toolchain observada en el candidato

Estado: fijación y verificación local para el DSK CPC clásico; reproducibilidad limpia y CPC físico aún pendientes.

La fuente canónica es [cfg/toolchain.lock.json](../../../cfg/toolchain.lock.json). Versiones observadas en este Mac: SDCC 4.6.0 #16555, SDAS 05.50.4, `sdar` de la misma distribución y Apple clang 21.0.0 arm64. El build usa `--sdcccall 0 --opt-code-size`, SDAS `-plosgff` y linker con código `0100`/datos `7800`.

CPCTelera está fijada a `b3f48a1b49dc9d99b73c75f98cefaf9c1e60dc31`; SHA de la biblioteca usada en esta auditoría: `64191573c577c44cfd8f0d47d7500f6feba85c91baf7f0ae0d45ddde2c957f09`. Caprice32 4.6.0 usa copia local y ROM CPC 6128 SHA `31c3668c67bea027dab698ece233c9434d9324f9ba7dac84db58f400b6689562`.

**Verificado en este paso:** `make doctor` devuelve código 0 y encuentra compilador, ensamblador, archivador, SDK/library, ZX0, utilidades AMSDOS/DSK, emulador y ROM; el SHA Git local coincide. `make package` también devuelve 0 con assets, validador estático de 24 arenas, enlace/mapa, lector de DSK y paquete. Las dos mediciones son de este host. No prueban diez resets limpios, corrección C→ASM universal, timing, audio escuchado o hardware.

CoreAudio de esta sesión no permite a Caprice iniciar `AudioQueue`; por eso los ensayos AY de escucha no pasan aquí. La configuración de Caprice remapea flechas y X/Z a joystick cuando `joystick_emulation=1`; el juego lee tanto teclado como `Joy0`. Se verificará cada ruta desde una sesión reiniciada antes de certificar controles.
