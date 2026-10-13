# Código y funcionamiento

El juego usa C para las reglas y ensamblador Z80 para las rutinas de hardware, con CPCTelera como biblioteca. El CPC 6128 tiene 128 KiB de RAM, pero el Z80 sólo puede direccionar 64 KiB a la vez; para acceder al resto hay que cambiar los bancos de memoria.

## Bucle principal

[input.c](../../src/platform/input.c) lee el teclado y el joystick. [input_logic.c](../../src/platform/input_logic.c) distingue una pulsación nueva de una tecla que sigue apretada. Esto permite, por ejemplo, pedir que el jugador suelte y vuelva a pulsar para reintentar.

[clock.c](../../src/platform/clock.c) cuenta seis interrupciones del CPC por paso de simulación. El bucle de [main.c](../../src/main.c) consume los pasos pendientes, actualiza el juego y el audio, y dibuja la imagen. El objetivo es ejecutar 50 pasos por segundo; falta comprobar que todo el trabajo cabe siempre en ese tiempo.

## Reglas y física

| Archivo | Responsabilidad |
|---|---|
| [player.c](../../src/core/player.c), [collision.c](../../src/core/collision.c) | Movimiento y contacto con plataformas, con coordenadas de punto fijo |
| [machine.c](../../src/core/machine.c), [projectile.c](../../src/core/projectile.c) | Máquinas, disparos y devoluciones; el número de objetos simultáneos está limitado |
| [flow.c](../../src/game/flow.c) | Vidas, daño y reintento |
| [main.c](../../src/main.c) | Menús, niveles, dibujo e integración de la campaña |

`main.c` todavía concentra bastante lógica. La primera pantalla usa la colisión más reciente; otras pantallas y parte de la demostración conservan el comportamiento anterior. Si cambias la física, prueba las dos variantes.

## Dibujo

Usamos **Mode 0: 160 × 200 píxeles y 16 tintas simultáneas**. Cada byte contiene dos píxeles. Las líneas de la pantalla no ocupan posiciones consecutivas en memoria, algo que las rutinas de dibujo deben tener en cuenta.

Los sprites tienen máscara y variantes para las orientaciones y alineaciones necesarias. El fondo descomprimido se guarda en `&8000–&BFFF` y la pantalla visible en `&C000–&FFFF`. Para mover un objeto se restaura su fondo y se dibuja en la posición nueva. Al cambiar de pantalla o mostrar ciertos paneles se redibuja la imagen completa.

`src/render/render_g.c` contiene un experimento de dibujo separado. La campaña no lo usa.

## Cargas de disco

El DSK contiene `DEVUELTO.BIN` y cuatro archivos, `CH01.BIN`–`CH04.BIN`. Cada uno guarda un fondo comprimido con ZX0, compartido por seis pantallas.

Al cambiar de capítulo, el juego:

1. Pausa la música y prepara el firmware y AMSDOS.
2. Lee el fondo comprimido en `&8000`.
3. Lo descomprime en la pantalla y guarda una copia para restaurar el fondo al mover sprites.
4. Reinicia la cola del reloj y reanuda la música.

El banco 7 conserva el espacio de trabajo del firmware necesario para las siguientes lecturas. El código y las tablas de niveles permanecen en RAM; sólo se sustituye el fondo. Durante la acción no hay lecturas de disco.

Las rutinas están en [disk_assets.s](../../src/platform/disk_assets.s). [attach_chapter_assets.py](../../tools/attach_chapter_assets.py) añade los archivos al DSK y [check_campaign_dsk.py](../../tools/check_campaign_dsk.py) comprueba su contenido y sus cabeceras.

## Memoria

El enlazador coloca el código a partir de `&0100` y los datos desde `&7C50`. La portada usa temporalmente el área que empieza en `&8000`; después se reutiliza para el fondo.

Consulta el archivo `.map` de cada compilación para conocer su ocupación. Los mapas de [ARCHITECTURES.md](../ARCHITECTURES.md) son propuestas anteriores, no el mapa del ejecutable actual.
