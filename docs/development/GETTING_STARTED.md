# Del código a un disquete

[Guía de lectura](../README.md) · [Cómo funciona](ARCHITECTURE.md)

El resultado de la compilación es un **DSK**, una imagen de disquete que puedes montar en un emulador CPC. No necesitas tener instalado el primer Banterhouse: las entradas gráficas necesarias están congeladas en este repositorio.

## 1. Prepara las herramientas del ordenador

Necesitas Python 3.9 o posterior, Git, GNU Make, un compilador C/C++, **SDCC 4.6.0** con `sdasz80` y `sdar`, y FFmpeg. Deben estar en `PATH`. FFmpeg convierte la portada; no reproduce el juego.

En el Mac de desarrollo se usan las herramientas de línea de comandos de Xcode y Homebrew. Si ya tienes Homebrew, `brew install sdcc ffmpeg` instala esas dos dependencias; comprueba `sdcc --version`, porque el proyecto fija 4.6.0 y el paquete disponible puede cambiar. No se incluye un instalador global automático.

La versión de referencia y los commits de las dependencias figuran en [toolchain.lock.json](../../cfg/toolchain.lock.json). El flujo se valida en macOS; no se afirma que todos los sistemas estén probados.

## 2. Desde la raíz del repositorio

```sh
make bootstrap
make doctor
make test
make
```

`bootstrap` descarga los commits fijados de CPCTelera y ZX0 dentro de `tmp/` y compila sus herramientas. No instala nada globalmente ni sustituye un checkout con cambios locales. Necesita red la primera vez. Las licencias permanecen en los clones.

`doctor` comprueba herramientas y versiones. `test` audita los archivos y prueba la lógica C y los formatos usando el ordenador. `make` genera la campaña CPC y verifica el contenido del disco.

## 3. Abre el resultado

Monta `build/campaign/DEVUELTO.dsk` en un emulador CPC 6128 con 128 KiB. En BASIC ejecuta:

```basic
RUN"DEVUELTO.BIN"
```

Mantén el DSK montado para las cargas de capítulo. [Controles y consejos](../game/PLAYING.md).

## Qué crea cada comando

| Comando | Resultado o alcance |
|---|---|
| `make test` | Auditoría y tests host sin emulador, ROM ni evidencias privadas |
| `make` | Compila la campaña completa; equivale a `make campaign-disk` |
| `make campaign-disk` | `build/campaign/DEVUELTO.dsk`, campaña con cargas de disco |
| `make build` | Variante M1 de una arena para diagnóstico; no es el DSK completo |
| `make solve-game` | Recalcula el replay desde el simulador host; modifica un archivo generado |
| `make test-lab` | Suite histórica amplia; necesita herramientas de laboratorio y capturas archivadas |
| `make public-check` | Audita archivos publicables y enlaces locales |

No uses `make package` como atajo de compilación: exige el archivo de evidencias de entrega y lo verifica antes de copiar un disco a `dist/`.

## Errores habituales

**Falta SDCC o FFmpeg:** instala la dependencia y comprueba que se encuentra en `PATH`.

**El bootstrap rechaza un checkout:** revisa los cambios de esa dependencia en `tmp/`. El script se detiene para no descartarlos. Usa una copia nueva del proyecto para repetir desde cero.

**El disco pide otro archivo:** confirma que es el DSK de campaña. Un BIN aislado o el disco M1 no reemplaza los cuatro recursos AMSDOS.

**No existe `.tools/cap32`:** sólo afecta al lanzador supervisado del laboratorio. Para jugar puedes montar el DSK incluido en `release/` en tu propio emulador. Las pruebas CPC y su configuración se explican en [Pruebas](TESTING.md).

El disco incluido permite jugar sin descargar compiladores. Su [manifiesto](../../release/manifest.json) identifica los bytes de la entrega. Una compilación nueva crea una candidata en `build/` y nunca sustituye automáticamente ese disco.
