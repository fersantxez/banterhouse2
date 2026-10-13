# Colaborar

Para empezar, sigue las [instrucciones de compilación](docs/development/GETTING_STARTED.md). El [índice de archivos](docs/development/REPOSITORY.md) indica dónde está cada parte del juego. Trabajamos para un CPC 6128 clásico de 128 KiB, sin Plus ni expansiones.

## Cambios de código

Explica qué problema resuelve el cambio y cómo lo has probado. Si un archivo tiene un generador, modifica la entrada y vuelve a generarlo.

Antes de enviar una propuesta:

1. Ejecuta `make test-host` y los tests específicos del cambio.
2. Si cambia el juego, compila con `make` y prueba ese disco en emulador.
3. Ejecuta `make public-check` y revisa el diff.

Incluye los comandos usados y cualquier prueba que no hayas podido hacer. Guarda capturas y resultados en `research/runs/`, junto al hash del disco. Cierra los procesos y ventanas que hayas abierto, también cuando una prueba falle. Conserva los resultados anteriores.

No subas ROM, MIDI privados, claves, sesiones personales ni archivos de despliegue. Consulta [los créditos](THIRD_PARTY.md) antes de añadir material de terceros.

## Errores y documentación

Para informar de un error, indica el disco y su hash, el emulador y modelo de CPC, los pasos para reproducirlo y qué ocurrió. Hay una plantilla de incidencia en GitHub.

Escribimos la documentación en español. Usa títulos descriptivos, frases directas y ejemplos concretos cuando ayuden. Evita eslóganes, metáforas para explicar carpetas o comandos y frases de relleno. Si algo es una propuesta o sigue sin probarse, indícalo donde corresponda.
