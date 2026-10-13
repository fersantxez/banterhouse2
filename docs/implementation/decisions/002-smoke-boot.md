# 002 — Arranque mínimo, contrato de enlace y mapa CPC

Estado: T02 completada para el perfil smoke aislado y el mapa enlazado actual.

El perfil `tests/cpc/smoke/` construye `build/smoke/SMOKE.dsk` sin reutilizar el `main.c` ni el DSK del juego. El programa entra desde AMSDOS a `&0100`, desactiva firmware, traslada la pila a `&7FF0`, configura Mode 0 y permanece en VSYNC. La marca pequeña de pantalla aparece sólo cuando la llamada C→ASM devuelve `&7D3C` para `&1234 XOR &6F08` y la prueba de canario deja al menos 256 bytes contiguos libres al fondo de la reserva de pila.

`cfg/memory.json` define código `&0100–&77FF`, globales `&7800–&7BFF`, pila reservada `&7CF0–&7FEF` (768 bytes), guardia inferior de 256 bytes, fondo limpio `&8000–&BFFF` y pantalla Mode 0 `&C000–&FFFF`. El verificador consume símbolos de SDCC del mapa real, valida las páginas de vídeo y el bootstrap, y rechaza mapas sintéticos inválidos. Para el smoke, el código ocupa `&0100–&02E2` y los datos residentes `&7800–&7801`; el mapa del juego ocupa código hasta `&4F36` y globales hasta `&786D`.

## Evidencia ejecutada

- `make smoke-boot`: binario de 483 bytes, DSK catálogo legible y carga a `&0100`; mapa smoke aceptado; los negativos de overflow de código, fuga de datos, bootstrap fuera del código y bootstrap que pisa datos son rechazados.
- Caprice32 4.6.0, modelo CPC 6128 y 128 KiB: marca del smoke visible después del autocmd; eso verifica en esta ejecución el valor C→ASM y el umbral de 256 bytes de canario. No mide el máximo de todos los caminos futuros ni de una ISR.
- `make smoke-resets`: diez boots fríos independientes con el mismo DSK y autocmd; cada proceso de Caprice permaneció vivo durante 1,5 s antes de cerrarse. La marca se inspeccionó visualmente en una ejecución, no en las diez.
- `make repro`: dos builds desde directorios temporales vacíos e independientes produjeron SHA-256 idéntico: BIN `f854ee751be606ae021beba9ad950131104e81c4649ade72974c9da7497b3990`; DSK `10f74522d4eb504f3127272c7e31a86c6a98a572e53ac7d4c7cd14b8a0bdadfd`.
- `make package` y `make check-map`: el mapa del candidato jugable respeta las reservas actuales; el paquete DSK candidato sigue generándose por separado.

## Límites

Los diez arranques son procesos nuevos de Caprice con el autocmd del perfil smoke, no diez reinicios observados individualmente en una CPC física. El canario cubre el camino de arranque smoke ejecutado, no sustituye medir el peor camino con ISR y juego integrado. No certifica CPC6128 físico, audio audible, latencia, FPS objetivo ni diversión. La prueba de escucha AY sigue limitada por el error de `AudioQueueStart` de CoreAudio de este host.
