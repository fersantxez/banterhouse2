# Publicar cambios

El repositorio público es [fersantxez/banterhouse2](https://github.com/fersantxez/banterhouse2). Contiene el código, los recursos necesarios para compilar, las pruebas, la documentación y el disco de `release/`.

La web se mantiene en un repositorio separado. Sus archivos de despliegue y los registros privados de las pruebas no se suben aquí.

## Antes de subir

1. Revisa el diff y comprueba que la documentación coincide con el cambio.
2. Ejecuta `make public-check`.
3. Si has cambiado código, ejecuta `make test-host` y las pruebas afectadas. Si cambia el juego CPC, compila y prueba el disco en emulador.
4. Revisa `git diff --cached --check` antes del commit.
5. Después del push, comprueba el resultado de GitHub Actions.

`make public-check` revisa tanto los archivos nuevos como los que Git ya sigue. Busca rutas privadas, repositorios incrustados, archivos demasiado grandes, patrones conocidos de credenciales y enlaces locales rotos. Comprueba también que el disco coincide con `release/manifest.json`. Conviene revisar el diff igualmente: el script sólo detecta los casos que tiene previstos.

## Exportar una copia

Para preparar un ZIP sin el historial de Git ni archivos locales:

```sh
python3 tools/export_public_source.py ../banterhouse2-public-source --archive ../banterhouse2-public-source.zip
```

El destino debe ser nuevo. El script copia los archivos publicables y deja un manifiesto de hashes junto al ZIP. Las dependencias descargadas, ROM, grabaciones y configuración del sitio quedan fuera.

La [revisión inicial](PREPARATION_REPORT.md) recoge las pruebas que se hicieron antes de publicar el repositorio.

## Actualizar el disco

Prueba la imagen final antes de sustituir `release/Devuelto-CPC6128.dsk`. Actualiza su manifiesto y el informe con los resultados correspondientes a ese archivo. Incluye las fuentes, los recursos necesarios para reconstruirlo y los avisos de sus dependencias.

Las licencias y atribuciones están en [COPYING](../../COPYING.md) y [THIRD_PARTY](../../THIRD_PARTY.md). El proyecto no tiene todavía una licencia general para el código y el arte propios.
