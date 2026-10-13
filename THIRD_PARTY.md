# Créditos

## El proyecto

Banterhouse 2 — ¡Devuelto! continúa los personajes de [Banterhouse](https://github.com/fersantxez/banterhouse), con nueva dirección arcade. Los sprites de Pitu y Alberto sirven de referencia para el resto del dibujo. El mundo toma referencias del cómic *Creatas y Ejecutas* y de la cultura pop de los ochenta. Los guiños a Prince y otros iconos no implican participación ni aprobación de sus titulares.

Se han usado herramientas de IA para programar, documentar y crear parte de las ilustraciones. Las notas de `assets/loading/` y `assets/cpc-studies/` distinguen la portada y el material nativo CPC. Las exploraciones descartadas se conservan fuera del árbol fuente. Las imágenes originales de referencia del cómic no se incluyen en el conjunto público.

## Componentes técnicos

| Componente | Uso | Procedencia y aviso |
|---|---|---|
| CPCTelera | Biblioteca CPC, funciones de vídeo, entrada y herramientas de construcción | [Fuente](https://github.com/lronaldo/cpctelera), commit fijado en `cfg/toolchain.lock.json`; biblioteca LGPL-3.0-or-later según sus avisos; herramientas con sus propios avisos. El DSK incluye código enlazado; las fuentes se descargan durante bootstrap. Textos originales: [LGPL-3.0](LICENSES/CPCTelera-LGPL-3.0.txt) y [GPL-3.0](LICENSES/CPCTelera-GPL-3.0.txt). |
| ZX0 | Compresión de fondos y portada; decoder Z80 adaptado al ensamblador SDAS | [Fuente](https://github.com/einar-saukas/ZX0), Einar Saukas; decoder acreditado a Einar Saukas y Urusergi. [BSD de tres cláusulas](LICENSES/ZX0-BSD-3-Clause.txt). |
| SDCC / SDAS / SDAR | Compilar, ensamblar y enlazar | [Proyecto SDCC](https://sdcc.sourceforge.net/); herramientas externas, no redistribuidas aquí. |
| FFmpeg | Conversión de portada a RGB reducido antes de cuantizar a tintas CPC | [Proyecto FFmpeg](https://ffmpeg.org/); herramienta externa, no redistribuida aquí. |
| Caprice32 | Laboratorio de ejecución y capturas | [Fuente](https://github.com/ColinPitrat/caprice32); ejecutable y ROM quedan fuera del repositorio. |
| Javascript 1984 | Emulador de la web de desarrollo y contraste de campaña | [Fuente](https://github.com/salvogendut/1984); pertenece al repositorio independiente del sitio, excluido de esta exportación. |

`src/platform/zx0.s` conserva la atribución del decoder. El adaptador de llamada sigue el ABI `--sdcccall 0`. Los clones de dependencias conservan sus archivos de licencia originales.

## Música y arte

`tools/build_pop_ay.py` genera la música compuesta para este proyecto. Los MIDI comerciales usados en exploraciones antiguas están excluidos y no son una dependencia de la compilación actual.

Los sprites heredados y las referencias visuales se documentan en los manifiestos canónicos y en [GAME_REFERENCES](docs/GAME_REFERENCES.md). No se ha añadido una licencia global para el arte ni para el código propio; consulta [COPYING](COPYING.md).
