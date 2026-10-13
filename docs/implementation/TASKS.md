# Tareas de implementación

Ejecutar según dependencias de [STATUS.json](STATUS.json). Las interfaces se crean o reparan en su tarea: algunos targets ya existen como recetas de prototipo, lo cual no demuestra que funcionen. O00 audita esa diferencia antes de implementar. Las tareas O se detallan en [OPTIMIZATION_TASKS.md](OPTIMIZATION_TASKS.md). Las rutas de implementación son destinos previstos, no afirmaciones de archivos existentes. Todos los comandos se ejecutan en `.`. Pruebas definidas en [TESTS.md](TESTS.md); contratos en [CONTRACTS.md](CONTRACTS.md).

En cada tarea: leer los archivos afectados, conservar cambios ajenos, implementar el mínimo, probar, registrar evidencia y actualizar estado. Si la ficha contiene subpasos, usar `substep` para retomarla sin repetir trabajo terminado. El cierre corresponde a todos sus subpasos.

## T01 Fijar herramientas y proteger las referencias

**Depende de:** O00. **Contratos:** C1, C9.

**Crear:** `cfg/toolchain.lock.json`, `tools/doctor.py`, Makefile con `doctor`, `docs/implementation/decisions/001-toolchain.md`.

1. Inventariar SDCC, SDAS/linker, Python, compilador host, SDK CPCTelera, empaquetador DSK y emulador. Verificar ejecutables reales; una ruta en documentación no basta.
2. Empezar con SDCC/SDAS y revisión CPCTelera identificada en investigación; resolver y fijar SHA completo. Dependencias faltantes se obtienen en `tmp/` o `.tools/` de esta secuela, conservando licencias. No cambiar instalaciones globales.
3. Fijar versiones, hashes, flags y ABI. Verificar por separado convención de llamadas de cada API SDK usada. Añadir un programa de prueba de llamada C→ASM como entrada de T02.
4. Copiar configuración de emulador a la secuela. Separar perfil funcional rápido de perfil de tiempos a velocidad real, con audio y sin disco acelerado. No ejecutar runners originales.
5. Registrar hashes de los archivos canónicos leídos y comprobar que el proyecto original no recibió escrituras.

**Probar/cerrar:** `make doctor` ejecuta B01. Tiene que señalar cada dependencia ausente sin decir PASS global. Cierre: toolchain utilizable y comandos de build/emulación documentados; si falta una pieza, dejar T01 bloqueada con alternativa concreta, no cambiar de motor silenciosamente.

## T02 Arranque mínimo y mapa real

**Depende de:** T01. **Contratos:** C1, C9.

**Crear:** `src/platform/boot.s`, `src/platform/platform.h`, `src/main.c`, `cfg/memory.json`, configuración de enlace, `tools/check_link_map.py`; targets `build`, `check-map`, `smoke-boot`, `repro`.

1. Conservar el prototipo auditado por O00 y crear un perfil de arranque mínimo aislado, sin sobreescribir su único fuente/DSK. Generar un binario que tome control desde AMSDOS, establezca pila y Mode 0, muestre una marca de versión y permanezca estable. Sin FDC propio ni juego.
2. Declarar las regiones A y secciones reales. El bootstrap temporal también tiene dirección, tamaño y vida contabilizados. Adaptar sólo la secuencia mínima de un ejemplo auditado; no copiar la campaña original.
3. Desactivar firmware/ROM conforme al stub fijado, inicializar datos/BSS y vectores antes de habilitar interrupciones propias. Probar ida y vuelta de la función ASM de T01.
4. Emitir DSK, binario, símbolos, mapa, hashes y guardas de pila. `check-map` compara secciones reales con reservas; añadir un fixture que desborde para probar el rechazo.

**Probar/cerrar:** B02–B04. Diez resets arrancan; dos builds limpios en directorios distintos coinciden; no solapes. Si el kernel no cabe, registrar mapa y detener la ampliación. No recortar guardas para pasar.

## T03 Importación de arte y galería nativa

**Depende de:** T02. **Contratos:** C2, C8.

**Crear:** `assets/source/canonical/`, manifiesto de procedencia, `tools/export_assets.py`, target `assets-check` y `smoke-gallery`.

1. Congelar copias verificadas de las poses y paletas de `assets/cpc-studies/` con hash de su fuente original. El build posterior no debe depender de reconstruir Banterhouse 1.
2. Importar pantallas raw, paletas, tiles y mapas. Los PNG ampliados son sólo vista previa; no se cuantizan para recuperar el recurso.
3. Validar rangos, tamaños, máscaras y tintas; hacer fallar una paleta de 17 índices, un tile truncado y una máscara inválida.
4. Crear un perfil de arranque por estudio: el bootstrap carga el recurso antes de entregar control al visor. No añadir aún loader dinámico para pasar de una imagen a otra.
5. Obtener VRAM y paleta del emulador y compararlas con la referencia host; capturar también la presentación visible.

**Probar/cerrar:** A01–A03. Las cuatro imágenes corresponden a sus recursos, con sprites y colores originales. Diferencias de señal CRT no se confunden con diferencias de índices de tinta.

## T04 Reloj, entrada e instrumentación mínima

**Depende de:** T02. **Contratos:** C3, C10.

**Crear:** `src/platform/clock.*`, `input.*`, `telemetry.*`, target `test-platform`; perfiles de emulación funcional/timing.

1. Implementar contador de tick, servicio de interrupciones y calibración contra VSYNC. Documentar registros preservados, duración y atomicidad.
2. Leer teclado/joystick y obtener `held/pressed/released`. Dibujar en pantalla de diagnóstico el estado y contadores, sin física.
3. Resolver propiedad del PPI/AY: una sección crítica breve o un servicio único evita escrituras entrelazadas. Mantener el estado previo de interrupciones.
4. Añadir contadores de ticks, presentaciones, retrasos y máximos. Probar presentación cada uno/dos ticks con la misma entrada grabada.
5. El runner exporta estado real mediante capacidades comprobadas del emulador o un puerto de diagnóstico. No inventar opciones CLI; no usar logs voluminosos por frame en la medición de tiempos.

**Probar/cerrar:** P01–P04. Reloj, flancos y wrap correctos; sobrecarga artificial produce error visible/registrado. Si no se pueden extraer ciclos, registrar esa limitación y mantener pendiente el gate de rendimiento.

## T05 API de bancos con guardas

**Depende de:** T04. **Contratos:** C9.

**Crear:** `src/platform/banks.*`, `tests/fixtures/banks/`, target `test-banks`.

1. Implementar selección C0/C4/C5/C6/C7, sombra y restauración. Código, stack y parámetros necesarios viven en RAM fija.
2. Escribir patrones distintos en RAM1 y RAM4–7; leer por banco y verificar que no se mezclan. Proteger vídeo y código.
3. Añadir copia banco→scratch fijo→otro banco con límites y prueba anidada. Ningún puntero paginado escapa de su operación.
4. Interrumpir durante el ensayo con la ISR real. Comprobar configuración y sombra al volver; repetir 10.000 ciclos.

**Probar/cerrar:** K01–K03 en Z80, mapa y guardas intactos. No basta simular un array de ocho bancos en Python. Ante corrupción, reducir a una pareja de bancos antes de integrar sprites.

## T06 Renderer G correcto

**Depende de:** T03, T05. **Contratos:** C8, C9.

**Crear:** `src/render/render_g.*`, conversor de variantes, `tools/reference_compositor.py`, target `test-render`.

1. Generar poses derecha/izquierda, alineadas/desplazadas con anclajes explícitos. Contar bytes expandidos y cargar Pitu en RAM4; fondo limpio en RAM1.
2. Restaurar todas las cajas anteriores antes de dibujar actores actuales. Primera versión puede redibujar todos los actores; no optimizar dirty regions a costa de perder corrección.
3. Implementar clipping en cuatro bordes, transparencia y orden de dibujo. Probar eliminación y cambio de pose con caja distinta.
4. Comparar VRAM tras secuencias contra compositor independiente por píxeles. Incluir Pitu/Alberto cruzados y modificación persistente del fondo.

**Probar/cerrar:** R01–R05; 0 diferencias sin explicar, 0 escrituras fuera de pantalla, guardas intactas. Un screenshot bonito no cierra el test de solapes. Guardar baseline G antes de experimentar H.

## T07 Simulación compartida y colisión estática

**Depende de:** T06. **Contratos:** C1, C2, C4.

**Crear:** `src/core/state.*`, `collision.*`, `tuning.h`, `assets/levels/m0.json`, exportador de niveles, `tests/host/`, target `test-sim`.

1. Definir estado con tamaños fijos, JSON de nivel y exportación binaria versionada. Empezar por suelo, dos plataformas y spawn.
2. Compilar el mismo `src/core/` con compilador host y SDCC. Añadir runner de fixture en Z80 que exporte campos, no structs crudas.
3. Implementar cuerpos, sólidos y apoyos de C2/C4. Añadir overlay debug de cajas y IDs fuera de builds de medida.
4. Probar cuerpos colocados a mano contra bordes, esquinas y plataformas unidireccionales. Crear estados esperados explícitos para casos pequeños.

**Probar/cerrar:** S01–S03. Host y Z80 coinciden, sin overflow ni acceso fuera de tablas. No producir todavía las cinco plataformas de la maqueta por considerarlas ya jugables.

## T08 Movimiento y salto de Pitu

**Depende de:** T07. **Contratos:** C3, C4.

**Cambiar:** `src/core/player.*`, `tuning.h`, nivel M0 y fixtures. Crear `make run-m0`.

1. Implementar mover, frenar, invertir y control aéreo; aplicar el orden de integración especificado.
2. Añadir salto por flanco, corte al soltar, coyote y buffer; probar extremos de cada ventana.
3. Añadir descenso que ignore sólo la plataforma actual. Probar dos apoyos cercanos: debe aterrizar en el segundo.
4. Medir arco discreto, tiempo en aire y alcance en el binario. Ajustar el recorrido para que se pueda completar; registrar tuning y trazas.
5. Colocar cinco marcas de recorrido provisionales, sin campaña ni puntuación definitiva. Comparar aceleración 2 ticks y respuesta inmediata manteniendo lo demás idéntico.

**Probar/cerrar:** S04–S08 y replay a 50/25 presentaciones. Colisiones y estado final deben ser iguales. Una animación no puede retrasar el inicio del salto.

## T09 SFX y reinicio de M0

**Depende de:** T08. **Contratos:** C3, C10.

**Crear:** `src/platform/audio.*`, SFX originales de salto, marca y aterrizaje; `make test-audio`.

1. Implementar cola/selección de efectos y un propietario de AY. Conservar ticks de audio aunque se presente cada dos ticks.
2. Disparar sonidos por evento, sin repetir salto por mantener tecla ni pasos cada frame de animación. Pasos sólo al desplazarse apoyado.
3. Reiniciar el recorrido en RAM; contador de entradas al loader permanece cero durante intentos y reintentos.
4. Medir tick de entrada→estado→petición de sonido y primer frame afectado. Escuchar en perfil con audio activo.

**Probar/cerrar:** U01–U03, S08. Sin crepitación por PPI, saturación de sonidos o bloqueo de movimiento. Una captura con audio dummy no demuestra esta prueba.

## T10 Revisión humana H0 del movimiento

**Depende de:** T09. **Entregar:** DSK M0, controles, hashes y `research/runs/.../playtest-h0.md`.

1. Pedir recorrer las cinco marcas tres veces, cambiar de dirección, saltar corto/largo y bajar una plataforma.
2. Mostrar variantes de aceleración A/B identificadas sin cambiar otras variables. Registrar cuál se prefiere y dónde falla el control.
3. Preguntar si el salto responde cuando se espera, si se entiende cada caída y si apetece repetir. No dirigir la respuesta.
4. Ajustar una variable por iteración y repetir S04–S08/U01 según el cambio. Conservar feedback literal o una paráfrasis identificada.

**Cerrar:** H0 con aprobación explícita del control o decisión concreta de variante. Si nadie ha jugado, T10 sigue pendiente de revisión. No crear M1 para esconder un M0 que no convence.

## T11 Máquina y pool de papel

**Depende de:** T10. **Contratos:** C5.

**Crear:** `src/core/machine.*`, `projectile.*`, `assets/levels/m1.json`, target `run-m1`.

1. Añadir una máquina con posición, boca, dirección, espera y aviso. Mantener carcasa estática; cambiar sólo indicador/boca.
2. Implementar los cuatro slots, reserva antes del aviso y emisión en el tick previsto. Despawn al salir o tocar sólido.
3. Crear prueba de saturación con las tres máquinas, aunque el nivel M1 muestre una. Liberar reservas al apagar/reiniciar.
4. Dibujar hostiles con forma legible a tamaño real y guardar su trayectoria para el test.

**Probar/cerrar:** M01–M03, R03. No aparece papel sin aviso ni se elimina uno existente para hacer sitio. Pool lleno sólo aplaza una oportunidad.

## T12 Devolución y colisión barrida

**Depende de:** T11. **Contratos:** C5, C6.

**Cambiar:** jugador/proyectiles/colisión/eventos; añadir indicación del sello y sonido de éxito.

1. Implementar ventana 6 ticks y recuperación 8, activa desde la pulsación. El gesto no altera velocidades.
2. Resolver barrido relativo, contacto con sello y cambio de propiedad/dirección. Consumir resto de desplazamiento del tick de devolución.
3. Golpear la boca apaga máquina y consume papel. Renderizar cambio persistente en fondo limpio y HUD parcial.
4. Probar antes/dentro/después de ventana, cara opuesta, papel que cruza toda la zona en un paso y dos papeles coincidentes.

**Probar/cerrar:** D01–D05, R04, U02. Los tests fijan prioridad sello/cuerpo y límites exactos. No agrandar invisiblemente el sello para tapar fallos del barrido.

## T13 Daño, finalización, puntos y reintento

**Depende de:** T12. **Contratos:** C6.

**Crear:** `src/game/flow.*`, checkpoint de arena, fixtures de muerte/salida.

1. Añadir dos impactos, invulnerabilidad y estado DEAD. Congelar amenaza al morir; soltar/pulsar acción para reintentar.
2. Puntuación por máquina y restauración de puntos de entrada al morir. Preparar contador por plaza de enemigo para T15.
3. Última máquina: cancelar amenazas, abrir salida y priorizar finalización frente a daño simultáneo como indica C6.
4. Reiniciar 100 veces alternando muerte, salida y reinicio voluntario. Restablecer reservas, timers, poses, fondo, HUD y eventos.

**Probar/cerrar:** F01–F05, R04. 0 accesos de loader/FDC durante reintento; no farmeo de puntos ni daño doble en un tick. Medir latencia del reintento sin presentar el objetivo <1 s como dato si falla.

## T14 Revisión humana H1 de la devolución

**Depende de:** T13. **Entregar:** M1 funcional, formulario H1 y builds A/B.

1. Explicar controles, sin enseñar un vídeo de la solución. Observar cómo se entiende la devolución.
2. Comparar ventana 6 frente a 8 ticks, con recuperación de 8 y todo lo demás fijo; luego cadencia de espera 50 frente a 70, manteniendo la ventana escogida. Registrar qué se cambió.
3. Observar espera, pulsaciones al aire, errores atribuibles a alcance y sensación del impacto. Registrar duración/acciones como datos auxiliares, no prueba de diversión.
4. Ajustar tuning, repetir D/F/U afectados y volver a jugar la versión elegida.

**Cerrar:** H1 cuando el usuario entiende y aprueba la interacción básica. Si domina quedarse quieto esperando o machacar acción, revisar posiciones/cadencia antes de añadir enemigos. Un resultado negativo mantiene abierta T14.

## T15 Alberto como perseguidor

**Depende de:** T14. **Contratos:** C6, C7.

**Crear:** `src/core/enemy.*`, fixtures de aviso, persecución y reaparición.

1. Activar una plaza de enemigo con Alberto canónico. Implementar estados y tiempos de C7; sin pathfinding entre plataformas.
2. Integrar contacto dañino barrido, interrupción por papel devuelto y paso del papel hacia otro objetivo.
3. Aplicar puntos por enemigo con límite de tres cobros por plaza e ID visitado por proyectil. Comprobar múltiples reapariciones.
4. Añadir aviso de entrada y posponer spawn cuando no sea seguro. Al abrir salida, finalizar persecución/reaparición.

**Probar/cerrar:** E01–E04, F01/F04, R02. No giro instantáneo, spawn sobre Pitu, desaparición de papel al apartar enemigo ni puntuación infinita.

## T16 Panel y arena M2 con dos rutas

**Depende de:** T15. **Contratos:** C2, C7.

**Crear:** `src/core/panel.*`, `assets/levels/m2.json`, target `run-m2`.

1. Implementar las ocho combinaciones dirección/orientación, flag de rebote y consumo en segundo panel.
2. Construir una arena de tres máquinas y un Alberto. Reubicar geometría respecto al estudio si el salto lo exige.
3. Conservar una ruta frontal que termine sin panel y otra que use un rebote. Para cada orden viable, comprobar que la última máquina sigue siendo alcanzable por alguna fuente de papel.
4. Grabar una solución frontal y una con panel, desde reset, en el binario CPC. Guardar estados intermedios e inputs.

**Probar/cerrar:** N01–N03, L01 y suites S/D/F/E. Rebotar es opcional para completar M2. Un grafo de plataformas o un bot host no sustituyen esos replays.

## T17 Arte animado y música de la muestra

**Depende de:** T16. **Contratos:** C8–C10. **Subpasos:** T17a poses, T17b SFX/música, T17c integración.

1. Añadir el mínimo de poses necesario para leer caminar, saltar y devolver; proteger las poses canónicas y someter las nuevas a H2. Medir cada variante antes de ampliar el banco.
2. Animar bocas/luces con regiones pequeñas. No convertir carteles, moto o fondo completo en animaciones por defecto.
3. Integrar un player AKG y una pieza/SFX originales cortos; fijar revisión y ABI. Comparar tamaño y peor tick; si falla, aislar la prueba antes de evaluar otro player.
4. Prioridades audio, invulnerabilidad legible, sello vacío/acierto y máquinas apagadas. Contar código del player, música, SFX y scratch en mapa real.
5. Crear target `test-m2` que reúna las regresiones de M2 sin ejecutar todavía pruebas largas de disco.

**Probar/cerrar:** A03, R01–R05, U01–U04 y B03. Sin regresión de colisión por recortar sprites. Conservar un build M2 sin adorno como comparación, con la misma simulación.

## T18 Revisión humana H2 de la muestra completa

**Depende de:** T17. **Entregar:** M2, ambas soluciones reproducibles, mapa real y formulario H2.

1. Jugar al menos tres intentos usando libremente rutas; observar qué se ve y qué se pierde entre color, sonido y movimiento.
2. Preguntar por control, lectura de peligro, utilidad del rebote y deseo de repetir. Comparar con M1 si la nueva carga distrae.
3. Revisar identidad de Pitu/Alberto y poses nuevas a tamaño de juego. La aprobación de los estudios estáticos no aprueba automáticamente animaciones.
4. Corregir el problema dominante y repetir sus tests. No producir más escenarios para compensar una muestra que no funciona.

**Cerrar:** H2 aceptada y problemas críticos resueltos. T19–T20 pueden medir el binario mientras se espera esta revisión; T21 y la producción de contenido no avanzan sin ella.

## T19 Perfil y comparación G frente a H

**Depende de:** T17, O14. **Contratos:** C3, C8, C9.

La implementación y los experimentos detallados se ejecutan en O02–O14. Esta tarea revisa sus resultados; no crea otro benchmark ni un segundo renderer híbrido.

1. Leer `research/reports/optimization-comparison.md` y verificar los hashes de los artefactos citados, fixtures, tres runs y pruebas funcionales.
2. Comprobar que G/H comparten invalidación, restore, scheduler, audio y escena en el ensayo que atribuye ganancias a sprites; que la comparación histórica está separada; y que las variantes rechazadas no se activaron.
3. Verificar Q01–Q04 y R01–R05 de la revisión elegida. Repetir sólo evidencia ausente o invalidada por un cambio; no volver a ejecutar lo idéntico por duplicación del plan.
4. Entregar a T20 candidatos, mapa real, peor cuadro, deadlines, pila, latencias, problemas de presentación y decisión A/B de O13. No exigir un motor S completo.

**Cerrar:** comparación trazable, correcta y con fallos/limitaciones explícitos. Un candidato puede seguir incumpliendo presupuesto; T20 no lo acepta hasta resolverlo. Sin tiempos verificables, T19 queda bloqueada.

## T20 Congelar la arquitectura de la muestra

**Depende de:** T19. **Crear:** decisión `020-runtime.md` y manifiesto de memoria aprobado técnicamente.

1. Elegir G o H con los datos. Mantener A si cumple imagen y margen; registrar ubicación real de cada sección y recurso.
2. Si no cumple, usar primero la evidencia O13/O14 y hacer una única revisión acotada: reducir trabajo redundante; o ensayo B para tearing; o redistribución de región fija. Cada alternativa conserva escena y pruebas. Dividir esa revisión en subtareas antes de tocar el motor.
3. Objetivo de aceptación: cero deadlines perdidos en la carga acordada, peor trabajo ≤80% del periodo real, pila con margen del plan. Cualquier relajación requiere decisión explícita y nueva revisión de respuesta; no se aplica automáticamente 25 Hz.
4. Declarar cadencia elegida, max actores realmente probados y presupuestos de producción. Si requiere cambiar jugabilidad, volver a H2.

**Cerrar:** Q/B/K aprobadas para la variante elegida, o T20 bloqueada con un fallo concreto reproducible. No iniciar loader/campaña sobre una memoria imposible. Las cifras son resultados sólo cuando acompañan binario y trazas.

## T21 Formato de paquetes y packer host

**Depende de:** T18, T20. **Contratos:** C9, C11.

**Crear:** `tools/pack_resources.py`, `docs/implementation/PACK_FORMAT.md`, fixtures binarios, `make test-pack`.

1. Fijar offset/anchura de cabecera/entradas, tipos, codecs, checksum y detección de volumen. Publicar ejemplo mínimo hexadecimal y decoder host independiente.
2. Construir paquete de dos arenas compartidas, otro de encuentro y uno de viñeta; inicialmente usar datos pequeños existentes y raw.
3. Dividir en bloques independientes de entrada/salida ≤4 KiB. Ordenar por vida y banco; emitir pico por transición y dependencias.
4. Rechazar fuera de rango, entradas duplicadas, ciclos/ausencias de dependencias, longitudes falsas y destinos protegidos. Pruebas positivas y negativas.
5. Comparar raw, ZX0 y LZSA en ese corpus, incluyendo overhead de bloques; guardar tiempos host sólo como host.

**Probar/cerrar:** C01–C04. Bytes reproducibles y reconstrucción exacta. El manifiesto debe diferenciar tamaño almacenado, expandido y residente simultáneo.

## T22 Decoder Z80 y validación antes de escribir

**Depende de:** T21. **Contratos:** C9, C11.

**Crear:** `src/platform/depack.*`, target `test-depack`.

1. Ensayar ZX0 y LZSA en builds separados con los mismos bloques; medir decoder + tablas, stack y tiempo Z80. Seleccionar uno y raw para el build principal.
2. Implementar validación acotada del flujo antes de llamar a un decoder sin límites, o decoder con límites. Comprobar input, output y distancia de referencia; no confiar sólo en CRC posterior.
3. Expandir desde scratch fijo a un banco destino, con guardas a ambos lados y sin fuente paginada que desaparezca al cambiar banco.
4. Inyectar truncados y streams malformados, incluso con checksum recalculado. Medir tiempo de validar+expandir, no sólo el bucle de copia.

**Probar/cerrar:** C05–C07, K03. Ningún caso inválido escribe fuera de su región. Si no hay decoder seguro que quepa, mantener raw y revisar almacenamiento con datos; no ocultar el coste.

## T23 FDC bloqueante con errores acotados

**Depende de:** T21, T05. **Contratos:** C11.

**Crear:** `src/platform/disk.*`, generador DSK de laboratorio, `make test-disk`.

1. Auditar/adaptar lectura mínima del laboratorio original o implementación documentada, copiando sólo código necesario y avisos.
2. Leer primero sectores raw conocidos, con patrón y CRC, hacia buffer fijo. Fijar timeouts y tres intentos totales; código de recuperación residente.
3. Crear DSK de ensayo y parser independiente que confirme posición de sectores, header de volumen y archivos. No ejecutar sobre el DSK original.
4. Probar cara incorrecta, disco ausente, sector inexistente y error/truncado en copias. No usar música durante transferencia; rearmar reloj al salir.

**Probar/cerrar:** O01–O04, K03. 100 cargas alternadas y 10 arranques fríos emulados por configuración ensayada; definir cómo se obtuvo estado frío. Si el emulador no simula un fallo, etiquetarlo pendiente, no PASS.

## T24 Transición de paquetes y recuperación

**Depende de:** T22, T23. **Contratos:** C9, C11.

**Crear:** `src/game/package_flow.*`, `src/platform/resources.*`, `make test-transitions`.

1. Implementar la máquina de estados completa con checkpoint fijo e invalidación de handles. No ejecutar código overlay en este alcance.
2. Encadenar FDC→scratch→validación/decoder→destino. El renderer y audio respetan la exclusión de uso del scratch.
3. Componer fondo usando staging entre RAM5 y RAM1, aplicar paleta y activar escena sólo tras verificación completa.
4. Fallar después del primer bloque, del último y antes de COMMIT. Reintentar desde recuperación, sin volver a la escena parcialmente cargada.
5. Probar handles caducados y retorno al menú mínimo. Las tablas/strings usadas para error sobreviven al reemplazo del paquete.

**Probar/cerrar:** O05–O08, C/K y B03. Estado fijo conservado, 0 accesos a datos invalidados, guardas y pico de memoria verificados.

## T25 Muestra de dos arenas y encuentro con disco

**Depende de:** T24, O15. **Revisión humana:** H3.

**Crear:** paquete normal de dos arenas reales, encuentro breve de una fase y viñeta; target `run-slice`.

1. Arena A→B sólo recompone recursos residentes. B→encuentro sustituye paquete y encuentro→viñeta libera combate.
2. Reintentar cada arena/encuentro diez veces con contador FDC; probar fallo de carga entre estados y recuperación.
3. Medir lectura, expansión, composición y primer frame jugable; separar frío/caliente. El skip de viñeta no promete omitir bytes pendientes.
4. Entregar DSK y pedir jugar la secuencia, provocar un reinicio y valorar interrupciones. Corregir ritmo o tiempos antes de ampliar a seis arenas.

**Probar/cerrar:** O05–O09, L01, H3. Reintentos y cambio A→B sin disco; transición recuperable; juego aprobado. Objetivos de segundos fallidos se registran y resuelven, no se maquillan con turbo.

## T26 Menú, ajustes y continuación

**Depende de:** T25. **Contratos:** C3, C6, C11.

**Crear:** menú mínimo, redefinición de teclas, pausa y códigos de capítulo.

1. Reasignar izquierda/derecha/salto/bajar/acción y rechazar duplicados/conflictos con teclas reservadas. Joystick de un botón mantiene todas las acciones.
2. Código versionado de capítulo/modo con checksum; empieza al inicio del capítulo y nunca escribe al disco. Ajustes y checkpoint en sesión permanecen residentes.
3. Añadir bonus de arena: inicial 3.000, resta 1 por tick de PLAY y al salir suma lo restante; cambiarlo después exige tuning registrado. Al llegar a cero no termina la partida ni aumenta presión en este alcance.
4. Historia sigue principal. Arcade es extensión separada tras la campaña, no requisito oculto para cerrar T26.

**Probar/cerrar:** F06, I01–I03. Código inválido no altera partida, pausa no consume bonus, muerte restaura puntuación de entrada, cara B puede arrancar para capítulos 3/4 cuando T32 la empaquete.

## T27 Reparto y biblioteca artística de producción

**Depende de:** T25. **Contratos:** C8, C9.

**Crear:** arte CPC de Art, Carlitos y Presidente, metadatos de anclajes/poses; biblioteca de tiles por capítulo.

1. Partir de referencias individuales del cómic y Pitu/Alberto. Las hojas generadas son bocetos; producir sprites indexados nuevos.
2. Un personaje cada vez: pose base, máscara, vista al lado de Pitu en CPC, después animaciones estrictamente necesarias. Registrar aprobación de identidad antes de multiplicar poses.
3. Compartir tiles y subanimaciones sin modificar tintas reservadas a personajes. Recortar/deduplicar con anclajes estables.
4. Exportar bytes de espejos/desplazamientos y todos los frames residentes. Fail de build si excede banco o paquete. No degradar colores automáticamente.

**Probar/cerrar:** A01–A03, R01–R05 para nuevas dimensiones y revisión humana de reparto. Si un personaje no está aprobado, mantener su producción pendiente; no sustituirlo por otro inventado.

## T28 Primer capítulo completo

**Depende de:** T26, T27. **Revisión humana:** H4.

**Crear:** seis niveles de Copias infinitas y remate según historia. **Subpasos:** una arena por vez, encuentro, revisión del capítulo.

1. Ampliar la muestra a cinco arenas normales compartidas y un encuentro con Alberto y tres bocas. Diferenciar decisiones y rutas; no copiar cinco veces el mapa gráfico con colores nuevos.
2. Validar cada nivel: rutas, fuente que puede apagar el último objetivo, spawn seguro, reinicios y solución grabada. Mantener todos los recursos normales residentes si caben.
3. Medir paquete real de cinco arenas, encuentro y remate. Si no cabe, revisar deduplicación antes de proponer una carga intermedia documentada.
4. Jugar el capítulo completo y valorar progresión. Registrar H4, corregir fallos críticos y repetir la muestra de rendimiento con el peor escenario nuevo.

**Probar/cerrar:** L01–L04, O09, Q02/Q03, H4. Primer capítulo utilizable como patrón de producción; no abrir capítulos restantes sobre fallos críticos conocidos.

## T29 Capítulo de Producción urgente

**Depende de:** T28. **Crear:** seis niveles y encuentro de Carlitos.

1. Enseñar paneles fijos con Art y conservar alternativa frontal al introducirlos.
2. Para paneles cambiantes, fijar primero contrato y pruebas: aviso mínimo de 25 ticks; cambio sólo con zona de seguridad libre de papeles; si está ocupada, posponer. Señalizar la nueva orientación antes de emitir hacia ella.
3. Implementar cambios discretos de Carlitos mediante datos; no nuevo renderer ni ángulos libres. Comprobar que ninguna combinación deja sin solución.
4. Producir rótulos/decorados nativos, un replay por nivel, remate y paquete. Validar tras cada arena, no después de dibujar las seis.

**Probar/cerrar:** N04, L01–L04, R04, O09 y Q02/Q03 del peor nivel. Revisión humana del capítulo y sus nuevos avisos; fallo de claridad bloquea la mecánica nueva.

## T30 Capítulo de calle y apoyos móviles

**Depende de:** T29. **Crear:** seis niveles, apoyo móvil y carro anunciado.

1. Antes de arte, crear fixture vacío de una plataforma móvil. Especificar delta por tick, transportar al actor apoyado antes de su movimiento propio y resolver techo/lateral sin empotrarlo. Estado y fase en replay.
2. Primera plataforma lenta sólo da un atajo; hay ruta fija. Probar extremos, salto al cambiar sentido, bajarse, descenso voluntario y pausa/reintento.
3. Carro reutiliza una plaza de enemigo, con aviso sonoro/visual y trayectoria fija; no eleva el límite medido de actores.
4. Implementar encuentro de reparto en cámara fija y seis arenas una a una. No introducir scroll o conducción por la apariencia del decorado.

**Probar/cerrar:** S09, E05, L01–L04, O09, Q02/Q03 y revisión humana del capítulo. Si aparece un caso de aplastamiento no especificado, resolverlo en el contrato/fixture antes de producir niveles dependientes.

## T31 Purple Paper y final

**Depende de:** T30. **Crear:** seis niveles, encuentro final, final narrativo y créditos.

1. Aplicar el estilo nativo del plató conservando separación visual de Pitu/papeles. Moto, focos y guitarra estáticos salvo presupuesto explícito para una región pequeña.
2. Encuentro final con tres fases cortas y checkpoint de fase en historia. Todos sus recursos residen durante reintentos; limpiar proyectiles/IA/timers al cambiar de fase.
3. Las conductas combinan reglas ya verificadas. El último encargo y caída del cartel son estados de resolución; no necesitan físicas nuevas de objetos grandes.
4. Intro/remates/final saltables, fuentes comunes y retratos parciales. Verificar que skip nunca activa gameplay con un paquete incompleto.

**Probar/cerrar:** F07, L01–L04, O09 y Q02/Q03. Revisión humana del capítulo/final y del checkpoint; no perder progreso de fase por muerte ni duplicar puntos reintentándola.

## T32 Dos caras y ocupación física del disco

**Depende de:** T31. **Crear:** `make disk-a`, `disk-b`, `check-disks`; manifiestos finales por cara.

1. Empaquetar DATA de 40×9×512; conservar arranque/común en ambas caras. Añadir índices, cabeceras y padding reales al cálculo.
2. Reabrir el DSK terminado con parser independiente: extraer cada archivo/recurso y compararlo con el build; reconstruir tabla de sectores desde colocación real.
3. Probar una partida A→B con una única vuelta manual, arranque B con código de capítulo 3/4 y rechazo de A cuando se solicita B.
4. Emitir ocupación/reserva por cara y pico por paquete. Si se consume reserva, documentarlo; si supera capacidad, rechazar y presentar opciones. No usar pistas extra ni cambiar geometría para ocultar el exceso.

**Probar/cerrar:** O10, C04, B04. Arranque independiente en ambas caras, recursos íntegros y ningún banco o medio desbordado. El tamaño del archivo DSK no es el espacio útil del disco.

## T33 Regresión de campaña en emuladores

**Depende de:** T32. **Revisión humana:** H5. **Crear:** `make verify-candidate` y matriz por entorno.

1. Ejecutar todas las suites existentes con candidato de hashes congelados. Cada nivel tiene al menos un replay ganador más casos de fallo/reintento. Además, controlar el emulador y ejecutar el DSK final desde arranque frío: menú → campaña entera sin saltos → final → nueva partida. Conservar entradas, checkpoints, snapshots de memoria, capturas y hashes. Los replays sólo pueden suministrar controles; no pueden editar vidas, posición, objetivos ni fase. Comprobar también controles manuales, ayuda, pausa, muerte y reintento. Un proceso vivo, un catálogo DSK correcto o los tests host no cierran este paso.
2. Usar un segundo emulador para arranque, casos de bancos, pantalla, audio y disco; anotar CRTCs soportados realmente y versiones/ROMs.
3. Repetir benchmark completo en la escena de peor carga de campaña y soak de disco. Registrar scanout/tearing y escuchar audio real.
4. Partida humana completa: controles, aprendizaje, dificultad, referencias visuales, final y posibilidad de continuar. Triage: corrupción, bloqueo, pérdida de checkpoint o daño invisible son bloqueantes.

**Probar/cerrar:** Z01–Z03, H5. Sin defectos críticos abiertos. Coberturas sin entorno disponible siguen pendientes; no afirmar todos los CRTCs a partir de un perfil genérico.

## T34 Validación en CPC físico

**Depende de:** T33, O16. **Crear:** paquete de prueba y formulario con modelo, CRTC, ROM, unidad y medio.

1. Preparar DSK/copia transferible, hashes, controles y lista corta de pruebas para quien tenga el equipo. No asumir que Gotek equivale a una unidad de 3 pulgadas.
2. Medir arranque frío, cambio de cara, reintento sin acceso, audio, respuesta, tearing y recuperación ante medio incorrecto. No retirar un disco durante escritura: el juego base no escribe.
3. Ejecutar recorrido y cargas largas definidos en Z04/O03 cuando el entorno lo permita; registrar límites físicos ensayados y fallos.
4. Si sólo hay un CRTC/unidad, certificar únicamente esa combinación. El resto sigue pendiente.

**Cerrar:** Z04 con evidencia real. Sin CPC disponible, marcar bloqueada por hardware y entregar el paquete preparado. T35 puede empaquetar un candidato de emulación sin fingir esta certificación.

## T35 Empaquetar el candidato y entregar instrucciones

**Depende de:** T33, O16. **T34 determina:** si puede etiquetarse validado en hardware.

**Crear:** `make candidate`, carpeta de entrega versionada, instrucciones de arranque/controles/cara B y notas de limitaciones.

1. Dos builds limpios reproducibles; DSK A/B, hashes, configuración, procedencias, créditos y manifest de pruebas.
2. Excluir herramientas temporales, ROMs no redistribuibles, archivos personales y logs enormes de la entrega del jugador; conservar evidencia técnica aparte.
3. El resumen indica `hardware_verified` sólo si T34 está done y enlaza combinaciones ensayadas. Si no, etiqueta «candidato validado en emulación».
4. Abrir/verificar el paquete desde una copia limpia siguiendo únicamente sus instrucciones. El empaquetador rechaza evidencia ausente, incompleta o de otro hash; el DSK entregado debe coincidir byte a byte con el completado en T33. No publicar ni subir a servicios como parte de esta tarea.

**Probar/cerrar:** B04, Z03/Z05; artefacto reviewable y lista de pendientes real. Terminar T35 no cierra automáticamente T34 ni convierte el plan entero en completo.
