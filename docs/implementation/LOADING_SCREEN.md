# Pantalla de arranque · 13 de octubre de 2026

Integración acotada solicitada por el usuario. No cierra N04–N10 ni cambia la aceptación general del juego, todavía pendiente de reparación y revalidación.

## Implementación

- Ilustración: `assets/concepts/cover-comic/banterhouse2-loading.scr` y `.hwpal`; Pitu conserva su sprite canónico.
- `tools/build_loading_assets.py` comprime con ZX0 y genera `src/generated/loading_assets.s`.
- El linker coloca `_LOADING` en `&8000–&99CE`: 6.607 bytes temporales. El código acaba en `&70B3`, los datos en `&78C8` y la pila arranca en `&7FF0`. No se cargan recursos encima de la zona de firmware `&A700` en adelante.
- `show_loading_screen()` oculta la descompresión con tintas negras, descomprime en `&C000`, aplica la paleta y espera 150 flancos VSYNC. Después `load_stage()` reutiliza `&8000–&BFFF` como fondo y presenta el menú.
- La pantalla aparece después de cargar el programa completo. La espera de cinta anterior a la ilustración es independiente.
- Disco y cinta incluyen el mismo binario de 39.119 bytes, cargado en `&0100` y ejecutado en `&2427`. `make build` genera ambos.
- La herramienta 2CDT del SDK necesita dos declaraciones ausentes para compilar con Clang: `tools/2cdt_compat.h` las aporta sin editar el SDK.
- Se corrigió además la receta independiente de CDT: el SDK sólo calculaba LOAD/EXEC cuando regeneraba `binaryAddresses.log`; con ese archivo al día emitía ambas direcciones como cero. La receta ahora vuelve a leer el log y el mapa. `tools/check_tape.py` decodifica los 20 bloques, verifica CRC, direcciones, indicadores primero/último y compara el contenido con BIN; `make build` exige ese check.

## Uso

```sh
make build
python3 tools/run_game.py build/DEVUELTO.dsk
python3 tools/run_game.py build/DEVUELTO.cdt
```

`Jugar-portada.command` abre este candidato desde disco. En un CPC/emulador con BASIC: disco `RUN"DEVUELTO.BIN"`; cinta `|TAPE`, `RUN""`, reproducir cinta y pulsar una tecla. El lanzador automatiza esa secuencia para Caprice.

## Pruebas

Evidencia: `research/runs/20261013-loading-integration/`.

- `asset-tests.log`: bitmap enlazado y descomprimido idéntico al original, paleta exacta, mapa de memoria y extracción de BIN desde DSK correctos.
- `host-tests.log`: pruebas existentes del juego con sanitizadores, ambas ventanas del sello, pasan.
- `repro-final.log`: reconstrucción independiente de BIN, DSK y CDT tras corregir sus direcciones. La primera reproducción anterior coincidía también, pero reprodujo el error de la cinta; reproducibilidad por sí sola no acredita carga.
- `disk-verified-2/result.json`: arranque frío en Caprice32 4.6.0, CPC 6128 clásico 128 KiB. Dos snapshots contienen la pantalla completa y sus 16 tintas exactas; después se alcanza menú y partida con Espacio. El código en RAM coincide con el candidato, excluyendo la zona mutable del SDK.
- `disk-session/`: primera inspección visual confirma ilustración y menú. El alias textual SNAPSHOT no existía en ese binario de Caprice; esa sesión sólo sirve como evidencia visual. La segunda usa el protocolo de teclas del emulador para Shift-F3.
- `disk-verified/`: intento rechazado por el cerrojo de otra sesión; no se abrió un segundo emulador.
- `tape-verified/result.json`: primer ensayo rechazado. La cinta con LOAD/EXEC a cero volvió a BASIC. Se conserva el CDT defectuoso y toda la evidencia.
- `tape-fixed/result.json`: **PASS** con el CDT corregido. Dos snapshots muestran bitmap y tintas exactos en Mode 0; después se observan menú y partida. Se cargó desde el firmware mediante `|TAPE` y `RUN""`, sin inyectar memoria. Esta repetición usó velocidad de reproducción 2× del emulador; el CPC siguió siendo el modelo clásico 6128 de 128 KiB. La sesión completa duró 152,959 s de reloj del host, incluyendo capturas posteriores. El disco se ensayó a velocidad normal. Ambos supervisores confirman `process_group_absent=true`.

### Artefactos probados

| Archivo | SHA-256 |
|---|---|
| `build/DEVUELTO.bin` | `d29544c58df1c58ce34ccb4550b2771ce81bc0f2edf7c54ecb003c94579400d6` |
| `build/DEVUELTO.dsk` | `344bc15f62c09e2433b7d3b19b046362a11337c8d0b2dedfbaa73d02da267ab8` |
| `build/DEVUELTO.cdt` | `00acc24a5d640c329ab665f7dd3d3ce4c449bdce0de8eb39b418e4d05e1715fc` |

Las carpetas `disk-verified-2/` y `tape-fixed/` conservan copias de los medios probados. El cambio de la receta de cinta no alteró BIN ni DSK, de modo que la evidencia de disco sigue correspondiendo a estos mismos bytes.

Repetición, con directorios de salida nuevos:

```sh
make test-loading
python3 tools/test_loading_runtime.py --medium disk --out research/runs/mi-prueba-disco
python3 tools/test_loading_runtime.py --medium tape --out research/runs/mi-prueba-cinta
```

El supervisor conserva configuración, comandos, logs y capturas, impide sesiones simultáneas y cierra su propio proceso incluso en timeout. El test sólo pasa si ve pantalla, menú posterior, partida y limpieza. No inyecta RAM ni carga snapshots para simular el arranque.

No hay prueba en CPC físico ni validación global de campaña/audio. Los 150 VSYNC son la duración programada; las capturas corroboran permanencia y transición, sin constituir una medición de laboratorio del tiempo visible.
