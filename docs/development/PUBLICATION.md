# Preparar el repositorio público

[Guía de lectura](../README.md) · [Mapa de carpetas](REPOSITORY.md)

El repositorio público contiene el código, sus entradas necesarias, pruebas, documentación y un único DSK validado en `release/`. Las sesiones privadas de desarrollo y el repositorio de despliegue del sitio se conservan localmente.

La [revisión realizada](PREPARATION_REPORT.md) documenta la reconstrucción limpia y sus resultados.

## Revisión reproducible

```sh
make public-check
make test-host
python3 tools/export_public_source.py ../banterhouse2-public-source --archive ../banterhouse2-public-source.zip
```

El exportador exige un destino nuevo, copia sólo los archivos publicables y produce un manifiesto con hashes al lado del ZIP. No copia `.git`, herramientas descargadas, ROM, registros de sesiones, MIDI privados ni configuración del sitio. Tampoco crea un repositorio remoto.

El validador comprueba el conjunto candidato de Git, incluidos los archivos ya rastreados: ignorar un archivo no basta si ya entró en el índice. Rechaza rutas privadas, repositorios incrustados, archivos demasiado grandes, patrones comunes de credenciales y enlaces locales rotos. El único DSK permitido debe coincidir con `release/manifest.json`. No reemplaza una revisión humana de contenido ni prueba los enlaces externos en Internet.

## Antes del primer envío

1. Revisa el contenido candidato y [las atribuciones](../../THIRD_PARTY.md).
2. Comprueba que el README describe el estado real y que no enlaza discos inexistentes como si fueran descargas públicas.
3. Prueba el bootstrap, los tests host y el DSK desde la exportación limpia.
4. Revisa `git diff --cached --stat` y `git diff --cached --check` antes del commit.
5. Crea el repositorio de GitHub cuando decidas publicarlo y envía el código revisado. Este procedimiento no cambia el acceso de la web.

## Licencia y material de terceros

[La nota de distribución](../../COPYING.md) distingue el código del proyecto y los componentes con licencia propia. La preparación no asigna automáticamente una licencia general al trabajo del autor. El decoder ZX0 conserva su aviso BSD. CPCTelera se descarga desde su fuente y no se copia como binario al repositorio.

Una eventual publicación de discos debe llevar también sus atribuciones y los materiales de construcción correspondientes. El repositorio fuente y un paquete de juego para usuarios son entregables diferentes: para el segundo sigue la validación de release, incluida la prueba de la imagen final.
