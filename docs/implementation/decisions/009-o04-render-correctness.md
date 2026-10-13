# O04 — Corrección gráfica del renderer G

**Resultado:** PASS en pruebas host y CPC 6128 emulado. **Fecha:** 2026-10-13.

## Cambio

`render_g_blit_masked` admite ahora anchos de 1 a 9 bytes y alturas de 1 a 32 píxeles. Esto permite probar y dibujar papeles estrechos de 4×6 píxeles además de los sprites de 16 píxeles. La composición de píxeles del host es independiente de la conversión de direcciones CPC. El fixture termina con una firma y un marcador que hacen que Caprice guarde el snapshot en el checkpoint final.

## Pruebas realizadas

- `make test-render`: PASS. Comparación exacta de 232 frames (3.801.088 bytes), bordes, paridad X, ocho fases Y, fondos `00/FF/55/AA` y patrones indexados; papeles 4×6 en `y=5..9`; solapamiento, cambios de pose, eliminación/reutilización, actualización persistente/HUD, pausa, retry y escena nueva.
- `make test-render-snapshot RENDER_SNAPSHOT=research/runs/20261013T-O04-render-snapshot/marker-capture-config/capture.sna`: PASS en Caprice32 4.6.0, CPC 6128 emulado con 128 KiB. El fixture llegó a `stage=55`; el snapshot verificó RAM2 visible byte por byte contra la referencia (16.384 bytes), SP `3F43` dentro de la reserva y canario de pila intacto. SHA-256 VRAM: `ffdcfbc8e1bba18e5dd6de2426f307777b1d02e345fd54cd55706191ac56cb07`.
- `cycles.csv` registra el marcador `done` en PC `07D2` a 284.414.100 ciclos emulados acumulados desde el arranque de Caprice. Este acumulado incluye la carga/espera del sistema y no se interpreta como coste del renderer.
- `make test-gallery-snapshots`, `make test-render-capture`, `make test-render-pageflip-probe`, `make assets-check` y `make smoke-gallery`: PASS. Los cuatro snapshots del Gate Array concuerdan con las paletas; round-trips Mode 0, rechazos negativos, pantallas/paletas enlazadas y perfiles de galería pasan.
- Mapa CPC del fixture actual: código `0100–2B87`, globals hasta `3C5C`, stack de 256 bytes en reserva y backbuffer RAM2; `check_render_map.py` y `check_render_disk.py` PASS.
- La cobertura de alineación/solapamiento y el vídeo de Caprice para R05 constan en `research/runs/20261013T-T06-render/results.json`. R05 es una observación de Caprice emulado y no acredita tearing en hardware.

## Límites

Las pruebas verifican el dominio de coordenadas y tamaños descrito en OP05/OP06 y los escenarios del fixture. No se midió rendimiento ni se probó en CPC físico o Plus. Las pruebas de tearing en hardware y con jugadores siguen pendientes. El usuario confirma por separado que la física ya funciona; esta tarea sólo trata renderizado.
