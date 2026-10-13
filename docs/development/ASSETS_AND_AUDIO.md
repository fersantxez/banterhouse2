# Gráficos y música

## Sprites y fondos

Los sprites de Pitu y Alberto proceden del primer Banterhouse. La compilación usa una copia de los recursos en `assets/source/canonical/`: son 35 archivos, con sus hashes en [manifest.json](../../assets/source/canonical/manifest.json). Así podemos construir el juego sin depender de otra carpeta de trabajo.

[build_runtime_assets.py](../../tools/build_runtime_assets.py) comprueba paletas, tiles, mapas y máscaras, y genera los datos que usa el juego. El origen de los fondos está explicado en [los estudios gráficos](../../assets/cpc-studies/README.md).

Los niveles se editan en `assets/levels/*.json`. [build_levels.py](../../tools/build_levels.py) comprueba la geometría y genera `src/generated/level_data.h`. Varias pantallas comparten geometría y fondo.

## Pantalla de carga

La ilustración está en `assets/loading/`. Se creó con ImageGen. [build_vazquez_loading.py](../../tools/build_vazquez_loading.py) usa FFmpeg para reducirla a 160 × 200 y convertir los colores a tintas CPC. [build_loading_assets.py](../../tools/build_loading_assets.py) comprime el bitmap con ZX0 y genera el ensamblador que lo incluye en el juego.

La vista previa de 800 × 600 muestra cómo queda en una pantalla 4:3. El bitmap CPC sigue teniendo 160 × 200 píxeles. El manifiesto de la carpeta guarda la paleta y los parámetros de conversión.

Las ilustraciones descartadas y las referencias privadas del cómic se guardan fuera del repositorio.

## Música y efectos

[build_pop_ay.py](../../tools/build_pop_ay.py) genera un tema pop/funk de 16 compases. El canal B del AY lleva la melodía; el C alterna bajo y arpegios. El A queda para los efectos de sonido.

Las tablas se escriben en [music.s](../../src/platform/music.s). Cada semicorchea dura seis pasos de simulación: a 50 pasos por segundo serían 125 BPM. Si el juego va más lento, también cambia ese tempo.

Para regenerar la música y ejecutar sus tests:

```sh
make pop-music
make test-pop-music
make test-audio
```

Los tests comprueban las tablas, las pausas y la prioridad de los efectos. También hay que grabar y escuchar la salida del emulador para detectar cortes, saturación o problemas de volumen. La entrega de referencia tiene una grabación PCM documentada en el [informe](../DELIVERY_REPORT.md).

Las pruebas antiguas con MIDI comerciales y su conversor se retiraron; no se usan para generar la música actual. [Créditos](../../THIRD_PARTY.md).
