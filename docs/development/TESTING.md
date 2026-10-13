# Pruebas

## Tests en el ordenador

Después de instalar las dependencias con `make bootstrap`, ejecuta:

```sh
make test
make
```

`make test` revisa los archivos y enlaces del repositorio y ejecuta los tests de física, colisiones, máquinas, audio, niveles, controles y gestión de procesos. Usa C, Python y sanitizadores; no abre un emulador ni necesita ROM.

`make` compila el disco y comprueba que sus archivos coinciden con el binario y el mapa de memoria generados.

GitHub ejecuta `make public-check` y `make test-host` en cada push y pull request. La [primera ejecución](https://github.com/fersantxez/banterhouse2/actions/runs/38470367753), sobre el commit `300c78b`, pasó el 13 de octubre de 2026. La compilación completa del CPC se ha comprobado localmente en macOS.

## Pruebas en emulador

Usa el disco que acabas de compilar, con el emulador configurado como CPC 6128 de 128 KiB. Comprueba el arranque desde frío, los menús, el movimiento, la muerte, el reintento, la pausa, el sonido, los cambios de capítulo y el final.

La tecla D del menú reproduce una partida con entradas predeterminadas. Sirve para repetir un recorrido, pero hay que probar también una partida normal con el teclado o el joystick.

El lanzador de pruebas espera Caprice32 en `.tools/cap32`, su configuración en `.tools/cap32.cfg` y las ROM en `.tools/rom/`. También admite rutas externas:

```sh
python3 tools/run_game.py --emulator RUTA_CAPRICE --config-template PERFIL_CFG
```

`python3 tools/doctor.py --emulator` comprueba la instalación local. Los scripts [run_game.py](../../tools/run_game.py) y [run_session.py](../../tools/run_session.py) guardan los resultados en `research/runs/` y cierran los procesos que han abierto, también si fallan o agotan el tiempo de espera.

`make test-lab` necesita capturas y herramientas de pruebas anteriores. No se puede ejecutar entero desde un clon público sin recuperar esos archivos. Lo mismo ocurre con `validate_release_evidence.py`, que comprueba las pruebas enumeradas en `research/release-validation.json`.

## Rendimiento y sonido

Anota el SHA-256 del disco, las versiones del emulador y del sistema, y las condiciones de la prueba. Mide por separado los pasos de simulación, las imágenes dibujadas y la velocidad del emulador. Los tiempos del navegador no indican por sí solos cuánto tarda el CPC en ejecutar el código.

Graba el audio para revisar silencios y saturación. Escúchalo también durante una partida: los efectos deben oírse sin tapar la música y las pausas no deben dejar notas sonando.

## Pruebas pendientes

Falta probar en un CPC físico, con su disquetera y las distintas variantes de CRTC. También falta probar con jugadores para ajustar dificultad, controles y música. Hay una [plantilla de sesión](../PLAYTEST.md).

Guarda los resultados, incluidos los fallos, junto al hash del disco probado. Cuando cambie el DSK, repite las pruebas afectadas. Los resultados de la [entrega anterior](../DELIVERY_REPORT.md) corresponden a ese disco concreto.
