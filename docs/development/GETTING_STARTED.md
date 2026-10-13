# Compilar el juego

La compilación genera `build/campaign/DEVUELTO.dsk`. El repositorio incluye los gráficos que necesita; no hace falta descargar el primer Banterhouse. Si sólo quieres jugar, puedes usar directamente [el disco publicado](../../release/Devuelto-CPC6128.dsk).

## Requisitos

Necesitas Python 3.9 o posterior, Git, GNU Make, un compilador C/C++, **SDCC 4.6.0** con `sdasz80` y `sdar`, y FFmpeg. Los ejecutables deben estar en `PATH`.

La compilación completa se ha probado en macOS, con las herramientas de línea de comandos de Xcode y Homebrew. Si usas Homebrew, puedes instalar SDCC y FFmpeg con `brew install sdcc ffmpeg`. Comprueba después `sdcc --version`: necesitamos 4.6.0 y la versión de Homebrew puede cambiar.

Las revisiones de CPCTelera y ZX0 están fijadas en [toolchain.lock.json](../../cfg/toolchain.lock.json).

## Compilar

Ejecuta desde la raíz del repositorio:

```sh
make bootstrap
make doctor
make test
make
```

`make bootstrap` descarga CPCTelera y ZX0 en `tmp/` y compila sus herramientas. Necesita conexión a Internet la primera vez. Si encuentra cambios locales en una dependencia, se detiene para no sobrescribirlos.

`make doctor` comprueba las herramientas y sus versiones. `make test` revisa los archivos del repositorio y ejecuta los tests de lógica y formatos en el ordenador. Por último, `make` compila el juego y comprueba que el DSK contiene el programa y los cuatro archivos de capítulo.

## Cargar el resultado

Monta `build/campaign/DEVUELTO.dsk` en un emulador CPC 6128 con 128 KiB. En BASIC escribe:

```basic
RUN"DEVUELTO.BIN"
```

Mantén el disco montado durante la partida. [Controles](../game/PLAYING.md).

## Otros comandos

| Comando | Uso |
|---|---|
| `make campaign-disk` | Compila el disco de campaña; es lo mismo que `make` |
| `make build` | Compila M1, una versión de una sola pantalla para pruebas |
| `make solve-game` | Recalcula la secuencia de entradas de la demostración y actualiza su archivo generado |
| `make test-lab` | Ejecuta pruebas antiguas que requieren emulador y capturas archivadas |
| `make public-check` | Revisa los archivos que se subirán a Git y los enlaces de la documentación |

`make package` exige los archivos de las pruebas de entrega antes de copiar el disco a `dist/`. Para compilar desde un clon nuevo, usa `make`.

## Problemas habituales

- **Falta SDCC o FFmpeg.** Instala la herramienta y comprueba que está en `PATH`.
- **El bootstrap rechaza una dependencia.** Revisa sus cambios en `tmp/`. Para repetir la instalación sin modificarlos, usa otra copia del proyecto.
- **Falta un archivo al cargar el juego.** Comprueba que has montado el DSK de campaña. El BIN suelto y el disco M1 no contienen los cuatro capítulos.
- **No existe `.tools/cap32`.** El lanzador de pruebas necesita una instalación local de Caprice32. Puedes montar el DSK en otro emulador. La configuración de Caprice está en [Pruebas](TESTING.md).

El disco de `release/` se conserva como referencia. Compilar crea otro en `build/`; no sustituye el publicado.
