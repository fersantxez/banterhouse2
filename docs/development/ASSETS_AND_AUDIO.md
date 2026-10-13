# Del dibujo y la melodía a los bytes

[Guía de lectura](../README.md) · [Pruebas](TESTING.md)

## Dos clases de imagen

La ilustración de `assets/loading/` es la entrada de la portada. Las exploraciones descartadas se conservan fuera del repositorio. Los recursos de `assets/source/canonical/` son entradas nativas CPC con dimensiones, paletas y hashes conocidos.

La conversión de una imagen al formato correcto sólo acredita que cabe en ese formato. La velocidad al dibujarla debe probarse en el runtime.

## Personajes y escenarios

Pitu y Alberto proceden de las bases gráficas del primer Banterhouse. Los scripts de investigación pueden consultar ese proyecto en lectura, pero una compilación normal usa los 35 archivos congelados en [el manifiesto canónico](../../assets/source/canonical/manifest.json).

[build_runtime_assets.py](../../tools/build_runtime_assets.py) valida paletas, tiles, mapas y máscaras; genera variantes de sprites y los recursos del runtime. Los escenarios estáticos conservan su documentación en [estudios CPC](../../assets/cpc-studies/README.md).

Los niveles se editan en `assets/levels/*.json`. [build_levels.py](../../tools/build_levels.py) comprueba su geometría y genera `src/generated/level_data.h`. La campaña actual comparte geometría y ambientes: editar una propuesta narrativa no cambia automáticamente sus arenas.

## La portada

La ilustración aprobada está en `assets/loading/`. [build_vazquez_loading.py](../../tools/build_vazquez_loading.py) usa FFmpeg para reducirla y cuantizarla a tintas CPC. [build_loading_assets.py](../../tools/build_loading_assets.py) comprime el bitmap con ZX0 y lo convierte en ensamblador.

La rejilla es de 160 × 200. La previsualización a 800 × 600 representa la proporción de un monitor 4:3; no añade píxeles al CPC. La ilustración fue creada con asistencia de generación de imágenes. Su manifiesto y sus notas conservan la procedencia, sin distribuir referencias privadas del cómic.

## Tres canales AY

El generador [build_pop_ay.py](../../tools/build_pop_ay.py) define un motivo pop/funk de 16 compases para el proyecto. La melodía usa el canal B. El C alterna bajo y arpegios; el A queda disponible para efectos prioritarios.

El resultado es [music.s](../../src/platform/music.s). El pulso de diseño es de seis pasos de simulación por semicorchea: equivale a 125 BPM **si** la simulación mantiene 50 Hz. Esa relación aritmética no mide la reproducción real.

```sh
make pop-music
make test-pop-music
make test-audio
```

Los MIDI privados empleados en exploraciones anteriores no forman parte del repositorio ni de este pipeline. La antigua herramienta de conversión MIDI se retiró del árbol fuente junto con las exploraciones que ya no se usan.

Las pruebas de tablas y prioridad de efectos no sustituyen la captura de sonido. La entrega anterior tiene una captura PCM documentada; una build nueva debe repetir las pruebas de runtime y la escucha. [Atribuciones](../../THIRD_PARTY.md).
