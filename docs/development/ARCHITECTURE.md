# Cómo funciona una partida

[Guía de lectura](../README.md) · [Gráficos y música](ASSETS_AND_AUDIO.md)

El CPC tiene un Z80 y 128 KiB de RAM. Esa memoria no aparece toda a la vez en el espacio de direcciones de 64 KiB del procesador: los bancos deben mapearse. El proyecto usa C para la lógica y ensamblador Z80 para las operaciones cercanas al hardware, con CPCTelera como biblioteca.

## Un paso de juego

La entrada comienza en [input.c](../../src/platform/input.c): lee teclado y joystick. [input_logic.c](../../src/platform/input_logic.c) separa una tecla mantenida de una pulsación nueva. Así saltar, confirmar o reiniciar no dependen de cuántas veces se vuelva a dibujar una tecla apretada.

El [reloj](../../src/platform/clock.c) cuenta seis interrupciones CPC por paso de simulación. El bucle de [main.c](../../src/main.c) consume los pasos pendientes, actualiza el juego, avanza el audio y presenta la imagen. La referencia nominal es 50 pasos por segundo; esto no demuestra que el trabajo de un paso siempre quepa en ese tiempo.

```mermaid
flowchart LR
    A[Teclado y joystick] --> B[Estado de entrada]
    B --> C[Física y reglas]
    C --> D[Música y efectos]
    D --> E[Restaurar y dibujar]
    E --> A
```

## Dónde viven las reglas

- [player.c](../../src/core/player.c) y [collision.c](../../src/core/collision.c) calculan movimiento y contactos con plataformas usando enteros de punto fijo.
- [machine.c](../../src/core/machine.c) y [projectile.c](../../src/core/projectile.c) gestionan emisores, papel y devoluciones mediante conjuntos de tamaño limitado.
- [flow.c](../../src/game/flow.c) gestiona vidas, daño y reintento.
- `main.c` integra menús, niveles, dibujo y las variantes de campaña. Todavía concentra bastante lógica; el proyecto no presenta esa integración como una arquitectura final ya desacoplada.

La arena inicial tiene una ruta de colisión más reciente. Las otras arenas y parte del replay conservan comportamiento anterior. Al modificar física, comprueba ambas rutas.

## Dibujar sin rehacerlo todo

La pantalla está en **Mode 0: 160 × 200 píxeles lógicos y 16 tintas simultáneas**. Un byte representa dos píxeles y las líneas están entrelazadas en la memoria de vídeo. Los sprites incluyen una máscara para preservar el fondo y variantes según orientación y alineación.

El fondo expandido se conserva en `&8000–&BFFF`; la imagen visible vive en `&C000–&FFFF`. El renderer restaura regiones del fondo y dibuja encima objetos y personajes. Al cambiar de arena o mostrar determinados paneles se reconstruye la imagen completa. El módulo `src/render/render_g.c` es un experimento separado, no el renderer que se enlaza automáticamente en la campaña.

## El disquete amplía el contenido

El DSK contiene `DEVUELTO.BIN` y `CH01.BIN`–`CH04.BIN`. El programa y las reglas permanecen residentes. Cada archivo de capítulo aporta un fondo comprimido ZX0, compartido por seis arenas.

Al cambiar de capítulo, el juego pausa la música, prepara el firmware y AMSDOS, lee el recurso comprimido a `&8000`, lo expande hacia la pantalla y guarda el fondo resultante para restauraciones. Después reinicia la cola del reloj y reanuda la música. El banco 7 conserva el espacio de trabajo del firmware que hace falta recuperar en lecturas sucesivas.

Esto es una carga entre capítulos. No es streaming durante el movimiento ni una descarga de todo el motor: las tablas de niveles y el código siguen residentes. El mismo espacio se reutiliza para el siguiente fondo.

Las rutinas están en [disk_assets.s](../../src/platform/disk_assets.s); el empaquetado, en [attach_chapter_assets.py](../../tools/attach_chapter_assets.py). [check_campaign_dsk.py](../../tools/check_campaign_dsk.py) comprueba archivos, cabeceras y correspondencia con el binario.

## El mapa se mide en cada build

El enlace coloca código desde `&0100` y datos desde `&7C50`. La portada ocupa un área temporal desde `&8000`, que después se reutiliza. El mapa `.map` generado y los validadores son la referencia para la ocupación real; los diagramas de [arquitecturas candidatas](../ARCHITECTURES.md) pertenecen a la investigación y no sustituyen ese mapa.
