# Plan de implementación y pruebas de Banterhouse 2

> Nota de archivo. Algunas propuestas de este documento se descartaron o siguen pendientes. Consulta el [estado actual](STATUS.md).

Versión 2 · 11 de octubre de 2026 · CPC 6128 clásico de 128 KiB.

Este plan divide la implementación de ¡Devuelto! en tareas para un agente que trabaje con poco contexto. El primer resultado es un pequeño juego con movimiento, salto, sonidos y devolución; la campaña se construye después de probar ese núcleo. Cada tarea tiene dependencias, archivos, pasos, pruebas y una condición de cierre.

**Estado observado en la revisión v2:** existen `src/`, Makefile, recursos generados y artefactos BIN/DSK del prototipo. Falta comprobar si cumplen los requisitos de las tareas T. La documentación v1 se había quedado atrás respecto al código. Empezar por O00 para conservar y auditar lo existente; no reconstruirlo a ciegas ni marcar tareas como terminadas. La aprobación estética no acredita jugabilidad, rendimiento o compatibilidad.

La ampliación [Optimización CPC para 6.1 Luna](implementation/OPTIMIZATION_PLAN.md) concreta 17 tareas adicionales y 20 pruebas de optimización. Se integra en el mismo STATUS: **52 tareas en total**, una habilitada cada vez. El documento se redactó antes de ejecutar esas tareas.

El [plan de reparación de la física de Pitu](implementation/PHYSICS_REPAIR_PLAN.md) y su [seguimiento F00–F08](implementation/PHYSICS_STATUS.json) definen una intervención prioritaria sobre la suspensión al abandonar plataformas y su regresión en las 24 arenas actuales. `make physics-plan-check` valida las fichas y sus dependencias junto con el plan general. Las pruebas de teclado, arte, hardware y las revisiones con jugadores se registran por separado.

La [reparación prioritaria de entrega](implementation/DELIVERY_REPAIR_PLAN.md) añade E00–E04: reproducir carga, corregir el bucle, completar todas las arenas en emulador y bloquear el empaquetado si no hay evidencia del mismo disco. Su seguimiento está en [DELIVERY_STATUS.json](implementation/DELIVERY_STATUS.json); se ejecuta antes de reanudar T06.

## Prioridad actual: entrega rechazada y reparación autónoma

El nuevo reporte del usuario reabre la aceptación: los BIN fallan y la primera fase se oye sólo como beats. Seguir primero [AUTONOMOUS_REPAIR_PLAN.md](implementation/AUTONOMOUS_REPAIR_PLAN.md), [su estado](implementation/AUTONOMOUS_STATUS.json) y [el prompt continuo](implementation/AUTONOMOUS_EXECUTOR.md). N00–N10 incluye diagnóstico, aislamiento, carga, controles, vídeo, música, campaña, validadores negativos y limpieza obligatoria. E00–E04 conserva historia, no aceptación actual. Para esta ruta, ejecutar una ficha habilitada cada vez y continuar con la siguiente durante la ejecución autorizada; la regla antigua de terminar tras una tarea no aplica. Este cambio documental no inicia por sí solo la implementación.

## Cómo usar el plan

1. Dar al ejecutor el [prompt de arranque](implementation/EXECUTOR_PROMPT.md).
2. Consultar [STATUS.json](implementation/STATUS.json): reanudar una tarea en progreso habilitada o seleccionar la primera pendiente habilitada en el orden del array. El arranque de esta revisión es O00, antes de T01. No ejecutar todo el plan en una sola sesión.
3. Para un ID T, leer su ficha en [TASKS.md](implementation/TASKS.md); para un ID O, en [OPTIMIZATION_TASKS.md](implementation/OPTIMIZATION_TASKS.md). Leer sólo los contratos y pruebas que cite; OP01–OP20 están en [OPTIMIZATION_TESTS.md](implementation/OPTIMIZATION_TESTS.md).
4. Implementar una tarea; en las fichas divididas, un subpaso que deje el build estable puede ocupar una sesión. Guardar el punto exacto de continuación.
5. Ejecutar sus pruebas y las regresiones afectadas. Registrar comandos, exit codes, binario, entorno y evidencias reales.
6. Marcarla terminada únicamente si cumple su cierre. Un test no ejecutado queda pendiente. Continuar con otra tarea sólo cuando esté autorizada y sus dependencias estén resueltas.

No hace falta volver a preguntar por cada tarea reversible. Las revisiones humanas señaladas en el plan sirven para evaluar juego y arte: presentar antes un DSK concreto, instrucciones y observaciones. Si falta hardware, emulador o respuesta humana, avanzar en trabajo independiente habilitado; no simular el resultado que falta.

## Documentos de ejecución

| Documento | Para qué sirve |
|---|---|
| [OPTIMIZATION_PLAN.md](implementation/OPTIMIZATION_PLAN.md) | Inventario actual, método de ejecución y reglas de adopción |
| [OPTIMIZATION_TASKS.md](implementation/OPTIMIZATION_TASKS.md) | 17 fichas pequeñas enlazadas a las tareas T |
| [OPTIMIZATION_TESTS.md](implementation/OPTIMIZATION_TESTS.md) | 20 ensayos, negativos y formatos de evidencia |
| [TASKS.md](implementation/TASKS.md) | Orden de implementación, cambios permitidos y pruebas por tarea |
| [CONTRACTS.md](implementation/CONTRACTS.md) | Reglas exactas de entrada, física, colisión, dibujo, audio y carga |
| [TESTS.md](implementation/TESTS.md) | Casos reproducibles, resultados esperados y evidencia exigida |
| [STATUS.json](implementation/STATUS.json) | Estado y dependencias, sin confundir planificación con código existente |
| [EXECUTOR_PROMPT.md](implementation/EXECUTOR_PROMPT.md) | Instrucción lista para copiar a otro modelo |

En caso de discrepancia: instrucciones actuales del usuario y `AGENTS.md` primero; dirección creativa y reglas de producto después; este plan concreta cómo empezar. Los valores nuevos de los contratos son **decisiones provisionales de laboratorio**, identificadas como tales, no cambios al canon ni resultados medidos. No elegir silenciosamente entre dos documentos contradictorios: registrar la discrepancia y resolverla antes del cambio dependiente.

## Ruta elegida para empezar

| Área | Elección inicial | Qué permite cambiarla |
|---|---|---|
| Lenguaje y build | C con SDCC, SDAS y primitivas CPCTelera; una sola ABI y un enlazador | Fallo reproducible de integración o comparación equivalente favorable |
| ABI | `--sdcccall 0` en código propio; wrappers explícitos para APIs con otra convención | Auditoría y prueba de llamadas, nunca cambio global por ensayo y error |
| Imagen | Mode 0 estándar, 160×200, una paleta fija por pantalla | Experimento posterior separado; Plus fuera del objetivo |
| Cámara | Arena completa, sin scroll en el primer juego de prueba | Problema jugable confirmado; requiere revisar tareas dependientes |
| Memoria | Candidata A como mapa provisional; restaurar desde fondo limpio | Mapa de linker o medición que obligue a revisar; decisión definitiva en T20 |
| Renderer | G genérico correcto primero; experimento H limitado después | Comparación con mismos píxeles, entrada, audio y cadencia |
| Simulación | Paso fijo nominal de 50 Hz, independiente del número de presentaciones | Ninguna bajada de render cambia física o temporizadores |
| Audio | SFX simples desde M0; reproductor musical después | Coste y escucha de una escena con música y SFX |
| Disco temprano | AMSDOS sólo para arrancar/cargar el prototipo antes de entregar control | Loader de recursos posterior; ningún acceso durante un intento |
| Disco final | Carga bloqueante entre paquetes, sin música durante la transferencia inicial | Ensayo específico que demuestre audio/FDC seguros |
| Ahorro | Tiles, paquetes con vida conocida, variantes generadas al cargar, raw + un codec | Contabilización de RAM, CPU y disco del recurso real |

No iniciar a la vez versiones en RASM, z88dk, TRSE y 8BP. Son alternativas investigadas, no cuatro obligaciones de implementación. No implementar inicialmente scroll, overscan, rasters, sprites con SP como destino, streaming ni código overlay. Un overlay sólo se abre como tarea separada si el mapa final lo necesita; cargar datos de un capítulo no obliga a sustituir código.

## Hitos y puntos de revisión

| Hito | Tareas | Entregable visible | Condición para avanzar |
|---|---|---|---|
| Auditoría | O00, T01, O01 | Prototipo conservado, herramientas y referencia de primera parte | Inventario y procedencia; ninguna escritura en el original |
| Base ejecutable | T02–T06, O02, O04 | DSK mínimo, galería CPC y personaje dibujado correctamente | Build reproducible, bancos y píxeles verificados |
| M0 | T07–T10 | Recorrido con movimiento, salto y sonidos | Prueba humana H0 del control |
| M1 | T11–T14 | Una máquina, devolución, daño y reintento | Prueba humana H1 de la interacción |
| M2 | T15–T18 | Tres máquinas, Alberto, dos rutas y panel opcional | Prueba humana H2 con arte y música |
| Decisión técnica | O03, O05–O14, T19–T20 | Peor cuadro, memoria y renderer elegido | No aceptar una mejora que cambie la escena comparada |
| Cargas completas | T21–T25, O15 | Dos arenas, encuentro y viñeta con errores recuperables | Prueba humana H3 y reintentos sin disco |
| Primer capítulo | T26–T28 | Menú, reparto nativo y seis pantallas | Prueba humana H4 de variedad y ritmo |
| Campaña | T29–T32 | Capítulos 2–4 y dos caras empaquetadas | Niveles resueltos, cuotas reales y guardas intactas |
| Candidato final | T33–T35, O16 | Matriz de pruebas, DSK y guía de ejecución | H5; hardware físico necesario para certificarlo |

Las tareas T19 y T20 pueden medir una M2 todavía pendiente de H2; la producción y la integración de nuevos paquetes requieren que H2 esté aceptada. Así se puede investigar mientras se espera una partida, sin convertir la espera en aprobación automática.

## Qué existe y qué se debe crear

**Observado:** diseño, estudios gráficos y scripts de investigación; prototipo `src/main.c`, descompresor Z80, generador de recursos, configuración/Makefile y salidas de build. El [inventario inicial](implementation/OPTIMIZATION_PLAN.md#1-punto-de-partida-observado) explica límites y rutas rotas detectadas. Su existencia no cierra pruebas.

**Por verificar o implementar:** build reproducible, contratos de simulación, reloj independiente, clipping completo, mapa/bancos seguros, audio integrado, comparaciones G/H, loader y campaña. O00/T01 reconcilian capacidades disponibles antes de reutilizar comandos.

Comandos documentales/de investigación existentes:

```sh
python3 tools/check_implementation_plan.py
python3 tools/check_research_budgets.py
python3 tools/check_campaign_budget.py
```

El primero valida sólo este plan. Los otros comprueban aritmética de propuestas. `tools/build_cpc_screen_studies.py --compress` regenera arte y necesita las dependencias descritas en `research/README.md`; no ejecutarlo para una edición documental. Las interfaces futuras de optimización tienen creador explícito en su plan. No presentar una receta Make rota como comando funcional.

Estructura que se irá creando, sin añadir directorios vacíos por adelantado:

```text
src/platform/       boot, entrada, reloj, bancos, AY, FDC y wrappers ASM
src/core/           simulación C compartida por host y Z80
src/render/         G, referencia de contratos y posterior H
src/game/           estados, campaña y encuentros
assets/source/      arte canónico congelado y ediciones de producción
assets/levels/      geometría y objetos; separado de los píxeles
assets/audio/       fuentes y exportaciones reproducibles
cfg/                toolchain fijada, memoria y perfiles de emulador
tests/host/         casos de lógica, packer y formatos
tests/fixtures/     entradas grabadas, estados esperados y casos de error
tools/              conversores, validadores y runners
build/              sólo salidas regenerables
research/runs/      evidencias conservadas por tarea y build
docs/implementation/decisions/  decisiones justificadas, cuando existan
```

El primer Banterhouse se consulta sólo en lectura. No ejecutar sus scripts `run_*` directamente: varios hacen `make`, restauran releases o escriben logs dentro de ese proyecto. Copiar y adaptar el código mínimo necesario a la secuela, conservando procedencia y avisos.

## Estados y cierre de tareas

Estados permitidos: `pending`, `in_progress`, `blocked`, `done`. `blocked` en este archivo es seguimiento del proyecto, no una llamada a la herramienta de objetivos. Añadir causa precisa y siguiente acción; no usarlo para una dificultad que el ejecutor puede resolver.

Las tareas O añaden `outcome`: `accepted`, `rejected`, `not_needed` o `report_only` según su ficha; `null` antes de ejecutar. Un experimento rechazado puede terminar con evidencia completa; no activa su código.

Cada entrada conserva: `id`, `depends_on`, `status`, `substep`, `evidence`, `remaining`, `blocker`. Las tareas de revisión tienen además `human_review`; `done` requiere el resultado humano enlazado. No confundir `tests passed` con `fun approved`.

Una evidencia mínima contiene:

```text
Tarea y subpaso:
Build y hashes de entradas:
Entorno, ROM, CRTC y configuración:
Comandos ejecutados y exit codes:
Casos y resultados, incluidos fallos:
Archivos de captura, traza y mapa:
Mediciones no disponibles:
Cambio respecto a la referencia:
Siguiente paso exacto:
```

Los registros de tiempos y memoria usan `null` cuando falta medición. Un runner termina con código no cero si falta una prueba exigida; puede indicar `BLOCKED`, pero nunca `PASS` por ausencia de emulador. Un `TODO`, una captura del generador host o una salida simulada no cierran una prueba Z80.

No sobrescribir evidencias anteriores. No actualizar automáticamente capturas esperadas o hashes para hacer pasar un test. Explicar cualquier cambio de referencia y volver a ejecutar los casos afectados.

## Cuándo pedir una decisión y qué preparar antes

- **Control o arte:** entregar DSK, controles, versión, imágenes y el problema observable antes de solicitar valoración humana.
- **Desbordamiento de RAM o deadlines:** entregar mapa, peor caso y dos opciones acotadas. No reducir actor count, ritmo, paleta o animación sin dejarlo explícito.
- **Bug complejo de ABI, bancos, ISR o FDC:** tras dos intentos distintos sin progreso, conservar reproducción mínima y logs; solicitar revisión técnica. Se puede continuar en otra tarea habilitada.
- **Falta de hardware:** completar la matriz de emulación y preparar un paquete de prueba para el CPC. La certificación física queda abierta, no todo el proyecto.

## Fuentes que acompañan la implementación

La base de diseño está en [GAME_DESIGN.md](GAME_DESIGN.md), la campaña en [STORY_STRUCTURE.md](STORY_STRUCTURE.md), los costes en [DISK_CONTENT_PLAN.md](DISK_CONTENT_PLAN.md) y la validación extensa en [PROTOTYPE_PLAN.md](PROTOTYPE_PLAN.md). Los objetivos de FPS y carga siguen pendientes de medición.

Para APIs, utilizar la fuente de la revisión fijada de CPCTelera. La documentación primaria de [paginación](https://lronaldo.github.io/cpctelera/files/memutils/cpct_pageMemory-asm.html) y [sprites enmascarados](https://lronaldo.github.io/cpctelera/files/sprites/cpct_drawSpriteMasked-asm.html), consultada el 11 de octubre de 2026, apoya esos contratos; la firma real y las restricciones del binario fijado prevalecen al escribir wrappers. No asignar tiempos de esas primitivas al juego completo.
