# Reparación autónoma de entrega, juego y música

Revisión 1 · 12 de octubre de 2026 (hora local del usuario; registros UTC pueden indicar día 13).

Prioridad sobre E00–E04 y sobre continuar optimización/producción. Petición: los BIN entregados fallan, la primera pantalla suena sólo a beats y las pruebas dejan ventanas abiertas. El plan se redactó antes de ejecutar la reparación. Seguimiento: [AUTONOMOUS_STATUS.json](AUTONOMOUS_STATUS.json). Instrucción de ejecución continua: [AUTONOMOUS_EXECUTOR.md](AUTONOMOUS_EXECUTOR.md).

## Resultado exigido y límites

Entregar un único DSK de juego identificable, un lanzador de doble clic que cargue ese mismo disco y una partida comprobada desde arranque frío hasta final y nueva partida. La primera fase tendrá música melódica pop ochentera y efectos distinguibles. Ningún paso técnico exige que Fernando pulse teclas, cierre ventanas, grabe vídeos o escuche para desbloquear la ejecución. El agente realiza las acciones y recoge evidencia; la valoración artística humana y el CPC físico conservan su estado pendiente.

Reparar las 24 arenas del prototipo. La campaña narrativa completa necesita trabajo adicional y debe seguir figurando como pendiente. No prometer una hora de finalización: trabajar secuencialmente hasta cumplir los criterios y, si existe un bloqueo externo real, dejar diagnóstico y continuación precisos. Conservar los fallos en el informe aunque se alcance la fecha prevista de entrega.

## Evidencia disponible y problemas del método anterior

- El usuario informa fallos generalizados; es una incidencia abierta. La causa concreta sigue sin reproducirse en esta revisión. Conservar los anteriores runs E como histórico; no borrarlos ni usarlos para invalidar el reporte actual.
- `tools/run_game.py` lanza un DSK explícito pero sobrescribe `build/launch.log`, usa configuración compartida y no administra el ciclo de vida de ventanas. `Jugar.command` abre un bundle que puede reutilizar una instancia: investigar esta ruta también.
- `make test` combina tests host, construcción de fixtures y validadores de evidencias anteriores. No acredita por sí solo una ejecución nueva de cada BIN en CPC.
- `tools/validate_release_evidence.py` comprueba hashes y snapshot final, pero admite checks manuales booleanos sin relacionar cada acción con su evidencia temporal. Un snapshot final no prueba teclado, scanout continuo ni audio.
- El código actual de `src/platform/music.s` contiene tablas de melodía/bajo y silencios; esto no prueba que el disco oído por el usuario las reproduzca. Comparar fuente, BIN, DSK y mezclador AY antes de atribuir el problema a la composición.
- Se observaron aproximadamente 1,1 GiB libres durante esta auditoría. Comprobar espacio antes de build/vídeo; no duplicar toolchains ni grabar toda la noche sin cuota. No limpiar archivos personales.
- Se ha observado un proceso de diagnóstico independiente `build/caprice-timing/source/cap32` ejecutando RENDER. No mezclar sus snapshots con los del juego ni matarlo por nombre. Si modifica entradas del build durante una validación, invalidar esa ejecución y aislar el candidato.

## Protocolo común de ejecución y limpieza

Cada caso sigue: inventario → adquisición exclusiva → arranque frío → acción → observación → aserciones → guardar resultado → limpieza en `finally` → verificar limpieza. Un caso no está terminado hasta registrar su limpieza, también con error o timeout.

1. Crear `research/runs/<UTC>-Nxx-<caso>/` con configuración privada, log, manifiesto de hashes, entradas, observaciones y resultado. Capturas en esa carpeta; nunca en raíz, Escritorio ni ventanas de Preview. Evitar abrir visores; inspeccionar archivos directamente.
2. Registrar PID, hora de inicio, ejecutable, argumentos, disco, identidad/ventana nativa, cwd y propietario del run. Un bloqueo de proyecto impide pruebas GUI y empaquetados simultáneos del mismo candidato. Los procesos ajenos no se adoptan como propios.
3. Un único Caprice de prueba a la vez. Obtener UI mediante Computer Use y verificar la ventana concreta antes de teclear. No basarse sólo en el título común «Caprice32». No usar AppleScript ni inyección alternativa para sortear restricciones de Computer Use.
4. Cerrar la ventana propia con la acción nativa; verificar ausencia mediante inventario global, sin volver a seleccionar la app cerrada (seleccionarla puede relanzarla). Para procesos hijos no interactivos, el supervisor puede terminar únicamente su PID/árbol cuya identidad sigue coincidiendo; nunca `killall`, `pkill cap32` ni PID reutilizado.
5. Soltar teclas, detener captura de audio/vídeo, vaciar logs, cerrar visores/diálogos auxiliares creados por el run, restaurar sólo configuración temporal propia y liberar bloqueo. Verificar delta respecto al inventario inicial. No cerrar apps/documentos personales ni descartar trabajo no guardado.
6. Ante falta de espacio: conservar primer fallo y candidato, reducir grabaciones a segmentos; borrar sólo temporales regenerables enumerados del propio run. Conservar evidencias y referencias antiguas. Archivar snapshots sueltos únicamente después de resolver referencias y generar manifiesto de rutas antiguas/nuevas.
7. Timeout inicial de ingeniería: 60 s para menú, 30 s para cierre, 30 min por campaña, 20 min por suite host/build. Son presupuestos de watchdog, no rendimiento medido. Esperar a eventos observados; no enviar teclas a BASIC porque han transcurrido dos segundos. Tras timeout recoger fallo y limpiar antes de reintentar.
8. Un intento fallido permanece FAIL. Como máximo dos reintentos automáticos por fallo de infraestructura; investigar a continuación. Los fallos del juego requieren causa/fix/regresión, no reintentar hasta obtener verde.

## N00 Conservar el fallo y retirar la aceptación anterior

**Depende de:** ninguna.
**Archivos:** dist, build, lanzadores, configuración/ROM, `research/release-validation.json`, registro de incidentes.

1. Copiar de forma acotada los artefactos actuales y reportes con SHA-256; guardar fuentes afectadas, toolchain y manifiesto. No ejecutar `make clean` antes de conservar.
2. Registrar literalmente síntomas del usuario y separar observado, histórico e hipótesis. Inventariar todos los BIN/DSK actuales y su tarea generadora sin ejecutar a ciegas.
3. Retirar aceptación de la entrega actual; conservar informe previo. Comprobar que el empaquetador no admite el informe invalidado.
4. Registrar ventanas/procesos y recursos previos; identificar interferencias y espacio disponible.

**Cierre:** reproducción preparada, histórico recuperable, inventario completo y entrega no publicable por evidencia antigua. La copia/revocación documental inicial no cierra automáticamente el inventario N00.

## N01 Aislar pruebas y asegurar cierre incluso al fallar

**Depende de:** N00.
**Archivos:** `tools/run_game.py`, nueva utilidad de sesiones y tests de supervisor, configuración privada por run.

1. Implementar exclusión, propiedad PID/ventana, logs únicos, timeout y limpieza descritos arriba. No introducir dependencia de stdin ni preguntas interactivas.
2. Separar lanzador de usuario de supervisor de pruebas, compartiendo resolución de disco/configuración. No abrir Terminal/Preview por cada captura.
3. Probar éxito, error antes de arrancar, crash del hijo, timeout, interrupción, segunda invocación y bloqueo abandonado. Un proceso señuelo ajeno debe sobrevivir todos los casos.
4. Verificar cero procesos/ventanas propios tras cada resultado. Si la herramienta de UI no permite cerrar, registrar fallo de limpieza y no crear más instancias.

**Cierre:** casos negativos pasan, sin recursos propios residuales ni configuración global alterada.

## N02 Reproducir y clasificar cada fallo de carga

**Depende de:** N01.
**Archivos:** inventario de N00, fixtures CPC, `tools/check_disk.py`, pruebas de smoke, launcher.

1. Clasificar BIN: ejecutable AMSDOS con dirección, binario crudo dependiente de loader, recurso no ejecutable o fixture diagnóstico. Entregar al usuario sólo juego; mantener diagnóstico fuera de dist.
2. Para cada ejecutable generado por las recetas actuales, registrar DSK contenedor, nombre interno 8.3, LOAD/EXEC, tamaño, checksum, RAM/ROM/CRTC requeridos, comando y resultado visible esperado. No asumir que doble clic en un BIN de macOS lo ejecuta en CPC.
3. Probar dist congelado mediante doble clic real; después montarlo manualmente y ejecutar el comando BASIC dentro del emulador, sin snapshots. Comparar con ruta candidata. Probar fixtures por su propio loader/comando, no todos como DEVUELTO.
4. Guardar texto exacto de error, momento, screenshot y snapshot cuando posible. Distinguir disco/nombre incorrecto, comando incompleto, ROM/perfil, cabecera, crash Z80, gráficos corruptos y falta de respuesta.
5. Si no se reproduce, ejecutar matriz de arranque N04 y documentar incidencia no reproducida; no inventar causa ni declararla resuelta por una captura de menú.

**Cierre:** cada ejecutable activo tiene resultado propio PASS/FAIL/blocked, ningún fallo queda oculto como test host; existe caso mínimo para cada fallo reproducido.

## N03 Corregir carga, build y memoria a partir del caso mínimo

**Depende de:** N02.
**Archivos:** sólo rutas causantes entre Makefile, project.mk, cfg, launcher, boot/ASM y código runtime.

1. Comprobar toolchain/ABI, cabeceras y objetos obsoletos, direcciones AMSDOS, límites de código/datos/pila, inicialización ROM/IRQ/bancos y cualquier decoder antes del menú.
2. Corregir una causa por cambio; ejecutar el mínimo que fallaba y sus regresiones. No sustituir juego por fixture ni parchear emulador para tolerar un bug del juego.
3. Dos compilaciones independientes con idénticos inputs deben producir BIN/DSK idénticos. Incremental frente a limpio también. Modificar cabecera de prueba en copia aislada debe invalidar los objetos que la consumen.
4. Congelar candidato y manifiesto. Cualquier cambio posterior de fuente/configuración relevante exige nuevo identificador y repetir casos afectados, incluida campaña completa final.

**Cierre:** fallos N02 resueltos o, si no se reprodujeron, matriz N04 obligatoria antes de aceptar; layout verificado y builds equivalentes. Ningún fixture fallido se presenta como funcional.

## N04 Probar la ruta real de arranque y teclado

**Depende de:** N03.
**Archivos:** launcher, sesiones, guiones de entrada/observación.

1. Diez arranques fríos consecutivos del mismo DSK: cinco con lanzador de doble clic y cinco montando DSK y RUN desde BASIC en instancia nueva. En todos: menú observado → entrada física mediante CUA → juego responde. Contabilizar intentos totales, no sólo los buenos.
2. Lanzar desde cwd distinto, ruta absoluta y copia de entrega en carpeta con espacios; probar dos invocaciones cercanas (reutilizar instancia correcta o error claro, nunca duplicación ambigua). No cambiar el layout del teclado del Mac.
3. Registrar mapa efectivo del emulador y verificar Left/Right/Up/Down/X/Space/P/R, pulsación, mantenimiento y liberación. La demo interna no acredita esta ruta de entrada.
4. Falta de DSK, archivo truncado, nombre interno inexistente y ROM/configuración ausente deben dar FAIL específico dentro de timeout, conservando limpieza. Sólo usar copias para corrupción deliberada.

**Cierre:** 10/10 arranques y controles correctos, negativos detectados y limpieza 100 %. Si falla uno, corregir y repetir la serie completa.

## N05 Corregir juego y representación visible

**Depende de:** N04.
**Archivos:** src/main.c, core/render, fixtures y tests actuales.

1. Verificar movimiento, salto corto/largo, caída de bordes, atravesar plataformas, colisión de máquinas/Alberto, devolución según orientación y salida. Contrastar estado Z80 y pixels visibles en varios instantes.
2. Probar pausa con ticks congelados, reanudación sin teclas pegadas, muerte, derrota, reintento, restart, transición y final. No usar escritura de RAM para acreditar resultados.
3. Comparar imagen antes/después de movimiento para detectar restos, borrado de fondo, sprite parcial, parpadeo y HUD corrupto; capturar secuencias breves en escenas de máxima carga. Una imagen correcta entre cuadros no demuestra estabilidad.
4. Reutilizar harness de lógica compartida; añadir regresión sólo de defectos reales. Resolver todas las arenas con reglas normales, conservar secuencias y checkpoints.

**Cierre:** casos dirigidos pasan en host y en Z80 según corresponda, representación visible coherente y ninguna arena imposible. No sustituye la partida completa N08.

## N06 Crear música melódica pop para la primera fase

**Depende de:** N05.
**Archivos:** src/platform/music.s, audio.s, main.c, fuentes musicales y conversor/tests.

1. Capturar referencia actual del DSK oído en N04. Auditar periodos AY, mixer, volúmenes, silencios, escrituras de SFX, registros preservados por ASM y reloj real. Separar error de reproducción de arreglo insuficiente.
2. Diseñar motivo principal de 4 compases audible desde el inicio (entrada antes de 2 s), respuesta de 4 compases y variación A/B de al menos 16 compases. Bajo sincopado y acompañamiento/arpegios con aire pop/funk de los 80; referencias de energía/timbre a Prince. Preferir composición original; conservar cualquier fuente musical aportada y su procedencia sin sustituirla silenciosamente.
3. Arreglo viable con los tres canales AY: B lleva melodía, C bajo y A acompañamiento/percusiones con prioridad temporal de SFX; restaurar música tras cada efecto. Si se mantiene A exclusivo para SFX, repartir armonía/arpegios en huecos de B/C y justificar resultado audible. No prometer más voces simultáneas.
4. Centralizar propiedad del mixer y volumen; OFF debe quitar música y conservar SFX. Evitar que un mute de SFX mate la melodía/bajo o que music_tick borre efectos. Pausa: silenciar y congelar posición, reanudar sin nota colgada.
5. Guardar partitura/eventos, fuente editable, exportación determinista y presupuesto real de bytes/ciclos. Reutilizar player si sirve; adoptar otro sólo si mejora medida y con integración/ABI comprobadas. No migrar por nombre de herramienta.

**Cierre:** tema A/B implementado, melodía y bajo diferenciados, acompañamiento, loop sin notas colgadas, coste medido y SFX legibles. La presencia de tablas de notas no cierra N06 sin prueba N07 de salida real; mantener N06 en progreso hasta disponer de una captura preliminar correcta.

## N07 Validar audio efectivo del emulador

**Depende de:** N06.
**Archivos:** captura PCM/AY, analizador y evidencia de audio.

1. Obtener PCM desde la salida de audio del emulador por una función oficial/documentada. Si falta, crear observador acotado del flujo PCM en una copia instrumental, sin cambiar síntesis, temporización ni juego; verificar equivalencia y repetir smoke visible con el emulador de entrega. Registrar expresamente esa diferencia. Un WAV sintetizado desde tablas host no demuestra sonido del juego.
2. Capturar 60 s de primera fase sin acciones y 60 s con saltos/devoluciones/impactos, más ON/OFF/ON, pausa/reanudación y dos vueltas completas del loop. Registrar los hashes de DSK, player, captura y entorno.
3. Aserciones: señal PCM presente, cambios de altura que siguen eventos de melodía, bajo presente, canales tonales habilitados cuando corresponde, temporización estable, efectos detectados y música restaurada, ausencia de silencio no previsto >2 s y saturación sostenida. Permitir descansos escritos en partitura; umbrales fijados antes del caso, no ajustados para hacerlo pasar.
4. Contrastar captura con eventos/traza AY y partitura; un contador ON o `Sound buffer ready` no basta. Si hay herramienta de escucha/análisis disponible, usarla y registrar valoración separada. Sin escucha no afirmar calidad subjetiva comprobada; tampoco certificar altavoces del laptop desde PCM.
5. Negativos: silenciar B, fijar una sola nota, apagar mixer con un SFX y corromper tempo en fixture aislado. El análisis debe detectar los cuatro defectos.

**Cierre:** música tonal comprobada en PCM del runtime, todos los escenarios y negativos pasan; ningún permiso/grabación manual de Fernando es requisito. Si no se consigue captura real, audio permanece bloqueado y la entrega completa no se certifica.

## N08 Completar campaña y estabilidad con el candidato final

**Depende de:** N07.
**Archivos:** fixtures de campaña, checker de snapshots, registro de inputs y checkpoints.

1. Desde DSK frío con audio final: título → las 24 arenas → WIN → nueva partida. Recorrido continuo sin cargar SNA, sin invulnerabilidad, teletransporte, cambio de vidas o salto de nivel. Replay interno sólo proporciona inputs a simulación normal y se declara; controles reales ya cubiertos por N04.
2. Registrar entrada/salida de cada arena, vidas, puntos, objetivos y ticks; observar al menos un checkpoint visual de cada fase y secuencias de transiciones. Validador de final más evidencia temporal, nunca sólo contador de fases.
3. Dos recorridos completos independientes. Además 30 min de estabilidad con pausas, reintentos y cargas normales; watchdog exige progreso esperado, guardas de memoria intactas y ningún crash/corrupción.
4. Repetir arranque y recorrido completo del mismo DSK en segundo emulador independiente configurado como CPC6128 clásico. Elegir y documentar fuente oficial y capacidades; no asumir que está instalado. No comprar herramientas. Si falta automatización de inputs, investigar API documentada; no simular PASS con primer emulador.

**Cierre:** ambas campañas primarias y recorrido secundario pasan; todos los fixtures ejecutables activos tienen resultado real, sin fallos de carga pendientes. CPC físico sigue no verificado.

## N09 Impedir falsos positivos y empaquetar los bytes probados

**Depende de:** N08.
**Archivos:** validate_release_evidence.py, package_release.py, test_release_gate.py, esquema de resultados.

1. Gate exige resultados por caso y enlaces a evidencia con hashes; rechaza booleans desnudos, checks ausentes, blocked, timeout, informe revocado, disco distinto, runs interrumpidos o cleanup fallido.
2. Pruebas negativas del gate: snapshot final de otro build, imagen antigua, log incompleto, checkpoint omitido, dos procesos ambiguos, audio sin melodía, limpieza pendiente y manifiesto alterado. Todas deben rechazar antes de tocar dist.
3. Empaquetar copia exacta del candidato aprobado, sin reconstruir tras validar; verificar SHA destino. Dist sólo contiene disco de juego, lanzador/guía y manifiesto; diagnósticos se quedan en build/research.
4. Repetir tres arranques fríos del paquete final mediante el mismo doble clic del usuario; empezar, mover/saltar/devolver, pausar y salir. Volver a verificar hashes tras abrir. Conservar entrega anterior recuperable.

**Cierre:** gate rechaza cada negativo; paquete nuevo pasa ruta real 3/3; informe enumera alcance y cualquier limitación sin reclamar juego narrativo terminado.

## N10 Cerrar sesión y entregar informe utilizable

**Depende de:** N09.
**Archivos:** README.md, docs/PLAYTEST.md, informe final y manifests de limpieza.

1. Guardar resumen corto: rutas, hashes, comandos de reproducción, número real PASS/FAIL/blocked, música verificada, memoria/tiempos medidos y limitaciones. No presentar el OSD del emulador como FPS del juego.
2. Cerrar todos los procesos/ventanas/visores creados por la ejecución, incluso la partida final. No dejar el juego abierto hasta que Fernando lo pida. Cero capturas nuevas sueltas fuera del directorio del run.
3. Verificar por inventario global y procesos que no queda nada propio; no relanzar para comprobar cierre. Registrar las instancias ajenas identificadas sin interferir.
4. Actualizar estado sólo con evidencias. Si algo falla, no marcar listo: dejar paquete anterior como no aceptado, fallo mínimo, último candidato, tarea exacta y próxima acción.

**Cierre:** artefacto probado accesible, informe honesto, limpieza comprobada. Sólo aquí cambiar aceptación a `ready_for_user`.

## Contrato de resultados para implementar en N01/N09

Cada caso contiene `case_id`, `run_id`, inicio/fin UTC, `status` (pass/fail/blocked), `reason`, hashes de candidato/ROM/config/emulador/fuentes, comando/ruta de lanzamiento, propietario PID/ventana, inputs observados, aserciones con esperado/actual, evidencias por hash, código de salida/timeout y `cleanup` con inventario antes/después y residuos. Los campos no medidos son null. El resumen se deriva de los casos, no se edita para aprobar.

Los comandos nuevos (supervisor, captura PCM, gate v2) **todavía no existen**: N01, N07 y N09 los crean y documentan con `--help` y tests. No anunciar `make autonomous-test` como funcional antes de implementarlo. Reutilizar comandos existentes tras leerlos: `make doctor`, `make test-game`, `make test-game-build`, `make test`, `python3 tools/check_disk.py`, `python3 tools/check_game_snapshot.py RUTA.sna --complete`, `python3 tools/test_release_gate.py`. No lanzar la suite completa sólo para validar este documento.

## Orden de ejecución continua

N00 → N01 → N02 → N03 → N04 → N05 → N06 → N07 → N08 → N09 → N10. Una tarea habilitada cada vez, pero continuar con la siguiente sin pedir confirmación tras cada ficha. Si un test descubre un defecto anterior, registrar regresión y corregirlo antes de repetir la prueba; invalidar los resultados afectados por los bytes nuevos. No usar los gates humanos de producción como excusa para no reparar este candidato, ni marcarlos aprobados automáticamente.
