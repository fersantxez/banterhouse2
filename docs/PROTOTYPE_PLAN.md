# Plan de prototipos

> Nota de archivo. Algunas propuestas de este documento se descartaron o siguen pendientes. Consulta el [estado actual](STATUS.md).

Propuesta del 10 de octubre de 2026. En esa fecha estaban terminadas las pruebas del ordenador descritas en [research](../research/README.md), pero faltaba implementar estos prototipos en CPC.

Secuencia operativa detallada: [plan de implementación y pruebas](IMPLEMENTATION_PLAN.md), con tareas, contratos, casos y seguimiento para el modelo ejecutor. Este documento conserva la especificación de los experimentos y las alternativas técnicas.

## Objetivo de las pruebas

La [dirección creativa actualizada](CREATIVE_DIRECTION.md) prevalece: reglas nuevas, control inmediato, ritmo y diversión, con ambición gráfica y artística. Antes de comparar renderers, encontrar una interacción que resulte satisfactoria jugando. No se heredan la campaña, la oficina, el HUD, la cámara ni el tamaño de personajes del primer juego.

## Fase 0: microprototipos jugables

La propuesta actual es [Banterhouse 2 — ¡Devuelto!](GAME_DESIGN.md). Concentrar la prueba en sus tres pasos, sin producir tres juegos distintos:

| Paso | Contenido | Evidencia jugable buscada |
|---|---|---|
| M0 | Movimiento, salto libre, apoyos, cinco marcas de recorrido y SFX | Control predecible y ganas de repetir el recorrido |
| M1 | Una máquina que emite papel, gesto de devolución, impacto y reintento | Gesto comprensible y satisfactorio, sin espera dominante |
| M2 | Tres máquinas, un perseguidor, dos rutas y un panel de rebote opcional | Decisiones durante el movimiento y varias maneras de resolver |

Los valores de física, ventanas y cadencias del diseño son puntos de partida. Para M1 comparar dos ventanas y dos cadencias cambiando una variable cada vez. Si el núcleo exige esperar o machacar acción quieto, corregirlo o reconsiderar la mecánica antes de producir campaña. Las alternativas anteriores permanecen en la dirección creativa como reserva.

Ajustar aceleración, frenado, cambio de dirección y, si hay salto, arco, control aéreo, aterrizaje y tolerancias de entrada. Las tolerancias son parámetros a probar, no mejoras universales. Evitar que animaciones decorativas retrasen la acción. Diseñar sonidos breves de acción, éxito y peligro con prioridades que mantengan la claridad durante la música.

Registrar observaciones de partidas reales: comprensión de controles, fallos que parecen injustos, decisiones que cambian entre intentos y deseo de repetir. No inferir diversión de telemetría ni inventar pruebas con jugadores. Construir una muestra artística exigente de M2 si las partidas sostienen el concepto; volver a evaluar control y legibilidad con ella.

Medir entrada→cambio de estado, entrada→primer cambio visible y entrada→sonido. Registrar mediana, p95 y máximo, con configuración de teclado/joystick, emulador y buffers de audio/vídeo. No confundir lectura a 50 Hz con latencia de presentación, ni tiempo de simulación con latencia física extremo a extremo. Buscar presentación a 50 Hz como objetivo inicial, sin prometerla. Una alternativa a 25 Hz requiere evaluar jugando sus consecuencias; no se aprueba automáticamente por mostrar más detalle.

Salida de esta fase: bucle jugable candidato, reglas/control descritos, evaluación real pendiente o realizada explícitamente y una carga visual representativa. La elección de arquitectura se hará después de probarlo.

## Prueba de paquetes antes de producir campaña

El [plan de disco](DISK_CONTENT_PLAN.md) propone cinco arenas residentes y un encuentro sustituible por capítulo. Tras M2, implementar dos arenas que compartan recursos, un paquete de encuentro y una viñeta; validar transiciones, reintento sin acceso FDC y recuperación ante cara incorrecta o carga fallida. Registrar pico de RAM, stack, tiempos de carga y expansión. La [historia](STORY_STRUCTURE.md) y las cuotas de disco siguen siendo propuestas hasta completar ese ensayo con recursos reales.

## Fase 1: comparación técnica de una escena representativa

La ejecución detallada de esta fase está en [Optimización para Luna](implementation/OPTIMIZATION_PLAN.md), tareas O01–O14. Su STATUS compartido gobierna el orden y evita repetir experimentos. Este documento conserva el fundamento y los fixtures de investigación.

Una vez elegida la dirección jugable, congelar una escena que la represente y comparar primitivas genéricas, renderer híbrido y especializado. Pantalla única, doble búfer y scroll son candidatos según la cámara y el movimiento necesarios. La comparación debe preservar el comportamiento y la respuesta de control.

La escena candidata nueva es M2: Pitu, un perseguidor, tres máquinas con avisos y cambios de estado, hasta cuatro proyectiles, un panel, plataformas y feedback de impactos. Congelar sus recursos y recorrido sólo después de probar las reglas; revisar los presupuestos de memoria con esos tamaños reales.

La siguiente escena de oficina se conserva como **fixture técnico heredado**, útil para comprobar rutinas y contrastar resultados anteriores. No constituye una decisión sobre el juego final, y se sustituirá o complementará con la escena surgida de la fase 0.

Una habitación Mode 0 estándar de 160×200, HUD superior de 16 líneas y zona jugable de 184. Pitu y tres actores de 16×32; dos efectos de 4×8; dos muebles de oclusión; un objeto persistente que desaparece; un elemento de decorado animado. Seis poses iniciales compartidas o seleccionadas con presupuesto, dos direcciones, y dos alineaciones cuando quepan. Añadir ocho poses como escalón de contenido, no como obligación que se oculte si desborda.

Congelar PNG/indexado, máscaras, paleta, colisiones, trayectorias, semillas, música, secuencia SFX y entrada grabada. Publicar SHA256 de cada archivo. Todos los renderers producen los mismos píxeles y actualizan los mismos actores incluso cuando no se vean completamente. Recorte y orden Z idénticos. No permitir que una variante gane reduciendo colores, poses o audio sin reportarla como otra escena.

| Variante | Qué cambia | Qué se mantiene |
|---|---|---|
| G: genérica CPCTelera | Sprite enmascarado genérico y primitivas existentes; invalidación corregida por región | Scheduler, lógica, música, fondo, recursos, reglas de clipping y loader compartidos |
| H: híbrida | Frames frecuentes especializados, fallback genérico para objetos o recorte complicado | Mismo resto del sistema y mismos recursos visuales |
| S: especializada Z80 | Generación de sprites/recorridos y manejo gráfico de regiones específico | Scheduler, simulación, loader y audio de G/H para aislar la diferencia gráfica |

Además, capturar G0 con invalidación histórica completa por cambios de HUD, sólo como diagnóstico. **No usar G0 como único adversario de H/S**: atribuiría a «sprites compilados» una ganancia de invalidación. Comparar G/H/S primero en A, después G/H/S en B si el núcleo cabe. Si S necesita otro scheduler/ABI, crear una prueba separada y describir exactamente la variable adicional.

Comparar a simulación fija de 50 ticks/s, audio a 50 ticks/s y presentación objetivo de 50 o 25 Hz. La misma trayectoria se evalúa por tick de simulación; al bajar render se presenta cada dos ticks. La velocidad del juego no cambia por dibujar menos veces. Evaluación z88dk/cpcrslib posterior y acotada con los mismos datos/contratos, sin migrar campaña.

El pasillo con scroll es otro fixture técnico, sin preferencia de cámara para el diseño final: mismos actores, arte comparable, música y efectos. No comparar el tiempo de un scroll vacío con una habitación llena. Antes de arte definitivo, verificar envoltura del buffer y HUD con patrones de diagnóstico.

## Secuencia determinista

La lista siguiente corresponde al fixture heredado. Para M2 sustituir sus contadores de carga/café/mensaje por máquinas pendientes, impactos y puntuación; incluir devolución y daño simultáneos, colisión barrida, rebote, saturación de cuatro proyectiles, última máquina apagada y reinicio. Mantener los casos gráficos y de audio pertinentes.

Guardar 12.000 ticks de simulación (4 minutos nominales a 50 Hz), tras 250 de calentamiento identificados. Repetir tres veces desde reset limpio. Si un deadline falla, el tiempo de pared puede crecer y debe constar. Muestrear al menos estos casos y publicar máximos por clase:

1. Actores separados, sin cambios de HUD: mejor caso estable.
2. Cuatro actores cruzándose, efectos y primer plano: oclusión y restauración.
3. Cambio simultáneo de puntuación, carga, café y mensaje: invalidación.
4. Clipping por cada borde, coordenadas pares/impares, salto entre las ocho fases `y & 7` y entre filas de carácter.
5. Cambio de pose y dirección con anchos distintos y eliminación/reaparición de actor.
6. Alternancia de escenas y vuelta a la anterior: recursos y generaciones.
7. Peor tick musical, SFX con prioridad y lectura de controles simultánea.
8. Para C: cámara en ambos sentidos, envoltura, entrada de columna/fila y actor en borde durante split.

No agregar cargas de segundos al p99 de cuadros para diluirlas ni retirarlas sin etiqueta: publicar métricas de gameplay, transición y disco separadas y además duración total del recorrido.

## Instrumentación y evidencia guardada

- Marcas por fase (restauración, dibujo, HUD, simulación, audio, bancos, FDC, decoder), contador de cuadros, ticks y deadlines perdidos. Medir overhead con build equivalente sin marcas; no restarlo silenciosamente.
- Contador de ciclos/timestamps de emulador con identificación de versión, ROMs, modelo, CRTC, velocidad 100%, turbo/fast disk desactivados y configuración guardada. Tiempo de pared host sólo como dato auxiliar.
- Volcado de pantalla y estado por puntos de control; comparación contra compositor de referencia por píxel. No basta CRC de pantalla si el renderer falló igual en todas las variantes.
- Captura de secuencia para tearing, parpadeo y glitches de paleta/split. Un framebuffer correcto al final del cuadro no demuestra que el barrido fuera limpio.
- Mapa de linker y manifiesto de cada banco: código, datos, comprimidos, scratch, padding, pila y hueco restante. Medir pila rellenándola con patrón antes de ejecutar y con guardas; incluir profundidad de ISR sobre llamada profunda.
- Trazas de audio: número de ticks, intervalos y mayor hueco; escuchar música+SFX y registrar selección de canal. No llamar al AY/PPI concurrentemente sin un contrato.
- Registro de disco por operación: motor frío/caliente, seek, primer byte, último byte, CRC, depack, composición, primera presentación; ST0/ST1/ST2, reintentos y fallos.

CSV propuesto: `run_id,variant,scene,frame,sim_tick,crtc,frame_us,restore_us,draw_us,hud_us,audio_us,bank_us,missed_deadline,stack_used_bytes,dirty_bytes`. En paralelo `loads.csv`: `run_id,volume,resource,bytes_packed,bytes_raw,motor_state,seek_from,seek_to,read_us,depack_us,compose_us,total_us,retries,status`. Campos sin medición quedan vacíos/null, nunca 0.

## Criterios de aceptación propuestos

| Área | Gate del prototipo |
|---|---|
| Jugabilidad | Evaluación real del control, claridad del fallo, decisiones y ganas de repetir. Registrar observaciones y ajustes; el resultado permanece pendiente hasta jugarlo |
| Respuesta | Registrar latencias entrada→estado/imagen/sonido y rapidez del reintento; comprobar que arte, animaciones y carga máxima no degradan perceptiblemente el control |
| Imagen | 0 diferencias no explicadas frente a referencia en checkpoints y 0 restos de sprite/oclusiones incorrectas; sin glitches observados en captura/hardware |
| Tiempo | Publicar mínimo, mediana, p95, p99 y **máximo** con identificador del peor cuadro. 0 deadlines perdidos en recorrido objetivo. Deseable ≤80% del periodo real en peor caso, incluidos ISR/bancos. Si falla, revisar algoritmo y coste visual; evaluar a 25 Hz como alternativa explícita cuya respuesta debe probarse jugando, nunca como aprobación automática |
| RAM | Ningún solape ni banco >16.384 B. El conjunto simultáneo cabe, incluidos formatos comprimidos y expandidos durante carga. No contar ventanas como RAM adicional |
| Pila | Guardas intactas; al menos 256 B de los 768 B reservados sin usar tras todos los casos, incluido IRQ sobre el camino profundo. Si usa SP para dibujar, medir ese camino aparte |
| Audio | 50 ticks/s nominales en gameplay independientemente de render; 0 ticks omitidos, publicar jitter máximo. Pausa de carga explícita aceptada en primera fase; audio continuo requiere su gate propio |
| Disco | 100 cargas alternadas y 10 arranques con motor frío por configuración ensayada; contenido idéntico tras CRC. Reintentos acotados, salida recuperable ante ausencia de sector, CRC inválido, cara equivocada y medio retirado |
| Cargas | Primero registrar distribución real. Objetivo de experiencia inicial ≤2 s caliente para paquete de 16 KiB, pendiente de evidencia; si falla, ajustar tamaño/zona/transición, no falsear cronómetro. Motor frío y cambio humano de cara se reportan aparte |
| Compatibilidad | Baseline estándar probado en CRTC 0/1/2 y 4 cuando disponible; efectos avanzados tienen suite independiente. CRTC 3, Plus y expansiones en columnas opcionales |
| Reproducibilidad | Dos builds limpios con toolchain fijada producen mismos binarios/DSK. Un tercero puede repetir el ensayo usando README, hashes y entradas |

Los números de recorridos, margen y carga son criterios de proyecto propuestos; no prestaciones demostradas. Fallar un gate aporta información para escoger arquitectura. El registro debe mostrar también resultados fallidos, no sólo la mejor captura.

## Matriz de validación y límites

| Entorno | Ensayo | Estado hoy |
|---|---|---|
| Host Python/Clang | Aritmética, máscaras, compresión/round-trip, hashes | Ejecutado; ver research |
| Caprice32 Mac | Gameplay determinista, memoria/guardas, bancos y FDC sin atajos | Pendiente; binario localizado, no lanzado aquí |
| ACE-DL | Tiempos/CRTC, traza de bancos, memoria y verificación independiente | Descarga/documentación disponible; ejecución pendiente |
| Segundo emulador | Casos que discrepen y configuraciones CRTCs disponibles | Pendiente; no afirmar que todos los emuladores implementan todos los tipos |
| CPC 6128 clásico físico, 128K, unidad 3 pulgadas | Arranque, gameplay, scanout, audio, cargas/fallos y varias unidades si es posible | No disponible en sesión; imprescindible antes de certificar compatibilidad |
| CPC clásico ASIC/CRTC 4 | Cobertura complementaria de clásico | Pendiente |
| Plus/CRTC 3, Gotek/HxC, M4, RAM ampliada | Regresión opcional | No sustituyen al equipo objetivo |

Si sólo hay un CRTC físico, registrar el que se probó y dejar otros pendientes aunque pasen emulación. Si el split falla en algún tipo, ofrecer baseline estándar sin ese efecto o resolverlo antes de producir contenido dependiente. No presentar detección de CRTC como garantía automática de compatibilidad.

## Disco y errores: plan específico

Crear dos zonas pequeñas con actores y música compartidos, más una tercera que fuerce sustitución de caché. El volumen contiene magic/version/build-id, geometría esperada, tabla generada de sectores, tamaños, CRC y dependencias. Probar regreso y handles caducados. Inyectar disco incorrecto, recurso truncado, cabecera corrupta y sector ausente en **copias** del DSK.

Primero carga bloqueante sin promesa de música. Después experimento separado: música en ventanas seguras entre comandos/datos; log de intervalos y reintentos comparado contra carga sin música. Cualquier ISR que cause overrun invalida el ensayo aunque la política de retries consiga terminar. Medir retrasos perceptibles y throughput de extremo a extremo, no sólo bytes transferidos.

No reutilizar el contrato atómico del gestor original hasta demostrar staging/commit. Si un banco se ha escrito parcialmente, marcarlo inválido y no devolver un handle anterior que parezca válido. La pantalla de error y reintento vive en núcleo/reservas que el loader no sobrescribe.

## Trabajo priorizado

| Prioridad | Trabajo acotado | Evidencia para cerrar |
|---|---|---|
| P0 inicial | M0 movimiento, M1 devolución y M2 combinación de ¡Devuelto!, con SFX | Partidas reales, observaciones y ajustes; descartar el núcleo si espera o repetición estática dominan |
| P0 inicial | Muestra artística de la dirección seleccionada | Legibilidad y respuesta conservadas al añadir arte, animación y efectos; revisión jugando |
| P0 | Congelar toolchain, ABI y bootstrap de Banterhouse 2 en esta carpeta; fijar perfil 6128 128K | DSK mínimo arrancable, mapa real, ISR y guardas; no tocar la campaña original |
| P0 | Crear escena/corpus del juego seleccionado y compositor host; ajustar reservas al contenido necesario | Manifiesto visual y memoria, preview CPC, clipping de referencia |
| P0 | G con invalidación de HUD/objetos separada y trazas | Baseline medido con audio independiente y peor cuadro identificado |
| P1 | H con generador de sprites sin clipping + fallback genérico | Píxeles idénticos, tamaño real del código y comparación de tiempo; conservar sólo si compensa |
| P1 | B y S como pruebas separadas | Coherencia por página y núcleo enlazado; comparación a igual cadencia |
| P1 | Integrar FDC/paquetes con carga bloqueante y fallos | Latencias reales en emulación, CRC, estado recuperable; hardware pendiente explícito |
| P2 | AKG/AKM y ZX0/LZSA con nuestros recursos | Tamaño total, peor tick y tiempo de descompresión CPC; elegir un formato principal |
| P2 | Ensayo C de scroll/split y pasillo artístico | Wrap sin artefactos, matriz CRTC y coste de bordes/arte; decisión de cámara |
| P2 | Validación física | Modelo/CRTC/unidad/medio identificados, evidencia y fallos documentados |
| P3 | Decisión de arquitectura y pipeline definitivo | Informe comparativo con hashes, datos brutos y razones; entonces ampliar contenido de secuela sobre el bucle jugable validado |

No migrar toda la campaña, comprar herramientas, publicar ni contactar con terceros durante este plan inicial. Mantener una lista de decisiones reversible hasta tener una escena completa y el mapa del linker.
