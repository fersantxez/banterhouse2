# Pruebas del plan de optimización

Especificaciones para implementar, **no resultados ejecutados**. Cada OP termina en `pass/fail/blocked` con evidencia. Contratos C y pruebas B/P/K/R/Q/U/O/Z en [CONTRACTS.md](CONTRACTS.md) y [TESTS.md](TESTS.md). Las tareas creadoras se definen en [OPTIMIZATION_TASKS.md](OPTIMIZATION_TASKS.md).

## Oráculos y entorno

Imagen: compositor host independiente por píxel y volcado real del Z80. Estado: serialización campo a campo por tick y casos pequeños calculados independientemente. Tiempo: ciclos CPC emulados verificados, nunca duración de Python. Memoria: mapa enlazado, guardas y máximo observado de pila. Dos renderers con el mismo error no quedan aprobados por coincidir entre sí.

Perfil funcional admite aceleración/dumps. Perfil temporal registra modelo, RAM, CRTC, hashes de ROM, emulador/versión/configuración, velocidad, turbo, disco acelerado, audio y método de captura. Verificar valores aplicados, no sólo solicitados. Plataforma obligatoria: CPC 6128 clásico 128 KiB. Plus se informa por separado.

## OP01 Auditoría y preservación

**Crea O00.** Ejecutar auditor en proyecto y fixture temporal con Makefile que referencia script ausente. Repetir alterando un archivo durante captura: rechazar snapshot inconsistente. Comparar hashes de copia recuperada e inventario. Sólo escribir bajo destino autorizado. BIN/DSK previos quedan `unverified-existing`; no aprobar tareas por existencia. Evidencia: inventario, copia acotada, logs y discrepancias.

## OP02 Original de sólo lectura

**Crea O01.** Hash inicial/final de todas las entradas copiadas: igualdad. El script rechaza destino dentro del original, incluso mediante symlink resuelto; probar protección con directorios temporales, sin intentar escribir en el original real. Copiar sólo allowlist y conservar procedencia. Adaptador nuevo y binario histórico tienen IDs distintos. Evidencia: manifiesto, dominio común, lista de adaptaciones y comandos de dibujo deterministas.

## OP03 Backend y cronómetro

**Crea O02.** Harness escribe `00,55,AA,FF`, build-id y contador conocidos en RAM reservada. Recuperar valores/VRAM del Z80. Negativos: build-id equivocado, símbolo ausente, timeout y dump corto deben producir no PASS. Medir secuencia ensamblada conocida con dos longitudes y VSYNC del perfil; considerar WAIT del CPC y documentar resolución/overhead. IRQ dentro de fase se incluye en tiempo de esa fase y no se suma otra vez. Backend sólo PNG no aprueba tiempo. Evidencia: binario, configuración, dumps y traza de calibración.

## OP04 Identidad de fixture y replay

**Crea O03.** Dos freezes iguales producen mismos hashes. Alterar por separado un byte de sprite, tuning, audio, entrada o geometría: rechazar comparación. Lógica y poses idénticas entre G/H. Dos replays comparan estado por tick; presentación a 50/25 conserva simulación. Negativos: replay truncado, recurso ausente, fixture sin música y perfil incompleto. No rellenar campos ausentes con cero. Referencia host no debe generarse a partir de un resultado Z80 fallido.

## OP05 Direcciones, clipping y píxeles

**Amplía O04.** Usar límites R01 y y=6/7/8,14/15/16,62/63/64,126/127/128,190/191/192. X pares/impares, fuera por los cuatro bordes y totalmente invisible. Fondos 00/FF/55/AA y patrón indexado; sprites transparente, negro opaco, opaco multicolor y parcial. Comparar 16.000 bytes visibles decodificados y comprobar que los 384 huecos conservan su valor inicial salvo uso explícito documentado. Canarios externos intactos. Papeles 4×6 del contrato en y=5..9; no heredar accidentalmente el 4×4 del prototipo. Fallo informa primer píxel distinto y coordenadas.

## OP06 Restauración y persistencia

**Amplía O04.** Secuencia: A solo; B cruza A; cambian pose; A desaparece; máquina cambia tapada por B; cambia HUD; B desaparece; pausa y retry. Repetir alineaciones y ocho fases Y. Cada checkpoint debe coincidir con reconstrucción independiente desde fondo persistente actual. Probar reutilizar slot con tamaño distinto y nueva escena. No usar framebuffer previo como fondo del oráculo. Evidencia: dumps, diff por píxel, secuencia exacta.

## OP07 Benchmark y estadística

**Crea O05.** Por variante/fixture: 250 ticks de calentamiento, 12.000 medidos, tres resets. Si pierde plazos, registrar cada pérdida; si entra en diagnóstico por backlog, conservar hasta fallo y marcar run incompleto, sin extrapolar. Warmup no entra en percentiles, pero sus errores se reportan.

Publicar mínimo, mediana, p95, p99, máximo e ID del peor frame. Percentiles nearest-rank: `sorted[ceil(p*n)-1]`. Mediana ordinaria: `[1,2,3,4]` debe dar 2.5 y p95/p99=4. Una traza con un pico debe conservarlo como máximo y deadline fallido. Rechazar unidades mezcladas o timestamps invertidos. Separar trabajo, espera, ISR durante espera y clases gameplay/transición/carga. Publicar además duración total; no ocultar las cargas.

## OP08 Flags y ABI

**Crea O06.** Directorios separados y flags efectivos en manifest/comandos. Wrapper con argumentos 0,1,255,256,65535 según su tipo; retorno esperado y centinelas de stack/registros preservados. Fixture negativo con ABI incompatible debe fallar verificación, sin contaminar release. Dos builds reproducibles. Medir helper y cuadro completo; tamaño y velocidad independientes. La firma real y assembler SDCC fijado gobiernan el wrapper, no una suposición sobre todas las funciones C.

## OP09 Copia de rectángulos

**Crea O07.** Width=0,1,2,8,9,64,80; height=0,1,4,6,8,32,200. Combinaciones dentro de pantalla se copian; fuera se recortan/rechazan por wrapper según contrato. Todas las fases Y y esquinas. Fuente/destino con patrones distintos. Sólo cambian bytes del rectángulo; cero no escribe y nunca ejecuta LDIR con BC=0. Comprobar 200 offsets y 16.000 direcciones visibles únicas. SP, banco e interrupciones conservados; ISR ocurre durante copia. Verificar estado inicial EI y DI mediante harness con interrupciones observables, no sólo variable sombra.

## OP10 Regiones y HUD

**Crea O08.** Score cambia cada tick: cero recomposiciones completas del escenario durante gameplay. Actor quieto anima; dos actores cruzan región fusionada; máquina se apaga debajo de Pitu; retry limpia listas. Forzar 33 rectángulos: fallback correcto, contador incrementado, misma imagen. Caso normal tiene cero overflow. Verificar contabilidad de área y comparar cada frame funcional con referencia. Descartar regiones para ganar tiempo falla aunque el promedio mejore.

## OP11 Generador de sprites

**Crea O09.** Para cada máscara/píxel del corpus enumerar 256 fondos y comparar `(background & mask) | pixel` con operaciones especializadas. Sintéticos FF/00 transparente, 00/00 negro opaco, 00/FF opaco y parciales válidos. Rechazar `(pixel & mask)!=0`, truncado, dimensiones inválidas e IDs duplicados. Dos generaciones idénticas; ensamblar y comparar tamaño máquina con manifest, no tamaño textual `.s`. Modelo host no sustituye OP12.

## OP12 Blitter Z80 ejecutado

**Crea O10.** Todas las variantes seleccionadas, par/impar, ocho fases Y, cambios de bloque y bordes con fallback. Frame ausente usa G; descriptor con generación/banco/entry inválidos se rechaza antes de salto. Comparar VRAM con G y oráculo; código/canarios intactos, SP/registros/IRQ conservados. Repetir con ISR/audio real. Guardar disassembly y retorno comprobado. Emular operaciones en Python no acredita ejecución de instrucciones Z80 enlazadas.

## OP13 Memoria y bancos

**Crea O11.** Fixture de banco de 16.384 B pasa; 16.385 falla. Solape simultáneo falla; vidas excluyentes sólo comparten con transición explícita. Código/stack/ISR necesario en ventana paginada falla mapa. Ventanas CPU no cuentan como RAM física nueva. Ejecutar 10.000 selecciones con interrupciones, H/G y retornos de error. Pico incluye comprimido, expandido, variantes, scratch, decoder, stack, padding y guardas. Mantener 256 B libres dentro de los 768 B de stack del contrato. Pico observado se etiqueta observado; no es prueba de todos los caminos posibles.

## OP14 Reloj, audio y latencia

**Amplía O12.** Replay a dos cadencias de presentación conserva estado por tick y eventos de audio. Flancos no se repiten al recuperar retrasos. Forzar >2 ticks pendientes genera diagnóstico de P04, no descarte oculto. Registrar ciclos de captura, aplicación al estado, servicio AY y primera presentación con resolución. No llamarlo latencia física hasta fotón/altavoz. Peor tick musical, SFX y teclado/joystick: cero corrupción PPI/AY y ticks de audio omitidos en runs completos aceptados. Escuchar captura. Cambios de lógica pasan S/D/F y casos de extremos/overflow.

## OP15 Presentación y páginas

**Crea O13.** Capturar movimiento/solapes/HUD a velocidad real y estudiar barrido además de imagen final. Si B no se activa, evidencia A y decisión `not_needed` cierran experimento, sin afirmar prueba física.

Si B se activa: al menos 120 presentaciones alternas; modificar HUD/fondo en impar, quitar actor en par, pausa y retry. Cada página conserva su historial y muestra versiones correctas al volver dos cuadros después. Registrar CRTC/página, guardas y ausencia de copia de 16 KiB por cuadro. Mapa B contabiliza pérdida de RAM2 como lógica. Captura insuficiente para observar tearing es inconclusa, no aprobación visual.

## OP16 Comparador y afirmaciones

**Crea O14.** Tests sintéticos: diferencia mayor que epsilon → mejora; menor/igual → inconclusa; más rápido pero píxeles distintos → inválida; audio/carga/cadencia distintos → no comparable; máximo ausente → bloqueado; menos RAM con tiempo dentro de ruido → sólo ahorro de RAM. Porcentaje `100*(base-candidate)/base`, base temporal cero rechazada, signo negativo conserva empeoramiento. No sumar porcentajes sucesivos. Métrica histórica de otro juego no es baseline equivalente.

## OP17 Adopción de variante

**Usan O06–O14.** Exigir equivalencia, mapa/stack, tres runs de baseline/candidato del mismo fixture, epsilon y decisión. Microbenchmark sirve para descartar, no basta para aceptar. Rechazo mantiene padre aceptado reconstruible; aceptación enumera todos los cambios heredados. Tiempo mejor con error de sonido/memoria falla. Acelerar un baseline lento no cierra aptitud de release T20.

## OP18 Compresión y transición completa

**Crea O15.** Corpus idéntico por codec; host round-trip y bytes Z80, longitudes 1,4095,4096 y recurso de 4097 dividido. Raw también valida contenedor. Flujos dañados no leen/escriben fuera; CRC válido no reemplaza validación de gramática/backreferences. Medir petición→primer cuadro controlable incluyendo lectura, validación, depack, variantes y composición; audio de carga aparte. Retry de partida no aumenta contador FDC. Sectores y padding salen del DSK final. Conservar fallos y distribución frío/caliente; no escoger codec por ratio exclusivamente.

## OP19 Matriz de compatibilidad

**Crea O16.** Fila por build/emulador/versión/modelo/RAM/ROM/CRTC/perfil/caso. Repetir peor carga real de campaña, bancos, solapes, audio y loader. Verificar CRTCs disponibles; no inferirlos de menú no comprobado. Segundo emulador sin cronómetro puede validar funcionalidad; no inventar tiempos. Ausentes `blocked`. T34 añade filas físicas con unidad/medio/fecha; CRTC3/Plus separado. Evidencia temporal de M2 no cubre automáticamente una escena posterior más cara.

## OP20 Reproducción y entrega

**Crea O16.** Dos builds limpios con mismos inputs/SDK generan BIN/DSK/recursos idénticos. Ejecutar instrucciones sin rutas temporales desaparecidas ni resultados previos. `verify-performance` devuelve no cero si omite caso obligatorio; mantiene reporte parcial/bloqueos. Cada afirmación enlaza a evidencia. `hardware_verified` sólo cambia con T34 done y evidencia real. Informe incluye rechazados y pendientes. No ejecutar `git clean` ni borrar cambios del usuario para hacer un build limpio.

## Esquemas mínimos que O05 debe implementar

`frames.csv`, una fila por presentación o intervalo diagnóstico identificado:

```text
run_id,variant,fixture,frame_id,sim_tick_first,sim_tick_last,phase_class,start_cycle,end_cycle,work_us,wait_us,restore_us,persistent_us,sprites_us,hud_us,sim_us,audio_in_work_us,irq_in_wait_us,bank_us,deadline_us,missed_deadline,dirty_bytes,bank_switches
```

Tiempos por fase inclusivos de ISR salvo indicación explícita en esquema. Audio dentro de trabajo es subconjunto y no se suma otra vez. `work_us` se obtiene de línea temporal global; si hay fases superpuestas se declara. Fase no medida queda vacía y en `unmeasured`. Debe cumplirse trabajo ≤ duración del intervalo con definición consistente; intervalo incompleto se etiqueta.

`audio.csv`: run, tick esperado, ciclo programado, ciclo servido, jitter y estado. `latency.csv`: evento, entrada capturada, estado aplicado, AY, presentación y resolución. Evento sin SFX tiene AY null/no aplicable, no cero.

`summary.json`: hashes/perfil, counts esperados/observados, runs completos, estadísticas por fixture/clase, peor frame, deadlines separados de render/sim/audio, stack usado/libre, bancos, overhead y ausencias. Pico de pila se mide en ejecución funcional equivalente con guardas; no fingir sondeo por cada frame temporal.

`results.json`: schema_version, task_id, build_id, environment, commands (argv/cwd/exit_code/stdout/stderr), cases (id/status/evidence/reason), unmeasured, next_step. Runners propios: 0 éxito completo, 1 fallo, 2 entorno ausente, 3 argumentos/manifiesto inválidos. Registrar códigos originales de herramientas y no reinterpretar ausencia como PASS.

## Regresión tras cambios

| Cambio | Pruebas cortas antes del gate largo |
|---|---|
| Captura/resumen | OP03/OP07/OP16 con negativos y baseline afectado |
| Flags/wrapper | OP08, B02/B03 y equivalencia de módulo |
| Restore/dirty/HUD | OP05/OP06/OP09/OP10 y replay gráfico |
| Generador/blitter | OP11/OP12, B03/K02 |
| Mapa/bancos | OP13, B03, K01–K03 y audio |
| Sim/IRQ/input/audio | OP14, P/S/D/F/U afectados |
| Doble búfer | OP15, OP05/OP06 y memoria pico |
| Codec/packer/loader | OP18, C/O y B03 |
| Arte/nivel más caro | OP04/OP05, nuevo peor caso Q |
| Sólo documentos | Comprobador documental, sin build CPC |

No reutilizar PASS si cambió un input relevante. Tampoco repetir 100 cargas por editar texto ajeno al build. Suites largas al aceptar variante, al cambiar riesgo o al candidato final.
