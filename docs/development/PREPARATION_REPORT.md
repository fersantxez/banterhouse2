# Revisión del repositorio

13 de octubre de 2026. Registro de la limpieza y las pruebas anteriores a la primera publicación.

## Archivos retirados

Se trasladaron 85 capturas, snapshots y archivos auxiliares a `banterhouse2-archive/20261013-cleanup/repository-preparation/`, junto a un manifiesto SHA-256. Los registros de pruebas, las referencias privadas y las portadas descartadas se conservaron en ese archivo externo.

Se borraron dependencias descargadas, compilaciones y exportaciones duplicadas. La web pasó a la carpeta hermana `banterhouse2-site`. En el repositorio quedaron el código, sus recursos, la documentación y el disco de `release/`. También se corrigieron rutas personales y enlaces.

## Reconstrucción desde cero

Se exportó una copia del repositorio y se descargaron de nuevo las dependencias. La prueba se hizo en macOS, con Python 3.9.6, SDCC 4.6.0, herramientas C/C++ y FFmpeg.

| Comprobación | Resultado |
|---|---|
| Bootstrap de CPCTelera y ZX0 | Correcto, con las revisiones fijadas |
| `make doctor` | Herramientas y versiones correctas |
| `make test` | Auditoría y tests de lógica correctos, sin emulador ni archivos privados |
| `make` | Ejecutable de 38.150 bytes y cuatro archivos de capítulo |
| Disco reconstruido | Idéntico byte por byte al de referencia |
| Planes | Dependencias y requisitos documentales consistentes |
| Auditor del repositorio | Enlaces y exclusiones correctos; rechazó los casos de prueba inválidos |

SHA-256 del DSK: `034efbab917c1ec318cf25312aa7842d4ff74a4c306a3f48f6890f4995dc1f8c`.

CPCTelera e iDSK produjeron advertencias al compilar sus fuentes antiguas. SDCC avisó del uso de `--sdcccall 0`, que el proyecto necesita para su ABI. La compilación terminó y el disco coincidió con el de referencia.

Se guardaron los resultados en el archivo externo y se borró la copia temporal usada para compilar. Esta revisión comprobó la reconstrucción; no repitió las partidas del [informe de entrega](../DELIVERY_REPORT.md) ni las pruebas pendientes de hardware y web.

## Publicación

El repositorio se publicó el mismo día en [GitHub](https://github.com/fersantxez/banterhouse2), con el commit `300c78b`. Se comprobaron las descargas públicas del README, el índice de documentación y el DSK. El disco descargado conservaba el mismo hash.

La [primera ejecución de GitHub Actions](https://github.com/fersantxez/banterhouse2/actions/runs/38470367753) pasó la auditoría y los tests de lógica en Ubuntu.
