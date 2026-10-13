# Fichas de optimización

Leer primero [OPTIMIZATION_PLAN.md](OPTIMIZATION_PLAN.md). Dependencias canónicas en [STATUS.json](STATUS.json); pruebas OP en [OPTIMIZATION_TESTS.md](OPTIMIZATION_TESTS.md). Las rutas nuevas son destinos previstos. Nunca reemplazar un archivo existente sin leerlo y conservar su comportamiento necesario. Cada subpaso numerado es una unidad de continuación para Luna; no cerrar la ficha hasta completar todos sus gates.

## O00 Auditar y conservar el prototipo existente

**Depende de:** ninguna. **Leer:** Makefile, `project.mk`, `cfg/build_config.mk`, `src/main.c`, `src/platform/zx0.s`, generador y manifiesto de recursos, T01–T06, C1/C3/C4/C8/C9. **Crear:** `tools/audit_runtime.py`, `docs/implementation/decisions/000-runtime-audit.md`. **No tocar:** lógica ni assets.

1. Inventariar sólo archivos del proyecto relevantes: fuentes, configuración, herramientas propias, recursos usados y artefactos de build. Para cada uno guardar ruta, SHA256 y tamaño. Evitar recorrer SDKs, ROMs y cachés enteras.
2. Conservar una copia de esas entradas en un directorio nuevo de `research/runs/`; guardar también BIN/DSK/mapa existentes con etiqueta `unverified-existing`. No ejecutar `clean` antes. No copiar todo `.tools/` ni `tmp/`.
3. Enumerar recetas Make y comprobar que scripts/rutas referenciados existen. Marcar `declared_only`, `missing_dependency`, `not_executed` o `verified`; no usar «available» por encontrar el nombre de un target.
4. Crear tabla `tarea T → archivos existentes → contratos satisfechos/no verificados → diferencia → siguiente acción`. Revisar específicamente pila en 7ff0, fondo en 8000, ausencia de paginación, reloj ligado al render, geometría/física, flancos/pausa, papel/devolución, audio y clipping. Una discrepancia observada es candidata a corregir, no un benchmark.
5. Registrar que T02 debe crear un perfil mínimo aislado y preservar el prototipo, T03 debe reutilizar el arte y T07 debe contrastar reglas. No reiniciar el proyecto desde cero ni aprobar T01–T17 por semejanza.

**Ejecutar:** OP01; comprobador documental. **Cerrar:** snapshot recuperable, inventario comprobado y lista de discrepancias. **Si falla:** corregir el auditor; si un archivo cambia durante copia, repetir sólo esa captura con nuevo ID. **Continuar:** T01, sin cambiar tareas T a done.

## O01 Congelar referencias de la primera parte

**Depende de:** T01. **Leer:** `../banterhouse/src/game_render.c`, `graphics.c`, `font_renderer.s`, `audio.c`, `game.c`, configuración de build y estado publicado; no ejecutar scripts allí. **Crear:** `tools/capture_legacy_reference.py`, manifiesto y fixtures bajo `tests/fixtures/legacy/`, decisión `o01-legacy.md`.

1. Guardar hashes iniciales de las entradas leídas del original. Copiar a un directorio nuevo en la secuela sólo el código/recursos necesarios para el ensayo. Conservar avisos/procedencia. No incluir saves personales ni dependencias completas.
2. Separar tres etiquetas: binario histórico encontrado; fuente actual inspeccionado; adaptación al harness nuevo. No afirmar que los tres son la misma release sin hashes/procedencia.
3. Definir fixture gráfico mínimo común: fondo fijo, Pitu y Alberto, trayectorias predefinidas en coordenadas admitidas por ambas rutas, cambio de puntuación/mensaje y retirada de actor. Guardar lista de comandos de dibujo por tick, orden y hashes de píxeles. No portar toda la lógica antigua.
4. Crear contrato de adaptador `legacy_render_commands(commands, count)` en el harness de la secuela; conservar el comportamiento de invalidación histórica en una variante `legacy-historical`. Las firmas reales y el build se completan con O02. Registrar cada adaptación que pueda cambiar coste.
5. Si existe binario histórico utilizable, preparar perfil de emulador con configuración/logs en la secuela. Si no, dejar esa observación pendiente y usar adaptación claramente etiquetada. Nunca dar cifras históricas como repetidas.
6. Volver a calcular hashes del original y comprobar igualdad. Exportar dominio común y diferencias de funcionalidad para O03.

**Ejecutar:** OP02. **Cerrar:** procedencia verificable y fixture equivalente definido; la falta de binario publicado no bloquea el fixture adaptado. **Si no hay fuente suficiente:** informar comparación histórica no disponible; no inventar adversario. La comparación interna G/H sigue habilitada mediante una decisión explícita en esta ficha.

## O02 Crear captura e instrumentación verificables

**Depende de:** T04, T06. **Leer:** contratos C3/C8/C9/C10, pruebas P/R/Q, interfaces reales del emulador fijado por T01. **Crear:** `tools/run_cpc_case.py`, `tools/cpc_backend.py`, `cfg/emulator-timing.json`, ampliar `src/platform/telemetry.*` y harness `tests/cpc/`.

1. Consultar ayuda y capacidades reales del emulador. Anotar cómo se carga/reset, observa PC/ciclos, lee memoria y guarda VRAM. Implementar sólo una integración comprobada. Si falta extracción automatizable, admitir captura manual documentada para pruebas funcionales; tiempo queda bloqueado.
2. Definir símbolos de entrada/salida para `restore`, `persistent`, `sprites`, `hud`, `sim`, `audio`, `banks` y ciclo completo. Preferir trazas del depurador sin escritura Z80 por evento. Si se requieren marcas en el binario, aislarlas por macro y medir su coste.
3. Crear harness mínimo con marca de build, contador, bytes centinela y terminación verificable. El runner debe detectar build equivocado, timeout y volcado incompleto. No aceptar sólo «proceso terminó» como prueba del CPC.
4. Calibrar reloj de emulador frente a VSYNC real del perfil y una secuencia ensamblada conocida, considerando WAIT del CPC. Guardar unidades/resolución. Tiempo de pared de Python no mide ciclos CPC.
5. Definir intervalos temporales anidados: trabajo total incluye ISR que lo interrumpen; `audio_us` es un subconjunto, no se suma otra vez al total. Medir servicio ISR durante espera por separado y situarlo en la ventana de deadline correspondiente.
6. Probar límite de buffers. No almacenar 12.000 filas de CSV en RAM del CPC; capturar fuera del invitado o por checkpoints de ejecución funcional separada. Nunca detener/reanudar cada frame dentro del run de tiempos.

**Ejecutar:** OP03, P01/P04, B03. **Cerrar:** evidencia extraída del Z80, fallos detectados y resolución temporal demostrada. **Bloqueo:** si el backend no puede medir, no completar el gate temporal; conservar el trabajo funcional y la causa exacta.

## O03 Congelar cargas comparables y replays

**Depende de:** T17, O01, O02, O04. **Leer:** diseño M2, contratos C1–C10, Q01–Q04. **Crear:** `tools/freeze_benchmark.py`, `tests/fixtures/benchmark/manifest.json`, niveles/replays/estados y hashes.

1. Congelar M2: Pitu, Alberto, tres máquinas, máximo cuatro papeles, panel, poses, geometría, música y efectos reales de T17. No requiere H2 aprobada para medir, pero etiquetar gameplay pendiente si lo está.
2. Crear replay de entradas con 250 ticks de calentamiento y 12.000 medidos. Si incluye resets, definir checkpoints y contadores para que no reutilicen estado de una partida anterior. Guardar estados serializados por tick y checkpoints visuales.
3. Añadir fixtures gráficos dirigidos: alineación par/impar, ocho fases Y, solapes, clipping, sprite quieto que anima, cambios de HUD/fondo y retirada/reutilización de slots. Inyectar comandos sólo en harness gráfico; no falsificar la solución de un nivel.
4. Añadir fixture heredado O01 y estrés de cuatro actores del plan de investigación como suites separadas. No confundir tres enemigos del estrés con la carga habitual de M2 ni rebajar el estrés para ocultar un fallo.
5. Validar todos los recursos y congelar música/SFX mediante su secuencia de eventos. Si una canción cambia, se crea una revisión del fixture y se repiten ambas variantes.
6. Guardar hashes de tuning/SDK/lógica, estados, entradas, recursos y perfil. Implementar rechazo de comparación ante cualquier diferencia no autorizada.

**Ejecutar:** OP04, Q01, P03 y replays L01 pertinentes. **Cerrar:** fixtures completos reproducibles; incluir casos que fuerzan el peor tráfico. **Si M2 no produce replay estable:** volver a la tarea T responsable; no optimizar sobre estado indeterminado.

## O04 Establecer corrección gráfica antes de optimizar

**Depende de:** T06, O02. **Leer:** C2/C8, R01–R05 y discrepancias O00. **Modificar:** `src/render/render_g.*`, `tools/reference_compositor.py`, harness y fixtures de renderer. No modificar física para esconder errores.

1. Confirmar coordenadas lógicas con signo; clipping anterior a conversión a byte. Cada sprite recibe frame, x/y, ancho/alto y anclaje explícitos. El SDK sólo ve rectángulos válidos; la ruta de borde puede ser propia y lenta.
2. Implementar referencia host independiente que decodifica índices de color y compone píxeles. No reutilizar cálculo de direcciones ni bucle del blitter Z80 como única referencia.
3. Resolver avance de líneas CPC para papeles y sprites: probar y=7→8 y cruces de filas. Una suma de 0x800 repetida sin corrección no es algoritmo general de scanline.
4. Ejecutar orden de restaurar todas las cajas antiguas, modificar fondo persistente, dibujar actores y HUD. Si una caja cambió de tamaño, restaurar toda la antigua antes de usar la nueva.
5. Comprobar pausa/retry/cambio de escena, aparición/eliminación y negro opaco frente a transparencia. Registrar bugs de lógica en su tarea T si afectan las pruebas, sin adoptar conducta incorrecta como referencia.
6. Guardar el renderer G correcto y sus checkpoints; ningún test esperado se genera automáticamente desde un resultado Z80 fallido.

**Ejecutar:** OP05/OP06, A01–A03, R01–R05 y B03. **Cerrar:** cero discrepancias de píxel/guardas en dominio soportado. Captura de tearing se registra aparte: no certifica hardware. **Si falla:** reducir a un sprite/una línea/una caja, corregir y volver al caso original.

## O05 Medir la referencia y localizar costes

**Depende de:** O03. **Crear:** `tools/run_benchmark.py`, `tools/summarize_benchmark.py`, baseline inmutable en `research/runs/`, decisión `o05-baseline.md`.

1. Compilar G-base con hashes y mapa; comprobar correspondencia entre DSK cargado y build. Ejecutar primero replays funcionales con checkpoints.
2. Medir tres runs desde reset por fixture y cadencia: simulación/audio nominales 50; presentación objetivo 50 y ensayo separado 25. Usar perfil real, sin turbo ni disco acelerado. No mezclar variantes en el mismo CSV.
3. Medir trabajo, espera, ISR, latencias, deadlines, RAM/pila y cada fase; reportar máximo por clase de evento, no sólo promedio. Conservar datos de las ejecuciones que no cumplen objetivos.
4. Ejecutar versión instrumentada y sin marcas cuando sea necesario; medir el efecto de las marcas, no restarlo silenciosamente. Si no existe método de observación de la versión sin marcas, declarar esa limitación.
5. Ordenar costes por tiempo absoluto y frecuencia. Escribir cuáles de O06–O12 pueden afectar al peor cuadro y cuáles sólo a carga o almacenamiento. Un loop que sólo ocurre al arrancar no es candidato a mejorar FPS.
6. Registrar la decisión de continuar experimentos aunque baseline falle el objetivo; preservar fallos como referencia, sin declararlo apto para release.

**Ejecutar:** OP07, Q01–Q04. **Cerrar:** baseline válido y reproducible, aunque sus deadlines fallen; esos fallos siguen abiertos hasta T20. **Si faltan tiempos:** O05 bloqueada, nunca valores estimados escritos como medición.

## O06 Comparar flags y coste de llamadas

**Depende de:** O05. **Leer:** flags actuales, manual/ayuda de SDCC fijado, wrappers SDK y disassembly real. **Crear:** `cfg/variants.json`, `tools/build_variant.py`, target `build-variant`, decisión `o06-flags.md`.

1. Crear directorio de salida por variante. Copiar G-base y cambiar sólo la política de optimización del módulo seleccionado. Consultar flags soportados; no inventar switches ni cambiar ABI.
2. Comparar compilación actual orientada a tamaño con alternativa orientada a velocidad soportada. Mantener el resto de fuentes y módulos iguales; generar mapa y assembler para inspección.
3. Señalar llamadas pequeñas repetidas y cálculos de dirección dominantes. Probar como máximo una variante adicional de helper integrado o tabla precalculada, separada de la prueba de flags.
4. Medir coste de wrapper C→ASM y primitiva por separado con argumentos representativos; no atribuir el coste del sprite entero a la llamada C.
5. Ejecutar suite funcional pequeña tras cada build; sólo candidatos correctos pasan a tres runs completos. Elegir por la regla de epsilon y presupuesto de RAM.
6. Mantener flags originales si no hay ganancia demostrada. Conservar los informes de variantes rechazadas; no mantener código muerto experimental en release.

**Ejecutar:** OP08/OP17, B02–B04, Q01–Q03. **Cerrar:** `accepted` o `rejected` documentado y configuración activa inequívoca. **Fallo de ABI:** restaurar flags, reducir al test de wrapper y no continuar optimizaciones dependientes de una llamada rota.

## O07 Implementar restauración especializada Z80

**Depende de:** O06. **Leer:** C8/C9, renderer y mapa actuales. **Crear:** `src/render/restore_rect.s`, wrapper en `render_g.*`, fixtures, decisión `o07-restore.md`.

1. Definir wrapper propio con rectángulo ya recortado `(x_byte, y, width_bytes, height)`. Rangos válidos: x 0..79, y 0..199, width/height positivos y extremos dentro de pantalla. Cero o rectángulo vacío retorna sin escribir.
2. Documentar ABI desde el assembler que genera SDCC y convenios reales, registros preservados, flags destruidos, SP y banco requerido. Fuente es fondo limpio RAM1 en C0; destino vídeo RAM3. Wrapper conserva banco e interrupciones según C9.
3. Primera versión: tabla de 200 offsets de 16 bits (400 B en RAM fija, contabilizados). Offset = `(y & 7)*0x800 + (y >> 3)*80`; sumar bases y x. Copiar sólo width bytes por línea. Nunca usar BC=0 con una instrucción de copia repetida.
4. Comparar loop de copia y LDIR para anchos representativos 2/8/9/80; elegir una implementación simple por evidencia. No desenrollar 80 casos a priori ni usar SP como destino.
5. Para cada llamada medir bytes escritos, guardas, SP antes/después y banco restaurado. Interrumpir durante el loop con ISR real. Recorte sigue siendo responsabilidad verificada del wrapper.
6. Medir ruta aislada y el fixture completo. Si la tabla no cabe o no compensa, conservar implementación previa; registrar que C→ASM no garantiza ganancia.

**Ejecutar:** OP09/OP17, R01–R04, K02, B03, Q01–Q03. **Cerrar:** exactitud byte a byte y decisión con coste de tabla/código incluidos. **Si falla cruce Y:** caso mínimo con una línea antes y después del salto de carácter.

## O08 Separar invalidación de fondo y HUD

**Depende de:** O07. **Modificar:** `src/render/dirty.*`, `render_g.*`, pruebas; mantener restore seleccionado por O07. **Crear:** decisión `o08-dirty.md`.

1. Añadir versiones independientes de fondo persistente, HUD y lista de actores. Un cambio de score invalida sólo su campo/área; no reconstruye el escenario.
2. Mantener lista de cajas anteriores por actor visible, aunque no se mueva. Una pose o tinta que cambia exige dibujo. Primera optimización conserva dibujado de todos los actores después de restaurar; evita optimizar dos problemas a la vez.
3. Crear lista acotada inicial de 32 rectángulos con coordenadas con signo y límites validados. Guardar su RAM real. Si se supera, fallback correcto y contador; no descartar regiones silenciosamente. El caso de gameplay aceptado debe tener contador de overflow cero.
4. Unir sólo rectángulos que se solapen si el área envolvente no supera la suma de sus áreas; conservar separados los otros. Usar área en bytes de pantalla, sin mezclar píxeles Mode 0. No prometer que la heurística sea óptima.
5. Al cambiar una máquina, actualizar fondo limpio y marcar región persistente. Restaurar todas las regiones antes de redibujar actores; el HUD se compone al final. Retry recompone fondo inicial y vacía listas.
6. Comparar G-restore y G-dirty. Para futura comparación H, el baseline genérico debe tener **la misma invalidación**; la ganancia de HUD se informa separada de sprites compilados.

**Ejecutar:** OP10, R02–R04, F05, Q01–Q03. **Cerrar:** mismas imágenes y estados; ahorro medido o cambio rechazado. **Si overflow sólo en estrés artificial:** reportar fallback y coste, no declarar cumplido el gate de ese estrés.

## O09 Crear generador determinista de sprites especializados

**Depende de:** O08. **Leer:** formato real de máscaras y generador existente; C8. **Crear:** `tools/compile_sprites.py`, `tests/host/test_compile_sprites.py`, manifiesto de selección y outputs sólo en build.

1. Seleccionar primero una pose de Pitu, dos direcciones y dos alineaciones ya disponibles. No inventar nuevas poses ni cambiar la imagen para facilitar el algoritmo.
2. Decodificar cada pareja `(mask, pixel)` y validar `(pixel & mask)==0`. Clasificar máscara FF como transparente, 00 como opaca y resto como parcial. Operación equivalente: `(background & mask) | pixel`.
3. Generar representación intermedia por línea: saltos, escrituras opacas y mezcla parcial. Saltar bytes transparentes sin leer/escribir fondo; escribir opacos sin lectura; parciales conservan bits. Negro opaco es escritura de cero, no salto.
4. Emitir un modelo host del plan de operaciones y demostrar equivalencia para 256 valores de fondo por pareja. Añadir máscaras válidas sintéticas, frame vacío/opaco, límites y entradas inválidas.
5. Emitir `.s` de SDAS con entrada de dirección de primera línea y resolución correcta de siguientes líneas para **cualquier fase Y válida**. Empezar sin automodificación; instrucción y avance de puntero explícitos. No conservar el error de incrementar siempre 0x800.
6. Emitir descriptor (frame ID, bank, entry offset, width, height, source hash), manifest de bytes estimados y comprobar después tamaño ensamblado. Dos invocaciones con las mismas entradas deben producir bytes idénticos. Prohibir rutas absolutas/fechas en código generado.

**Ejecutar:** OP11. **Cerrar:** equivalencia del modelo y ensamblado sin errores; aún no declarar el blitter Z80 correcto ni más rápido. **Si el código supera la reserva:** producir diagnóstico de tamaño y reducir sólo selección de variantes, conservando fallback G y arte.

## O10 Ejecutar sprites compilados y fallback en CPC

**Depende de:** O09. **Crear:** `src/render/render_h.*`, wrappers, harness de ABI y target `test-compiled-sprites`; decisión `o10-sprites.md`.

1. Enlazar pose especializada en región explícita; comprobar mapa y dirección de entrada real. Invocar desde wrapper único cuya ABI se verifica con B02.
2. Dispatcher: pose compilada residente, generación válida y rectángulo totalmente visible → H; cualquier clipping/pose ausente → G. Rechazar descriptor corrupto antes de saltar a código. No recortar después de llamar H.
3. Ejecutar H y G con todas las fases Y, X pares/impares, direcciones y fondos sintéticos. Comparar VRAM con oráculo por píxeles, SP y registros conservados; canarios antes/después de código y datos.
4. Probar llamada con ISR activa, dirección de pantalla cerca de cambio de bloque y retorno al banco anterior. No insertar DI largo para ocultar corrupción.
5. Medir H-pitu frente a G-dirty con exactamente el mismo restore, HUD, audio y scheduler. Publicar tamaño agregado del código frente a datos; incluir fallback y dispatcher en tiempos.
6. Sólo si aporta mejora y cabe, ampliar a la segunda pose y Alberto en subpasos separados. Cada ampliación repite casos OP12 y medidas afectadas. No compilar automáticamente todos los frames del reparto.

**Ejecutar:** OP12/OP17, R01–R05, B02/B03, K02, Q01–Q04. **Cerrar:** decisión aceptada/rechazada con resultados del Z80, no sólo del modelo Python. **Si falla:** una pose, un fondo y una posición; desactivar únicamente H en la selección hasta corregir.

## O11 Optimizar residencia y uso de bancos

**Depende de:** O10, T05. **Leer:** C9, mapa enlazado real, manifest de recursos, candidatas A/B. **Crear:** `tools/check_residency.py`, `cfg/residency.json`, decisión `o11-residency.md`; modificar empaquetado residente y accesos sin cambiar imágenes.

1. Enumerar por fase `boot`, `play`, `retry`, `transition`: código, datos, comprimidos, variantes, fondo, vídeo, stack, scratch, guardas y padding. Para cada objeto: banco físico, offset, longitud, alineación, vida y dependencia. Mapear secciones SDK también.
2. Mantener fondo RAM1 y vídeo RAM3 en A; pila/ISR/trampolines fuera de la ventana. Si no cabe una reserva, fallar con objeto/bytes; no utilizar guardas ni los 256 B libres de pila.
3. Colocar código H y datos por actor/uso. Durante ejecución de un blitter en banco no paginar otra fuente ni llamar una función oculta. ISR no toca recursos paginados. Ningún puntero de ventana sobrevive a la operación.
4. Reducir selecciones redundantes dentro del orden de dibujo permitido. No reagrupar actores por banco si cambia su orden visual en solapes. Cachear sólo configuración comprobada y restaurar el estado del llamador.
5. Comparar variantes precalculadas en build y generadas durante carga para un conjunto acotado. Medir RAM pico y transición; en PLAY todas las variantes usadas deben estar listas. Un ahorro en disco puede no ahorrar RAM.
6. Ejecutar 10.000 cambios con ISR y llamadas H/G mezcladas; probar handles caducados, rangos y errores. Medir selección + restauración incluidas en el cuadro completo.

**Ejecutar:** OP13, K01–K03, B03, Q02/Q03. **Cerrar:** mapa físico real sin solapes y política de residencia aceptada; también es válido rechazar una agrupación que no compensa. **Si colisiona con memoria A:** registrar alternativas antes de O13, sin activar B de forma implícita.

## O12 Integrar control, audio y costes de simulación

**Depende de:** O11, T17. **Leer:** C1/C3/C4/C6/C10 y código real de clock/input/audio/sim. **Modificar:** sólo módulos que el perfil O05 identifique; decisión `o12-scheduler-audio.md`.

1. Ejecutar A-selected con música y SFX reales. Confirmar tick fijo y captura de flancos de T04, sin multiplicar velocidad al variar presentación. No crear otro reloj paralelo.
2. Medir ISR/AY/PPI y secciones críticas; verificar que teclado y player no intercalan accesos. Interrupciones conservan registros y estado previo; ningún banco/loader dentro de ISR.
3. Medir por tick entrada→estado, evento→servicio AY y estado→presentación. A 25 Hz publicar retraso adicional visible; el input muestreado a 50 Hz no garantiza imagen a 50 Hz.
4. Si la simulación domina, elegir una sola operación frecuente y optimizarla en C primero: tabla/constante, rango probado, eliminación de trabajo duplicado. Mantener barridos y desempates. Probar extremos/overflow; no sustituir el barrido por colisión de posición final.
5. Si aún merece ASM, crear ficha local de wrapper/ABI y casos de equivalencia antes de escribirlo. Usar mismos estados host/Z80; tamaños de entero explícitos. No reescribir toda la IA.
6. Ejecutar 12.000 ticks incluyendo peor tick musical, saturación SFX, cambios de HUD y sprites superpuestos; escuchar/capturar sonido. Reportar jitter y ticks omitidos. Si gate falla, conservar reproducción para T20.

**Ejecutar:** OP14/OP17, P01–P04, U01–U04, S/D/F afectados, Q02/Q04. **Cerrar:** integración verificada e informe; los incumplimientos de rendimiento no se esconden y bloquean selección final T20. **No aceptar:** audio omitido, ticks descartados o colisiones simplificadas para ganar benchmark.

## O13 Resolver pantalla única frente a doble búfer

**Depende de:** O12. **Leer:** R05, candidatas A/B y mapa real. **Crear:** decisión `o13-presentation.md`. **Condicional:** perfil `B-trial`, memoria y renderer por página.

1. Capturar A-selected en movimiento vertical/horizontal, cruces, HUD y máximo tráfico a velocidad real. Inspeccionar scanout además del framebuffer final. Registrar límites del método y resultado por CRTC disponible.
2. Si A cumple calidad observada y gates, cerrar `outcome: not_needed` con evidencia: no implementar doble búfer por obligación. La prueba física sigue en T34.
3. Si hay tearing/parpadeo reproducible, evaluar mapa B con secciones reales: RAM2 deja de poder alojar lógica porque será vídeo. Crear presupuesto alternativo antes de mover código. Si no cabe, documentar el fallo y elevar decisión de memoria; no simular B dentro de reservas A.
4. Si B cabe, mantener por página lista de regiones antiguas y versión de fondo/HUD. Restaurar la página oculta según lo que se dibujó allí dos presentaciones antes, luego dibujar estado nuevo y cambiar página sólo en frontera verificada.
5. Ejecutar secuencia que modifica máquina/HUD en un frame impar y los observa en ambos buffers, elimina actor, pausa y retry. No copiar 16 KiB de una página a otra cada cuadro.
6. Comparar A/B con la misma carga, cadencia, lógica/audio; contabilizar banco, presentación, transición y RAM. Elegir B sólo si la ganancia visual justifica coste y conserva los gates. Si requiere reducir cadencia, preparar build y revisión H2; no aprobarlo automáticamente.

**Ejecutar:** OP15, R01–R05, B03, Q01–Q04. **Cerrar:** decisión comprobada o rechazo del ensayo con causa; un problema visual sin solución mantiene T20 bloqueada. **Si cambia mapa/loader:** llevar restricciones a T21–T24 y volver a comprobarlas en O15.

## O14 Publicar comparación y elegir candidatos

**Depende de:** O13. **Crear:** `tools/compare_benchmarks.py`, `research/reports/optimization-comparison.md`, decisión `o14-candidates.md`.

1. Validar igualdad de hashes/entorno y aislar la variable de cada experimento. Rechazar mezcla de audio, escenas, cadencias o perfiles. El cambio de módulo/flags declarado es la única excepción permitida a igualdad de build.
2. Repetir tres runs completos de G-base, genérico con invalidación/restauración elegidas y variante H final, más B si existe. Ejecutar funcionalidad por separado; no reciclar baseline de otra revisión de fixture.
3. Mostrar tabla incremental: flags, restore, HUD/regiones, sprites, bancos, scheduler; peor cuadro, p95/p99, deadlines, latencias, código, datos, RAM pico, stack. Separar beneficios que se solapan; no sumar porcentajes como si fueran independientes.
4. Calcular epsilon y diferencia; cero diferencias gráficas/estado como prerrequisito. Si falló un gate, mostrarlo aunque haya aceleración. Reportar estrés y M2 por separado.
5. Comparar fixture heredado con dominio compartido y límites O01. Sólo afirmar «más rápido que el primero en X» si el ensayo equivalente se ejecutó. FPS de juegos distintos y registros históricos se presentan como contextos distintos.
6. Entregar candidatos y regresiones pendientes a T19. T19 verifica evidencia y T20 congela arquitectura/cadencia. No cambiar `hardware_verified` ni H2.

**Ejecutar:** OP16/OP17, Q01–Q04. **Cerrar:** reporte reproducible que puede concluir que una optimización no compensa. **Si comparación inválida:** fallar, corregir la procedencia y repetir las variantes afectadas; no suprimir el campo que detectó diferencia.

## O15 Comparar compresión y tiempo total de transición

**Depende de:** T20, T22, T24. **Leer:** C9/C11, manifiesto y loader real; decisiones O11/O13. **Crear:** `make bench-loads`, corpus real y decisión `o15-compression.md`.

1. Seleccionar fondo, sprites, tiles, mapa y audio de los paquetes implementados; raw, repetitivo e incomprimible. Usar los mismos bloques, límites y checksums para todos los codecs. No comparar una concatenación grande con bloques pequeños de otro codec.
2. Generar builds separados raw y ZX0, añadir LZSA sólo mediante integración aislada con procedencia, límites y pruebas de decoder. Un codec no probado queda «no evaluado»; no ganador/perdedor.
3. Medir archivo/sectores reales, código del decoder/validador, scratch, pico de expansión, profundidad de pila, lectura, validación, descompresión, variantes, composición y primer cuadro jugable. No elegir por bytes comprimidos exclusivamente.
4. Ejecutar corrupción/truncado/rango de C06. El decoder ZX0 pequeño existente no se asume seguro ante datos dañados: cumplir el validador con límites o decoder acotado de T22 antes de escribir destinos.
5. Medir cargas frías/calientes a velocidad real; operaciones y reintentos etiquetados. Comprobar 100 cargas alternadas y errores del loader del plan, reutilizando evidencia válida de la misma revisión si existe.
6. Elegir raw o un codec por política del packer; la selección puede variar por recurso si formato/loader lo permite. Mantener reintentos de partida sin FDC; las pausas de carga/audio se informan aparte de FPS.

**Ejecutar:** OP18, C01–C07, O03/O05/O08/O09 de TESTS, B03. **Cerrar:** política y tiempos Z80/sectores reales con memoria completa. Si no se cumple objetivo de carga, documentar medidas y corrección antes de T25; no anunciar «carga rápida» a partir del ratio.

## O16 Cerrar regresión y preparar evidencia final

**Depende de:** T33, O15. **Crear:** `make verify-performance`, `research/reports/performance-final.md`, paquete de pruebas físicas y matriz de entorno.

1. Seleccionar build final congelado de campaña. Identificar mediante perfil la escena con mayor coste real; si supera M2, crear fixture adicional y repetir comparación afectada. M2 continúa como regresión histórica.
2. Ejecutar suites de T33 y OP19/OP20; reutilizar resultados únicamente con hashes/configuración idénticos. Medir control/audio/render/cargas/pila del candidato completo, no sólo microbenchmarks.
3. Segundo emulador: verificar perfiles soportados y ROM/CRTC, ejecutar arranque, bancos, renderer, sonido y loader; registrar discrepancias. CRTC clásico 0/1/2 y 4 cuando esté disponible; Plus/CRTC3 en columna separada opcional.
4. Preparar para T34 BIN/DSK, hashes, controles, casos de tearing, instrucciones de carga fría/caliente y formulario. Distinguir disquetera original y emulador de disquetera. No afirmar pruebas físicas ejecutadas.
5. Publicar prestaciones medidas, entorno, peor caso, límites de actores/poses, tiempos de transición, pendientes y optimizaciones rechazadas. No usar «máximo absoluto del CPC» como criterio de cierre.
6. T35 empaqueta candidato de emulación con pendientes explícitos; sólo T34 puede habilitar `hardware_verified`. Si un cambio final toca ISR/bancos/renderer, invalidar las evidencias afectadas y repetir sus gates.

**Ejecutar:** OP19/OP20, B04, Q/R/U/O/Z pertinentes. **Cerrar:** evidencia de emulación completa para los perfiles requeridos disponibles y paquete físico preparado; faltas de cobertura declaradas. Fallos críticos reproducibles bloquean release. Hardware ausente no se convierte en PASS ni bloquea preparar la entrega de emulación.
