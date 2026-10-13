# Revisión para publicación del código

Fecha: 13 de octubre de 2026. Esta revisión prepara el código y su disco validado; no publica un repositorio de GitHub ni cambia la web.

## Limpieza

Se retiraron de la raíz 85 capturas, snapshots y archivos auxiliares. Sus bytes originales y un manifiesto SHA-256 se trasladaron al archivo externo `banterhouse2-archive/20261013-cleanup/repository-preparation/`. Las evidencias históricas de las sesiones se trasladaron al mismo archivo externo. No quedan esas carpetas dentro del repositorio.

Se eliminaron físicamente las dependencias descargadas, compilaciones y exportaciones duplicadas. El sitio web se trasladó a `banterhouse2-site`; los materiales privados y las pruebas necesarias, al archivo externo. Se retiraron portadas descartadas y herramientas obsoletas. El conjunto público contiene ahora un único DSK validado en `release/` y la portada que realmente se usa en `assets/loading/`. Se sustituyeron rutas personales por referencias relativas o enlaces al repositorio del primer Banterhouse. Los documentos históricos mantienen su fecha, alcance y un acceso al estado actual.

## Pruebas ejecutadas en una exportación limpia

| Comprobación | Resultado observado |
|---|---|
| Bootstrap con clones nuevos de CPCTelera y ZX0 | PASS; commits fijados y herramientas compiladas localmente |
| `make doctor` | PASS con SDCC 4.6.0 y las dependencias esperadas |
| `make test` | PASS; auditoría pública y lógica host sin emulador, ROM ni archivo privado de sesiones |
| `make` | PASS; ejecutable de 38.150 bytes y cuatro archivos AMSDOS de capítulo |
| Comparación del disco reconstruido | SHA-256 idéntico al DSK de referencia |
| Validación de planes | PASS; dependencias y contratos documentales consistentes |
| Auditoría pública y negativos del auditor | PASS; enlaces locales y exclusiones verificadas |

SHA-256 del disco reconstruido: `034efbab917c1ec318cf25312aa7842d4ff74a4c306a3f48f6890f4995dc1f8c`.

La reconstrucción se hizo con Python 3.9.6, SDCC 4.6.0, las herramientas C/C++ y FFmpeg disponibles en el Mac de desarrollo. Los clones nuevos se crearon dentro de la copia exportada, sin reutilizar los binarios de dependencias del árbol original. CPCTelera e iDSK emiten advertencias de sus fuentes antiguas; la construcción terminó correctamente. SDCC advierte sobre el ABI no predeterminado: el proyecto lo fija deliberadamente a `--sdcccall 0` y el resultado reconstruido coincide con el disco de referencia.

Los logs de preparación y el resultado de la reconstrucción posterior a la limpieza están en el archivo externo; no se publican las rutas personales de ese entorno. El ZIP de fuente y su manifiesto se generan con `tools/export_public_source.py`.

## Límites

Esta revisión no vuelve a jugar la campaña, no mide rendimiento y no cambia el estado de las pruebas físicas o web. La identidad del DSK permite relacionar la reconstrucción con la [entrega histórica](../DELIVERY_REPORT.md); no añade una nueva sesión de emulador. El workflow de GitHub está preparado, pero todavía no se ha ejecutado en GitHub.

La revisión automática busca patrones conocidos de credenciales y rutas privadas; no se presenta como garantía universal de ausencia de cualquier dato sensible. Las condiciones de distribución del código propio siguen recogidas en [COPYING](../../COPYING.md), sin atribuirle una licencia general nueva.

[Volver al procedimiento de publicación](PUBLICATION.md) · [Guía de lectura](../README.md)
