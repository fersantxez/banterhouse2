# Optimización CPC: guía de ejecución para 6.1 Luna

Versión 2 · 11 de octubre de 2026. Plan de trabajo, **no resultados de rendimiento**.

Objetivo: reducir trabajo del Z80, aprovechar la RAM del CPC 6128 clásico y mantener el control, los píxeles y el audio del juego. Demostrar cada ganancia con una comparación equivalente. No hay obligación de convertir todo a ensamblador ni una promesa de 50 FPS.

Este documento amplía [el plan principal](../IMPLEMENTATION_PLAN.md). Las fichas están en [OPTIMIZATION_TASKS.md](OPTIMIZATION_TASKS.md), los ensayos en [OPTIMIZATION_TESTS.md](OPTIMIZATION_TESTS.md) y **el único estado de ejecución** en [STATUS.json](STATUS.json). Los IDs O00–O16 son tareas; los IDs OP01–OP20 son pruebas. No confundirlos con las pruebas O01–O10 de disco del plan original.

## 1. Punto de partida observado

Inspección de archivos, sin ejecutar el juego ni certificar el DSK existente:

| Existe | Observación y consecuencia |
|---|---|
| `src/main.c` | Prototipo monolítico C con movimiento, máquinas, cuatro slots de papel y cuatro fondos. No demuestra cumplimiento de los contratos C1–C11. |
| `src/platform/zx0.s` | Wrapper y descompresor Z80; no es un renderer de sprites compilados. |
| `src/generated/runtime_assets.s` | Principalmente datos `.db`; la extensión de ensamblador no convierte los gráficos en instrucciones de dibujo. |
| `tools/build_runtime_assets.py` | Prepara espejos y variantes desplazadas antes de ejecutar en CPC. |
| `cfg/build_config.mk` | SDCC/SDAS, CPCTelera, `--sdcccall 0`, `--opt-code-size`; pila actual en `0x7ff0`, fondo en `0x8000`, vídeo en `0xc000`. |
| `build/DEVUELTO.*` | Hay artefactos de build. Su existencia no prueba procedencia reproducible, correspondencia con el fuente actual ni ejecución correcta. |
| Makefile | Define `build`, `assets`, `assets-check`, `doctor`, `run`, `clean`. `doctor` y `assets-check` invocan scripts que faltaban en esta inspección. `run` apunta a una ruta distinta del ejecutable `.tools/cap32` observado. Auditar antes de usar. |
| `STATUS.json` v1 | Las 35 tareas seguían pendientes. Conservar ese estado hasta demostrar sus criterios; no marcar tareas por encontrar archivos parecidos. |

La configuración actual no es la candidata A: no activar paginación con la pila en la ventana `4000–7fff`. T02/T05 deben establecer y verificar el nuevo mapa. La aritmética de la física actual, la pausa, la devolución y el dibujo de papeles deben contrastarse con los contratos; no usarlos automáticamente como oráculo.

El original ya usa sprites de CPCTelera y restauración bajo actores. Su clave de invalidación puede recomponer escena y HUD cuando cambian puntos/mensajes. Ambas observaciones salen de `../banterhouse/src/game_render.c`; no prueban por sí solas cuánto tiempo se ahorrará.

## 2. Cómo trabajar una sesión

1. Leer AGENTS, plan principal y STATUS. Reanudar una tarea `in_progress` habilitada; si no, seleccionar la primera `pending` habilitada en el orden del array. Una tarea habilitada tiene todas las dependencias `done`.
2. Leer sólo su ficha O o T, contratos citados y pruebas requeridas. Verificar de nuevo rutas y contenido antes de editar: el inventario anterior puede haber cambiado.
3. Marcar `in_progress` y `substep` con el primer paso concreto. Mantener `remaining` explícito.
4. Implementar **un subpaso estable**. Si no se puede completar la tarea, dejarla `in_progress`; no saltar sus dependencias.
5. Ejecutar primero el caso pequeño, después las regresiones afectadas. Las comparaciones largas se hacen en el gate que las solicita, no en cada edición.
6. Guardar resultados, incluidos los negativos. Actualizar estado y siguiente comando exacto que otro ejecutor pueda retomar.
7. Un experimento puede terminar `done` con `outcome: rejected` si se ejecutó y documentó por qué no compensa. Eso no activa su código en la variante elegida.

La petición actual autoriza preparar este plan. La ejecución se inicia cuando se encargue implementar. No poner tareas `done` por redactar sus fichas. No delegar ni crear chats automáticamente.

## 3. Orden y enlace con las 35 tareas existentes

| Fase | Tareas | Punto de unión |
|---|---|---|
| Inventario y preservación | O00 → T01; O01 tras T01 | Guardar prototipo actual y referencia histórica antes de cambios |
| Base correcta | T02–T06; O02 y O04 | Reloj, memoria, bancos y renderer G correctos |
| Juego mínimo | T07–T17 con H0/H1 | Se conserva el recorrido jugable ya definido |
| Comparación congelada | O03 → O05 | M2, casos gráficos y evidencia temporal |
| Optimizaciones aisladas | O06 → O07 → O08 → O09 → O10 → O11 → O12 | Flags, restauración, regiones, sprites Z80, bancos y audio |
| Decisión de presentación | O13 → O14 → T19 → T20 | T19 resume los experimentos; no repite su implementación |
| Carga y residencia | T21–T24 → O15 → T25 | Validar ahorro y tiempo real antes de producir capítulos |
| Candidato | T26–T33 → O16 → T34/T35 | Regresión y documentación de emulación; hardware en T34 |

T18/H2 puede seguir pendiente mientras se mide O03–O14; no bloquea investigación de rendimiento. T21 sigue dependiendo de T18 y T20. O16 no depende de T34: permite entregar emulación sin afirmar certificación física.

## 4. Tres comparaciones distintas

**Histórica:** observar el primer juego publicado o su binario disponible desde una copia en la secuela. Etiquetar métricas como históricas si no se repiten. No comparar sus FPS con M2 como si tuvieran la misma carga.

**Fixture heredado:** O01 copia/adapta exclusivamente las rutas necesarias, conservando procedencia. Alimentarlas con la misma lista de dibujos y recursos que una ruta nueva. Si una ruta no admite clipping, sólo comparar su dominio compartido; documentar por separado esa limitación.

**Secuela:** todas las variantes G/H usan el mismo binario lógico o fuentes/flags de lógica fijados, estados, scheduler, música, entrada y geometría. Sólo cambia el módulo experimental. Un benchmark gráfico alimentado con estados artificiales prueba dibujo; un replay de entrada prueba integración. Conservar ambos.

## 5. Variantes y regla de aceptación

Nombrar `G-base` a la referencia genérica correcta, nunca al prototipo defectuoso. `G-flags`, `G-restore`, `G-dirty` cambian un factor cada vez. `H-pitu` y `H-cast` añaden sprites especializados. `A-selected` integra sólo cambios aceptados. `B-trial` existe sólo si O13 activa ese ensayo.

Cada build incluye `variant.json`: ID, parent ID, única variable, fuentes/recursos/flags/hash del SDK, mapa, cadencias, instrumentación y hashes BIN/DSK. Nunca reemplazar G-base en el mismo directorio. El DSK original conservado no se convierte en baseline correcto por renombrarlo.

Para aceptar una optimización de velocidad:

- Cero diferencias de estado o píxeles sin explicar; mismas acciones y contenidos.
- Cero errores de memoria/ABI/bancos/audio nuevos; memoria y pila dentro de contrato.
- Tres runs por variante. Definir `M(v)` como el mayor trabajo de cuadro de los tres runs, y `J(v)` como la diferencia entre el mayor y menor máximo de run. `epsilon = max(2 × resolución temporal, J(base), J(candidate))`.
- Exigir `M(base) - M(candidate) > epsilon` para afirmar mejora del peor cuadro. Este umbral es una regla del proyecto, no una prueba estadística universal.
- Si mejora una primitiva pero no el peor cuadro, informar «mejora local; ganancia global no demostrada». No promover por entusiasmo.
- Un ahorro de RAM puede aceptarse sin aceleración si era el objetivo declarado y no empeora tiempo/latencia más allá de epsilon ni rompe los gates. Registrar bytes liberados y su uso.

El gate global heredado sigue siendo cero deadlines perdidos y trabajo máximo ≤80% del periodo real. Para 50 presentaciones nominales, medir el periodo del perfil; para 25 medir también los plazos de simulación/audio a 50. Rechazar una supuesta mejora que sólo difiera trabajo a la ISR o al cuadro siguiente.

No bajar actores, resolución, poses, sonido ni cadencia para hacer pasar una comparación. Si la escena no cabe, producir medidas y una decisión de alcance separada. No reescribir en otro toolchain por intuición. Primeras técnicas excluidas: SP como destino de sprites, interrupciones deshabilitadas durante un cuadro, código automodificable y streaming FDC durante juego.

## 6. Interfaz de herramientas futuras

Salvo el comprobador documental señalado abajo, esta tabla es **un contrato por implementar**. Una receta Make sin implementación no cuenta como herramienta disponible. Cada creador añade `--help`, valida argumentos y prueba un error deliberado.

| Creador | Interfaz prevista | Salida mínima |
|---|---|---|
| O00 | `python3 tools/audit_runtime.py --out DIR` | `inventory.json`, discrepancias, hashes y snapshot acotado |
| T01 | `make doctor` | Toolchain/SDK/emulador detectados y causas de ausencia |
| T02 | `make build check-map smoke-boot repro` | BIN/DSK/mapa/guardas y reproducibilidad real |
| O01 | `python3 tools/capture_legacy_reference.py --original ../banterhouse --out DIR` | Copia acotada y manifiesto de procedencia, sin ejecutar el original |
| O02 | `python3 tools/run_cpc_case.py --case CASE --variant VARIANT --profile PROFILE --out DIR` | Binario ejecutado, checkpoint/VRAM/tiempos según capacidad |
| O03 | `python3 tools/freeze_benchmark.py --manifest FILE --out DIR` | Fixtures y hashes, rechazo de entradas incompletas |
| O04 | `make test-render` ampliado | Diferencias gráficas, coordenadas, guardas |
| O05 | `python3 tools/run_benchmark.py --variant VARIANT --fixture DIR --profile PROFILE --runs 3 --out DIR` | `frames.csv`, `audio.csv`, `summary.json`, metadatos |
| O06 | `make build-variant VARIANT=NAME` | Directorio independiente y `variant.json` |
| O09 | `python3 tools/compile_sprites.py --manifest FILE --out DIR` | Plan de operaciones, `.s`, descriptores y coste de almacenamiento |
| O10 | `make test-compiled-sprites` | Resultados host y Z80 separados |
| O11 | `python3 tools/check_residency.py --manifest FILE --map FILE --out DIR` | Ocupación por fase/banco y solapes |
| O14 | `python3 tools/compare_benchmarks.py --baseline DIR --candidate DIR --out DIR` | Comparación o rechazo explícito de equivalencia |
| O15 | `make bench-loads` | Tiempos completos y pico de memoria con recursos reales |
| O16 | `make verify-performance` | Matriz del candidato con pendientes visibles |

Disponible al entregar la revisión v2: `python3 tools/check_implementation_plan.py`. Sólo valida documentos, IDs y dependencias. No construye ni ejecuta el CPC.

## 7. Evidencia y fallos

Carpeta nueva por ejecución: `research/runs/<fecha>-<task>-<build-id>-<run-id>/`. No sobrescribir un run anterior. Comandos contienen rutas reales, configuración y flags completos. No guardar secretos ni redistribuir ROMs; registrar su hash y origen local.

`results.json` tiene `schema_version`, `task_id`, `build_id`, `environment`, `commands` (argv, cwd, exit_code, stdout/stderr), `cases` (id, status, evidence, reason), `unmeasured`, `next_step`. Estados de caso: `pass`, `fail`, `blocked`. Cero es un resultado medido; falta de dato se representa con `null`. Exit codes de runners propios: 0 todos los casos requeridos pasaron; 1 fallo; 2 falta de entorno; 3 argumentos/manifiesto inválidos. No cambiar los exit codes del SDK: registrarlos y traducir sólo en el runner.

Por experimento crear `decision.md`: hipótesis, variable, baseline, resultados locales/globales, RAM extra, peor caso, limitaciones, `accepted/rejected/conditional`, y variante que queda activa. `conditional` no habilita promoción al juego final.

Si falla: conservar el primer caso, reducirlo, cambiar una causa y repetir. Tras dos intentos distintos sin avance en ABI/ISR/bancos/FDC, preparar una reproducción y revisión técnica; no dar por aprobada la tarea. Un emulador sin interfaz temporal verificable permite trabajo funcional pero bloquea las afirmaciones de tiempo. El paquete de revisión humana o hardware se prepara antes de solicitar esa intervención.

## 8. Fuentes y límites

Los contratos del SDK se comprueban contra su revisión fijada: [sprites enmascarados](https://lronaldo.github.io/cpctelera/files/sprites/cpct_drawSpriteMasked-asm.html), [paginación](https://lronaldo.github.io/cpctelera/files/memutils/cpct_pageMemory-asm.html), consultados el 11 de octubre de 2026. La [investigación técnica](../TECHNICAL_RESEARCH.md) contiene más fuentes y sus límites. Una cifra de documentación de una primitiva no sustituye el tiempo medido del juego.

El cierre entrega mejoras cuantificadas y límites conocidos. Nunca la afirmación indemostrable de que ya no existe ninguna optimización posible para el CPC.
