# 007 — Servicio de reloj y diagnóstico CPC (T04, en curso)

Fecha: 2026-10-11. Perfil objetivo: CPC 6128 clásico con 128 KiB; emulación observada con Caprice32 4.6.0.

## Mecanismo implementado

- La rutina corta `clock_irq` cuenta las interrupciones del CPC; cada seis produce un tick lógico y suma una entrada a una cola saturante de ticks pendientes. La ISR no lee PPI/AY, no dibuja y no ejecuta simulación.
- Las lecturas de 16 bits usan `LD A,I` para conservar IFF2, `DI` para leer atómicamente y `EI` sólo si las interrupciones estaban habilitadas al entrar. `clock_pop_tick` guarda AF antes de restar el contador porque `OR`/`DEC` cambian P/V; restaurar P/V desde la operación aritmética podía dejar las interrupciones apagadas.
- El sondeo de VSYNC lee el bit 0 del PPI B con puerto `&F500` (byte alto `&F5`, según la constante `PPI_PORT_B` de CPCTelera), espera primero el nivel inactivo y luego el activo. No se convierte el indicador de FPS del emulador en una medición de periodo.
- El perfil diagnóstico fija SP en `&7FF0` antes del salto al prólogo C. Cambiarlo dentro de `platform_main` invalida el marco local que el compilador ya había creado.
- La pantalla usa una fuente Mode 0 de 3×5; evita `cpct_drawStringM0` en el perfil enlazado bajo `&4000`, donde esa rutina habilita la ROM baja y puede ocultarse a sí misma. Los indicadores de entrada escriben bytes de VRAM directamente.

## Evidencia disponible

- `make test-platform`, `make platform-logic`, `make test` y `make package` pasaron durante esta sesión. Los tests host verifican diferencias modulares de 16 bits, sobrecarga y flancos derivados; no sustituyen la prueba en CPC.
- En una ejecución exploratoria de 30 intervalos VSYNC visibles en Caprice32 4.6.0, la pantalla leyó 30 ticks, 181 interrupciones y un mínimo/máximo de 6 interrupciones por intervalo. Es un smoke corto, no el P01 requerido de 3.000 intervalos.
- Los intentos de P01 largo no dejaron una pantalla final estable con cifras: una corrida mostró progreso parcial y otra volvió a BASIC al terminar. Se excluyen como pase. No hay lectura de T-states ni de periodo absoluto guardada.
- La salida de Caprice mostró aproximadamente 49–51 FPS durante actividad; es un indicador de presentación del emulador, no una medición del periodo CPC.

## Pendiente

P01 de 3.000 intervalos debe repetirse con cifras finales legibles. P02 requiere mantener, soltar y volver a pulsar cada tecla y las combinaciones de C3; el diagnóstico aún no registra esa matriz completa. P03 requiere replay con simulación por tick, que se implementa en T07; mientras tanto se puede validar el consumo del scheduler con un fixture determinista. P04 tiene wrap y predicate de overrun en pruebas host, pero falta acumular más de dos ticks pendientes y mostrar su recuperación en CPC.

## Seguimiento 2026-10-12

El perfil reconstruido completó el bucle de 3.000 VSYNC en Caprice32 4.6.0 sobre CPC 6128/128 KiB y mostró el panel de fin de P01. El indicador parecía decir `PASS 50HZ TICK LOCK`, pero el texto Mode 0 de 3×5 no permitió transcribir con fiabilidad las cifras de ticks e IRQ. Registro el resultado como parcial, sin declarar periodo ni jitter exactos. La prueba de Derecha tampoco produjo una transición claramente legible en las filas held/pressed/released. Datos, límites y hashes: `research/runs/20261012T160659Z-T04-clock-3000/results.json`.


## Seguimiento 2026-10-12 — panel ampliado

Se añadieron números ampliados para el panel final y una sobrecarga intencional acotada para ejercitar la cola. `make test-platform` (mapa residente y catálogo DSK incluidos) y `make platform-logic` pasan. La corrida revisada en Caprice no dejó un panel final transcribible de forma fiable; por tanto P01 no aporta cifras, P02 no se ejecutó como matriz y P04 sigue sin validación visual. No se infieren periodo, jitter ni aprobación a partir del OSD. Evidencia: `research/runs/20261012T-T04-readable-panel/results.json`.

## Seguimiento 2026-10-12 — corrida CPC reconstruida

Tras reconstruir `build/platform/PLATFORM.dsk` desde la fuente actual y arrancarlo con `RUN"PLATFORM.BIN"` en Caprice32 4.6.0/CPC 6128, el panel final apareció tras el tramo largo. La lectura visual fue: ticks `3011`, IRQ `18067`, mínimo/máximo `06/06`; no archivamos una captura raster y la transcripción debe tratarse con cautela. El panel informa 3000 intervalos, pero 3011 ticks excede el margen ±1 del ensayo, así que P01 falla y requiere diagnóstico. En la inyección de overrun se vio `03`, y el valor posterior a `while(clock_pop_tick())` fue `04`; P04 no demuestra recuperación limpia. P02 no se ejecutó como matriz, P03 sigue a la espera de T07. Artefacto: `research/runs/20261012T-T04-3000-rebuilt/results.json`.

En una repetición CPC corta se movió la lectura de cola a inmediatamente después de drenar y antes de dibujar. El panel mostró 30 ticks, 181 IRQ, mínimo/máximo 6/6, `OVERRUN 03` y `DRAINED 00`. Esto verifica la recuperación de la inyección corta P04; no cambia el fallo de tolerancia P01 a 3000 ni sustituye P02. Al pulsar Derecha tras el panel, Caprice volvió a BASIC; se requiere aislar esa reacción antes de aceptar P02. Evidencia: `research/runs/20261012T-T04-drain-snapshot/results.json`.


## Seguimiento 2026-10-12 — relectura y prueba de entrada

El panel ampliado en la sesión de Caprice mostró `FAIL`, 3011 ticks, 18067 IRQ y rango observado 02–16 IRQ entre lecturas de borde VSYNC. Esta transcripción reemplaza la anotación cautelosa anterior de min/max 06/06 para esa relectura; el hash cargado por el proceso no se capturó a tiempo y no se atribuye a la reconstrucción posterior. `OVERRUN 03` y `DRAINED 00` sí quedaron visibles antes de la prueba de entrada, limitados a esa inyección corta. Una pulsación sintética Derecha dejó negra el área del panel y no permitió leer held/pressed/released, por lo que P02 sigue inconclusa. Se reconstruyó después con `make test && make package`; esa build pasa host, mapa y empaquetado, pero no constituye evidencia CPC de esos mismos bytes. Registro: `research/runs/20261012T-T04-current-recheck/results.json`.
