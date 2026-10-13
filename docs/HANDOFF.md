# Continuar el trabajo

13 de octubre de 2026. Cierre de la limpieza, publicación y revisión de documentación.

## Estado

El repositorio público es [fersantxez/banterhouse2](https://github.com/fersantxez/banterhouse2), rama `main`. La publicación inicial está en `300c78b`; la revisión de redacción, en `83b64a5`. Esta última cambió 53 archivos Markdown, sin modificar el código ni el disco.

El juego sigue siendo el prototipo de 24 pantallas descrito en [Estado](STATUS.md). El disco está en [release/Devuelto-CPC6128.dsk](../release/Devuelto-CPC6128.dsk), con SHA-256 `034efbab917c1ec318cf25312aa7842d4ff74a4c306a3f48f6890f4995dc1f8c`. En BASIC se arranca con `RUN"DEVUELTO.BIN"`; debe permanecer montado para cargar los capítulos.

## Comprobaciones

- Se reconstruyó desde una copia limpia con `make bootstrap`, `make doctor`, `make test` y `make`. El DSK coincidió byte por byte con el publicado.
- La revisión documental pasó `make public-check`, `tools/check_implementation_plan.py`, la comprobación de enlaces a secciones y `git diff --check`.
- [GitHub Actions del commit 83b64a5](https://github.com/fersantxez/banterhouse2/actions/runs/38472332144) terminó correctamente.
- Se comprobaron las descargas públicas de documentación y disco. Las partidas anteriores están documentadas en el [informe de entrega](DELIVERY_REPORT.md); no se repitieron por el cambio de redacción.

## Carpetas locales

La web está en `../banterhouse2-site`, con su propio repositorio y despliegue. Las evidencias y referencias retiradas están en `../banterhouse2-archive/20261013-cleanup`. No deben copiarse al repositorio público del juego.

Se eliminaron las compilaciones, dependencias descargadas, exportaciones duplicadas y la copia usada para verificar la reconstrucción. Para volver a compilar, sigue [Compilar el juego](development/GETTING_STARTED.md). El primer Banterhouse, en `../banterhouse`, sigue siendo de sólo lectura.

## Pendiente

- Completar las pruebas y mediciones de la web sobre su versión vigente. Se editó en otro chat; consulta el repositorio del sitio antes de preparar una prueba.
- Probar en CPC físico y con jugadores.
- Terminar los personajes, encuentros y escenas de la campaña narrativa.
- Elegir una licencia general para el código y el arte propios, si se quiere conceder permisos de reutilización. Los avisos de terceros ya están incluidos.

Antes de implementar, lee `AGENTS.md`, [Estado](STATUS.md) y [el índice de tareas](implementation/README.md). Los planes antiguos contienen resultados de versiones distintas: no marques una tarea como terminada sólo porque exista un archivo con ese nombre.

La documentación debe seguir en español directo, con títulos descriptivos y sin eslóganes ni frases de relleno. Conserva los comandos, las fuentes, las cifras y las limitaciones de las pruebas.
