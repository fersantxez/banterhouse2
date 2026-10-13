# Cómo sabemos qué funciona

[Guía de lectura](../README.md) · [Mapa del repositorio](REPOSITORY.md)

Una prueba de lógica en el ordenador, una partida en emulador y una prueba en CPC físico contestan preguntas distintas. Mantener esa separación evita entregar un disco sólo porque su código compila.

## 1. Pruebas que puede repetir un clon limpio

```sh
make public-check
make test-host
make campaign-disk
```

La primera revisa qué archivos entrarían en Git y comprueba enlaces locales. La segunda usa C, Python y sanitizadores para física, colisiones, máquinas, audio, niveles, entrada y supervisión de procesos. No necesita ROM ni abre un emulador. La tercera requiere el bootstrap y produce un disco cuya estructura se inspecciona contra el BIN y el mapa reales.

La CI de GitHub ejecutará las dos primeras al subir el repositorio. Incluir el workflow no significa que ya se haya ejecutado en GitHub.

## 2. Pruebas de la máquina emulada

Abre la build exacta en CPC 6128/128 KiB. Comprueba arranque desde frío, menú, controles, muerte, reintento, pausa, salida de audio, transición de capítulo y final de campaña. El modo D permite repetir el recorrido determinista; prueba también controles reales fuera del replay.

El laboratorio opcional espera Caprice32 en `.tools/cap32`, su perfil en `.tools/cap32.cfg` y ROM en `.tools/rom/`. Esos archivos se preparan localmente; no se distribuyen en Git. También puedes indicar rutas externas con `python3 tools/run_game.py --emulator RUTA_CAPRICE --config-template PERFIL_CFG`. `python3 tools/doctor.py --emulator` comprueba su presencia.

[run_game.py](../../tools/run_game.py) y [run_session.py](../../tools/run_session.py) gestionan una sesión exclusiva y guardan evidencia bajo `research/runs/`. Cada prueba tiene que cerrar su propio grupo de procesos incluso si falla o agota el tiempo. Nunca se cierran procesos ajenos por nombre.

`make test-lab` incluye experimentos y verificaciones históricas que esperan capturas específicas. No es la ruta de bienvenida de un clon nuevo. `validate_release_evidence.py` exige el archivo de evidencias enumerado en `research/release-validation.json`; si falta, debe fallar. No se rellena una aprobación con datos ficticios.

## 3. Rendimiento y audio

Registra la build por SHA-256 y las versiones del emulador y del host. Distingue pasos de simulación, cuadros renderizados y velocidad del emulador. La instrumentación de la web mide trabajo y cadencia del navegador; no certifica el tiempo de CPU del CPC físico.

La captura PCM verifica señal, silencios y saturación. La escucha comprueba equilibrio, fatiga y calidad musical. Se necesitan ambas para afirmar que la música funciona bien.

## 4. Pruebas que siguen siendo externas

La compatibilidad física, variantes de CRTC y disquetera requieren esos equipos. La diversión y la claridad de los controles requieren jugar y observar jugadores. [Plantilla de playtest](../PLAYTEST.md).

## Después de un cambio

Ejecuta las pruebas relacionadas con él, conserva los fallos como evidencia y vuelve a comprobar la build final. Si el DSK cambia, los resultados históricos ligados a otro hash no aprueban automáticamente el nuevo. La [entrega registrada](../DELIVERY_REPORT.md) sirve como referencia, no como permiso para saltarse ese paso.
