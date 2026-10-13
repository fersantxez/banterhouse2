# Tres arquitecturas candidatas para 128 KiB

> **Diseño e investigación históricos.** Este documento conserva propuestas y decisiones de su fecha; no describe por sí solo la build actual. Consulta [Estado](STATUS.md) y [la guía de lectura](README.md).

2026-10-10. **Todo este documento es [P] diseño propuesto**, salvo límites de hardware y aritmética indicados. No son mapas del binario enlazado ni mediciones de FPS. KiB = 1.024 bytes. Presupuestos comprobables en [memory-budgets.json](../research/memory-budgets.json).

La [aclaración creativa](CREATIVE_DIRECTION.md) cambia su uso: estas tres candidatas son ejemplos técnicos, no una elección de género o cámara. Primero se exploran reglas y respuesta al control. Las cuotas de 25 Hz de B/C son escenarios de coste; no constituyen una aceptación de esa cadencia para un juego de acción rápida.

El [plan de campaña en disco del 11 de octubre](DISK_CONTENT_PLAN.md) toma A como punto de partida para probar paquetes y propone subdividir sus 8 KiB de lógica en 4 KiB fijos y 4 KiB de overlay. No cambia estas reservas históricas ni acredita un mapa de linker; B/C siguen como alternativas condicionadas a resultados.

## Reglas comunes

Ocho bancos físicos de 16 KiB = 128 KiB. En C0: RAM0 `0000–3FFF`, RAM1 `4000–7FFF`, RAM2 `8000–BFFF`, RAM3 `C000–FFFF`. En C4, C5, C6 o C7, sólo la segunda ventana cambia a RAM4, RAM5, RAM6 o RAM7. RAM1 sigue existiendo aunque quede oculta. El vídeo permanece en RAM0–3 físicas. [Tabla de hardware/API](https://lronaldo.github.io/cpctelera/files/memutils/cpct_pageMemory-asm.html).

Inicialmente firmware y ROMs desactivados tras bootstrap, IM1 controlado, banco sombra en RAM0, far handles `{banco, offset, longitud, generación}`. Todo cambio de banco vuelve al estado del llamador. Las actualizaciones de banco y su sombra deben ser atómicas respecto a ISR. La ISR usa RAM0 y no llama al gestor ni al renderer. No se almacenan punteros a datos paginados para usarlos después de devolver el banco.

Reserva RAM0 común (suma exacta **16.384 B**):

| Dirección inclusiva | B | Reserva |
|---|---:|---|
| 0000–00FF | 256 | Vectores, arranque mínimo, IM1 |
| 0100–23FF | 8.960 | Código residente: ISR/scheduler, API bancaria, FDC, decoder, player y núcleo gráfico |
| 2400–2FFF | 3.072 | Canción/efectos calientes; el código del player se cuenta arriba |
| 3000–37FF | 2.048 | Estado, colisiones calientes, tabla de actores, colas y telemetría |
| 3800–3BFF | 1.024 | Dos sectores de staging o bounce buffer |
| 3C00–3CFF | 256 | Guardas de pila y separador |
| 3D00–3FFF | 768 | Pila descendente; SP inicial 4000, primer push en 3FFE |

Estas reservas son exigentes, especialmente los 8.960 B de código con audio+FDC+decoder. Si el enlace las supera, A puede trasladar lógica a RAM2; B y C deberán reducir núcleo, usar overlay durante cargas o descartarse. El guard no es espacio utilizable; el criterio adicional pide 256 B libres **dentro** de los 768 B de pila tras medir el máximo.

El buffer de 1 KiB no permite prometer streaming de cualquier decoder. Sólo sirve para copias entre ventanas en bloques, sectores o formatos con bloques independientes pequeños. Los formatos comprimidos y su estado deben diseñarse expresamente si se quieren alimentar por fragmentos.

## A: habitaciones, pantalla única y renderer híbrido

| Banco físico | Ventana CPU | Reserva interna (KiB) | Total |
|---|---|---|---:|
| RAM0 | 0000 fija | Núcleo/estado/audio/pila descritos arriba | 16 |
| RAM1 | 4000 en C0 | Fondo limpio 16 | 16 |
| RAM2 | 8000 fija | Lógica residente 8 + scratch/primer plano 4 + save-under 2 + trabajo/guardas 1 + margen 1 | 16 |
| RAM3 | C000 fija | Pantalla visible 16 | 16 |
| RAM4 | 4000 en C4 | Animación/código de protagonista 14 + margen 2 | 16 |
| RAM5 | 4000 en C5 | Sala/tiles/piezas 12 + colisiones/índice 2 + margen 2 | 16 |
| RAM6 | 4000 en C6 | Animación NPC compartida 12 + efectos 2 + margen 2 | 16 |
| RAM7 | 4000 en C7 | Caché/paquetes comprimidos 14 + índice/margen 2 | 16 |
| **Suma física** | | **32 residentes/auxiliares + 32 fondo/vídeo + 64 paginados** | **128** |

Dos modos de restauración a comparar: (a) guardar bajo actores y restaurar en orden inverso; (b) recomponer regiones desde RAM1 limpia. La segunda permite olvidar contenido de save-under y usar esos 2 KiB para listas/colas; no sumar ambas ventajas como memoria libre simultánea. Se restaura con C0, luego se pagina y dibuja por actor/grupo. No mezclar fondo limpio y actor del banco RAM4 en la misma ventana.

Ventaja: RAM2 fija admite lógica C, clipping y buffers sin forzar un núcleo mínimo. Riesgo: escribir en la pantalla mostrada produce tearing o borrado visible. Iniciar tras VSYNC ayuda, pero no prueba ausencia de artefactos; hace falta comparar posición vertical de actualización y captura/hardware. Si la escena no cumple calidad visual, B sigue siendo opción aunque A sea más rápida.

Durante transición se suspende composición normal: usar 4 KiB de scratch fijo en RAM2 para entrada comprimida en bloques **independientes** de tamaño limitado; expandir a la ventana del banco destino. Para una pantalla de 16 KiB, mapear RAM7 como fuente y expandir hacia RAM3; presentar sólo cuando esté lista o mantener una transición acordada. Un bloque comprimido mayor de 4 KiB destinado a un banco se divide en el packer o se cambia el mapa temporal, nunca se pisa lógica fija.

## B: habitaciones con doble búfer y núcleo pequeño

| Banco físico | Ventana CPU | Reserva interna (KiB) | Total |
|---|---|---|---:|
| RAM0 | 0000 fija | Núcleo/estado/audio/pila común, toda la lógica caliente debe caber | 16 |
| RAM1 | 4000 en C0 | Fondo limpio 16 | 16 |
| RAM2 | 8000 fija | Página A 16 | 16 |
| RAM3 | C000 fija | Página B 16 | 16 |
| RAM4 | 4000 en C4 | Protagonista compilado/datos 14 + margen 2 | 16 |
| RAM5 | 4000 en C5 | Sala 12 + colisiones/índice 2 + margen 2 | 16 |
| RAM6 | 4000 en C6 | NPC/efectos 14 + margen 2 | 16 |
| RAM7 | 4000 en C7 | Caché/paquetes comprimidos 14 + índice/margen 2 | 16 |
| **Suma física** | | **16 núcleo + 16 fondo + 32 vídeo + 64 paginados** | **128** |

Cada página necesita su propia lista de regiones y versión de HUD/objetos. Antes de reutilizar la página oculta, restaurar regiones de la última imagen dibujada **en esa página**. Dibujar el estado actual y cambiar CRTC sólo en frontera de presentación sincronizada. No copiar 16 KiB de frente a fondo cada vez.

Carga comprimida hacia banco: mantener una pantalla visible, usar la página oculta como staging fijo de hasta 16 KiB, expandir desde ella hacia RAM4–7 en 4000, validar CRC y después recomponer la página. Cargar directamente el staging desde FDC evita mover RAM7→RAM2 innecesariamente. Para producir una pantalla/fondo fijo, mapear el banco comprimido como fuente y escribir en la página fija. **RAM7 y RAM4 no son visibles a la vez** bajo este contrato. Si se necesita conservar simultáneamente ambas páginas acabadas y fondo limpio durante una carga, este procedimiento no sirve: hay que cambiar transición o almacenamiento.

Guardar recurso activo intacto ante error exige escribir a un banco libre o staging y confirmar después. Con los cuatro bancos llenos, «recargar in situ y mantener el anterior si falla» no es posible sin copia. En transición se puede declarar inválido el conjunto saliente y ofrecer reintento/retorno a un estado seguro residente.

## C: scroll continuo con superficie de 32 KiB y HUD separado

Es la candidata de mayor riesgo. **No es doble búfer**: los 32 KiB forman almacenamiento de scroll, no dos cuadros completos que se intercambian. Todavía falta demostrar el programa CRTC que use esa superficie y sus envolturas.

| Banco físico | Ventana CPU | Reserva interna (KiB) | Total |
|---|---|---|---:|
| RAM0 | 0000 fija | Núcleo/estado/audio/pila común | 16 |
| RAM1 | 4000 en C0 | Reserva completa 16 para página física del HUD/split | 16 |
| RAM2 | 8000 fija | Primera mitad de superficie scroll 16 | 16 |
| RAM3 | C000 fija | Segunda mitad de superficie scroll 16 | 16 |
| RAM4 | 4000 en C4 | Protagonista 14 + margen 2 | 16 |
| RAM5 | 4000 en C5 | Tiles 8 + mapa de zona 6 + colisiones 2 | 16 |
| RAM6 | 4000 en C6 | NPC/efectos 14 + margen 2 | 16 |
| RAM7 | 4000 en C7 | Caché de zona/paquetes 12 + tiras de borde 2 + margen 2 | 16 |
| **Suma física** | | **16 núcleo + 48 vídeo reservado + 64 paginados** | **128** |

La reserva de HUD de 16 KiB evita fingir que 16 líneas se alojan siempre en 1.280 bytes contiguos con el addressing CPC habitual. Podrá reducirse cuando se pruebe un layout concreto. La RAM1 oculta a CPU sigue disponible para vídeo; se actualiza HUD sólo al volver a C0.

Primera prueba: scroll grueso con cámara de recorrido fijo, sólo luego suavidad de un píxel si compensa. El origen CRTC y el puntero CPU se calculan por separado. Restaurar actores por posición física previa antes de reutilizar tiras; regenerar tiles de fondo en el área sucia. Con scroll fino/rupturas, no asumir una simple suma lineal de 32 KiB ni R12/R13 idénticos entre CRTCs. La prueba de wrap, split y reversión de cámara precede a producir niveles.

Cargas sólo con scroll detenido; después regenerar superficie y HUD. Streaming continuo no está presupuestado. Si requiere los 32 KiB intactos, no se puede usar una mitad como staging; se carga raw hacia banco o se habilita explícitamente una pantalla de transición en RAM1.

## Tiempo: cuotas de diseño, no tiempos observados

Para evitar prometer 50 fps, A tiene una hipótesis de 50 Hz y B/C una de 25 Hz; **las tres se medirán también a la misma cadencia**. Estas cuotas indican cuándo rechazar una configuración. En B/C el audio a 50 Hz se atiende dos veces por presentación.

| Fase | A / 20 ms nominales | B / 40 ms nominales | C / 40 ms nominales |
|---|---:|---:|---:|
| Restaurar + guardar + dibujar actores/primer plano | 8,5 ms | 22 ms | 17 ms |
| Bordes/tiles de scroll | 0 | 0 | 6 ms |
| Simulación y controles | 2 ms | 4 ms | 3 ms |
| Audio + coste ISR | 1,5 ms | 3 ms | 3 ms |
| Cambios de banco/descriptores | 0,5 ms | 1 ms | 1 ms |
| HUD/objetos persistentes | 1 ms | 1 ms | 1 ms |
| Scheduler/split/instrumentación/otros | 2,5 ms | 1 ms | 1 ms |
| **Trabajo máximo propuesto** | **16 ms** | **32 ms** | **32 ms** |
| **Margen deseado** | **4 ms** | **8 ms** | **8 ms** |
| **Total** | **20 ms** | **40 ms** | **40 ms** |

Para 19,968/39,936 ms reales, el límite del 80% es 15,9744/31,9488 ms: ajustar el gate y no redondear a favor de un resultado. Las cuotas internas podrán moverse, pero no desaparecer guardas, audio ni tiempo del scheduler. Cargas y reconstrucción inicial se registran como transiciones separadas, nunca se eliminan de la estadística sin publicar su clase y duración.

Cuatro actores de 16×32 suman al menos 1.024 bytes de rectángulo; con desplazamiento, hasta 1.152. Guardar y restaurar esas regiones ya implica miles de accesos, más máscara, dirección, lógica y llamadas. Por eso las cuotas A son una hipótesis ambiciosa y falsable, no un cálculo de velocidad basado sólo en RAM o reloj.

## Selección

Elegir tras los microprototipos jugables. A permite un fixture técnico sencillo; B debe justificar su coste con presentación y respuesta; C debe responder a una cámara útil para las reglas nuevas. No presuponer que una habitación sea preferible al scroll ni que C deba ser una evolución de B. Ninguna candidata obliga a abandonar CPCTelera. La decisión requiere el binario, mapa del linker, peor cuadro y pruebas de CRTC/disco descritas en el plan.
