# Pruebas de investigación

> Archivo de las primeras pruebas. Las fechas indican a qué versión corresponden. El [estado actual](../docs/STATUS.md) recoge las pruebas posteriores. Los registros completos de `runs/` se conservan en `banterhouse2-archive`, fuera del repositorio público.

## Plan de ejecución v2 · 11 de octubre de 2026

El [plan de optimización](../docs/implementation/OPTIMIZATION_PLAN.md) amplía el seguimiento a 52 tareas. Su comprobación documental se reproduce con `python3 tools/check_implementation_plan.py`; [resultado v2](results/implementation-plan-v2-check.json). Comprueba IDs, fichas, dependencias sin ciclos, enlaces locales, revisiones con jugadores y pruebas de hardware y negativos del validador. Comprueba los documentos; no ejecuta el juego. `implementation-plan-check.json` se conserva como informe histórico de la versión 1.

Actualización gráfica del 11 de octubre: [cuatro estudios CPC nativos](../assets/cpc-studies/README.md) y su [manifiesto de pruebas](../assets/cpc-studies/manifest.json). Incluyen exportación VRAM, comprobación de paletas, reconstrucción desde tiles y compresión opcional. Son verificaciones host, sin ejecución del futuro juego en CPC o emulador.

Fecha de ejecución: 2026-10-10. Todas son pruebas **host en el Mac**; no se han ejecutado nuevos benchmarks en un CPC ni en emulador. No hay resultados nuevos de FPS, scanout, pila Z80, audio/FDC simultáneo o carga física.

## Resultados guardados

- [host-probe.json](results/host-probe.json): hashes de entradas locales, versiones, cuatro censos de sprites, 12 compresiones/round-trips y cálculos.
- [upstream-metadata.json](results/upstream-metadata.json): metadatos públicos de GitHub, SHA y fecha de commit consultados. `NOASSERTION`/null no equivale a «sin derechos»; las licencias que se leyeron se explican en la matriz.
- [memory-budgets.json](memory-budgets.json): reservas propuestas de los tres mapas, no ocupación medida de un binario.
- [budget-check.json](results/budget-check.json): comprobación de sumas, intervalos y cuotas temporales de esos diseños.

Herramientas ejecutadas: Python estándar, Git, Clang/make, compresores y descompresores C oficiales ZX0/LZSA. Se invocó `sdcc --version` (4.6.0 #16555), sin compilar el juego. Se usaron web, API GitHub y lectura local para fuentes. Para el compendio ACCC se usó `curl` y `pypdf` del runtime local Codex; 296 páginas detectadas, versión 1.11/agosto 2026. No se redistribuye ese PDF en los entregables.

## Repetir el análisis sin descargar nada

Desde `.`:

```sh
python3 tools/research_probe.py --original ../banterhouse
python3 tools/check_research_budgets.py
```

El primero crea `research/results/asset-probe.json`, sin sustituir el registro de compresión. Sólo lee Banterhouse; los temporales y salidas quedan aquí. Requiere los recursos generados que ya existían en el proyecto original. Si faltan, la prueba falla: no ejecuta automáticamente el build original. Los resultados sólo son comparables si coinciden los hashes de las entradas.

## Repetir las pruebas de compresión

Requiere red, Git, Make y Clang. No instalar nada global. Los comandos de clonación son para una carpeta aún inexistente; si ya existe, comprobar el SHA antes de reutilizarla.

```sh
mkdir -p tmp/research-tools
git clone https://github.com/einar-saukas/ZX0.git tmp/research-tools/ZX0
git -C tmp/research-tools/ZX0 checkout --detach ecde3a2ae05061fe06469ed46df81a33b7de7d86
git clone https://github.com/emmanuel-marty/lzsa.git tmp/research-tools/lzsa
git -C tmp/research-tools/lzsa checkout --detach 15ee2dfe118eeb8f7683ca44f64821c3a61ca1e5
make -C tmp/research-tools/ZX0/src CC=clang CFLAGS=-O2 EXTENSION=
make -C tmp/research-tools/lzsa -j2
python3 tools/research_probe.py --compress --original ../banterhouse
```

La ejecución inicial clonó shallow HEAD; los SHA obtenidos son exactamente los fijados arriba. Salida ZX0 por defecto (formato actual forward) y LZSA `-r -f 1`/`-r -f 2`. Cada salida se descomprime con el decoder host correspondiente y se compara byte a byte. El JSON guarda los comandos efectivos y hashes. Los binarios de terceros permanecen en `tmp/` ignorado, con sus licencias en los clones.

Resultados en bytes: sprites 2.048 → ZX0 384 / LZSA1 469 / LZSA2 412; carga 16.384 → 6.292 / 7.328 / 6.516; fixture 16.384 → 2.337 / 2.708 / 2.457; salas concatenadas 711 → 474 / 582 / 530. Los seis archivos de sala se concatenan en orden de nombre, sin índice adicional. Esto favorece la compresión cruzada y **no** es una comparación de seis bloques de acceso aleatorio.

## Alcance de la prueba de sprites

Extrae sólo las cuatro matrices fuente activas de 512 B de `src/graphics.c`, excluyendo `#if 0`. Comprueba formato de máscaras M0 y que los bits de píxel no invadan los preservados. Clasifica cada par máscara/píxel y compara la operación genérica con la selección transparente/opaca/parcial para los 256 valores posibles de fondo.

Resultado: 380 posiciones transparentes, 517 opacas, 127 parciales; 262.144 casos de equivalencia. Es una comprobación del **modelo de operación por byte**, no un test de un compilador Z80, del clipping, del direccionamiento CPC o de un renderer completo. El posible ahorro de lecturas/escrituras no es una medición de milisegundos.

Cálculo de variantes: `8 poses × 2 direcciones × (8+9 bytes de ancho) × 32 líneas × 2 (máscara/píxel)` = **17.408 B**. El noveno byte sólo corresponde a la variante desplazada; no se ha creado arte de ocho poses. Cuatro save-under de ancho máximo: 1.152 B, sin metadatos.

## Resultados negativos y no ejecutados

- Ruta heredada `.tools/cpctelera` no presente en Banterhouse en la inspección; no se rehízo su toolchain ni se ejecutó make sobre el original.
- `pdftotext` no estaba en PATH; se utilizó `pypdf` disponible en el runtime local. El enlace ACCC 1.8 devolvió HTML y se sustituyó por el PDF 1.11 enlazado por el autor.
- No se lanzó ACE-DL, WinAPE, Caprice32, 8BP o TRSE ni se comparó código generado por compiladores.
- No se ensamblaron decoders Z80 ni sprites compilados. No hay medición de pila ni de tiempos CPC de descompresión.
- No se dispone de CPC físico ni disquetera accesible en esta sesión. Compatibilidad CRTC y fiabilidad de disco físico quedan expresamente pendientes.
- No se descargó ni compiló el conjunto Phactory/Phortem; se verificó la publicación por el autor y su ruta de fuente. Las atribuciones a demos se limitan a lo que explican sus autores.

Falta repetir la descompresión con el código Z80, usando las mismas entradas, guardas de memoria y un contador de tiempo CPC.

## Planificación de campaña · 11 de octubre de 2026

[Cuotas de almacenamiento](campaign-storage-budget.json) y [comprobación aritmética](results/campaign-budget-check.json), reproducibles con:

```sh
python3 tools/check_campaign_budget.py
```

Comprueba sumas por cara, reservas físicas de la candidata A, límite de staging y ejemplos de tiles/sprites. Resultado: 178 KiB por cara después del directorio, con 24 KiB sin asignar en A y 20 KiB en B; candidato A suma 128 KiB. Estas son cuotas de diseño: no se ha empaquetado el arte de la campaña ni medido una carga CPC. La historia y el uso de paquetes se describen en [estructura](../docs/STORY_STRUCTURE.md) y [plan de disco](../docs/DISK_CONTENT_PLAN.md).
