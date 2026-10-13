# O00 — Estado real del runtime y preservación

Fecha: 11 de octubre de 2026. Auditoría local estática; no es benchmark.

## Snapshot

`research/runs/20261011T195739Z-O00-audit/inventory.json` registra y copia 73 archivos de fuente, configuración, herramientas, recursos usados y artefactos del candidato. Los 73 hashes originales y de snapshot coinciden y la fuente no cambió durante la copia. BIN/DSK existentes se etiquetaron `unverified-existing`; no se ejecutó `make clean`.

El DSK que estaba en `build/DEVUELTO.dsk` y el de `dist/Devuelto-CPC6128.dsk` comparten SHA-256 `d31c11ec657a22ae8d7789703f8962abc4ad0ebaebe9a590ffae9f9e1085f78f`. La declaración de release coincide con el hash observado. Ese dato identifica los bytes; no reemplaza las pruebas de juego.

## Diferencias del código observado

| Área | Observación | Seguimiento |
|---|---|---|
| Arranque | El binario se enlaza desde `0100`; el stack inicial es `7ff0`. | T02 debe crear un perfil independiente y medir guardas. No paginar `4000–7fff` con esta pila. |
| Vídeo/fondo | Pantalla `c000`, fondo limpio `8000`; no hay API de banco del juego. | T05/O11 antes de proponer paginación. El candidato actual no acredita uso de 128 KiB. |
| Build | Existen `assets`, `assets-check`, `campaign-check`, `build`, `check-map`, `test`, `run`, `doctor`, `package`; sus scripts existen en esta revisión. | T01 comprobará invocación/versions; la auditoría sólo comprobó rutas. No se encontraron scripts ausentes en las recetas Make. |
| Entrada | Escaneo y lectura se hacen dentro de `game_tick`; acciones y movimiento comparten bitmask C, flechas también se consultan como joystick emulado. | Probar cada tecla en Caprice con estado/captura reproducibles; los movimientos de CUA son observación breve, no aprueban P02. |
| Inicio | `MODE_TITLE` es un marcador de color dentro de la arena. No compone una portada, menú de opciones ni selección accesible. | Añadir pantalla de entrada/menu después de fijar teclado; cubrir con replay. |
| Sonido | `src/platform/audio.s` inicializa AY y emite SFX en canal A; no hay secuenciador musical. | T17 exige música; O12 debe medir audio, no llamar «música» a SFX compilados. |
| Renderer | Sprites enmascarados genéricos CPCTelera y copias en bucle C; existen variantes espejadas/alineadas generadas. | O04/O07–O10; la extensión `.s` del fichero generado no implica sprites compilados. |
| Simulación | Aritmética y colisión de papel son discretas; el cierre de salida muestra condiciones incompatibles en `update_papers` y al final de `game_tick`. | Abrir regresión en T07/T12/T13: una condición comprueba Pitu en x40–54 y luego exige simultáneamente x18–32. No puede cumplirse. |
| Campaña | Tabla estática de 24 posiciones valida rangos/soportes con script host. | El script es estructural; no demuestra terminar las 24 arenas en CPC. |
| Canales AY | SFX cambia generador/volumen de A; escucha no disponible en host. | Cualquier música debe reservar otro canal o suspenderse; la aceptación final requiere escuchar en un entorno con audio. |

## Límite de esta tarea

El snapshot demuestra recuperación de los archivos y hashes en el instante de O00. Caprice mostró el DSK arrancado y se observaron pulsaciones breves de flechas y P; el personaje parpadeó/desapareció durante las observaciones y una flecha dejó Caprice en BASIC `Ready` hasta pulsar Return. Es evidencia de que hay que automatizar/estabilizar el arranque y la captura; no se considera una prueba de teclado aprobada.

No se ha ejecutado todavía el suite completo del paquete en esta sesión. Próximo paso obligatorio T01: registrar/fijar toolchain de esta revisión. Después seguir T02–T06 y usar un harness de entrada/captura antes de cambiar el menú. El proyecto original sólo se consultó en modo lectura.
