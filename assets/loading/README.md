# Portada de arranque

Esta carpeta contiene sólo la portada usada por el juego y sus recursos CPC.

- `banterhouse2-portada-vazquez.png`: ilustración original aprobada, 1024 × 1536, creada con ImageGen.
- `banterhouse2-loading.scr`: bitmap CPC Mode 0, 16.384 bytes.
- `.fwpal` y `.hwpal`: paletas de 16 tintas para firmware y Gate Array.
- `.native.png`: píxeles lógicos nativos, 160 × 200.
- `banterhouse2-loading-preview.png`: visualización 4:3 a 800 × 600, sin añadir detalle al bitmap.
- `loading-manifest.json`: hashes, paleta y parámetros de conversión.

`tools/build_vazquez_loading.py` reduce la ilustración con FFmpeg y la cuantiza a tintas CPC. `tools/build_loading_assets.py` comprime el resultado con ZX0 para el arranque. Después se reutiliza su memoria para el fondo del juego.

Las portadas descartadas, las referencias privadas y el prompt de generación se conservan fuera del repositorio; no hacen falta para compilar. La conversión usa la ilustración completa; no añade otro sprite de Pitu encima.

[Gráficos y música](../../docs/development/ASSETS_AND_AUDIO.md) · [Créditos](../../THIRD_PARTY.md).
