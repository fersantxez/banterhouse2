# Carpetas y archivos

[Documentación](../README.md) · [Preparar una publicación](PUBLICATION.md)

| Carpeta | Para qué sirve |
|---|---|
| `src/core/` | Física, colisiones, máquinas, proyectiles y estado |
| `src/game/` | Vidas, daño y reintento |
| `src/platform/` | CPC: entrada, reloj, AY, bancos, disco y ZX0 |
| `src/main.c` | Integración de campaña, menús y renderer actual |
| `src/render/` | Experimento de renderer, separado de la campaña |
| `src/generated/` | Datos generados que también usan los tests del ordenador |
| `assets/levels/` | Niveles y geometrías editables |
| `assets/source/canonical/` | Copias de los gráficos originales, con sus hashes |
| `assets/loading/` | Ilustración de portada y su conversión al formato CPC |
| `release/` | Disco publicado y manifiesto con su hash |
| `assets/cpc-studies/` | Estudios gráficos en formato CPC |
| `cfg/` | Configuración, dependencias y mapas de validación |
| `tools/` | Generadores, validadores y herramientas del laboratorio |
| `tests/host/`, `tests/cpc/` | Pruebas para el ordenador y para el CPC emulado |
| `docs/game/` | Historia y guía para jugar |
| `docs/development/` | Tutoriales de construcción, arquitectura y pruebas |
| `docs/implementation/` | Contratos y seguimiento histórico de tareas |
| `research/` | Cálculos de memoria y disco, manifiestos y resultados |
| `LICENSES/` | Avisos de los componentes de terceros incluidos |

## Archivos locales

`build/`, `dist/`, `tmp/`, `.tools/`, `.local/`, `artifacts/` y `research/runs/` están excluidos de Git. Ahí se guardan las compilaciones, dependencias, herramientas locales y resultados de pruebas. Tampoco se suben los MIDI o imágenes de referencia privados, la configuración de acceso ni las claves.

El repositorio de despliegue está físicamente separado del juego, en la carpeta local hermana `banterhouse2-site`. No se incluye como submódulo. Las evidencias y el archivo creativo están también fuera del árbol fuente, en `banterhouse2-archive`.

## Archivos que se editan habitualmente

- Para ajustar movimiento: `src/core/tuning.h`, `player.c` y las pruebas de física.
- Para cambiar máquinas de una arena: su JSON en `assets/levels/`, después `make levels-check`.
- Para componer música: `tools/build_pop_ay.py`, después `make pop-music test-pop-music`.
- Para cambiar el arranque y las cargas: `src/main.c` y `src/platform/disk_assets.s`; además de tests host, exige pruebas reales del emulador.

No edites a mano los bytes generados cuando exista un generador. Cambia su entrada, regenera y revisa la diferencia.
