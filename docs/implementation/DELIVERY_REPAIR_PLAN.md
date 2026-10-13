# Reparación de la primera entrega

> Registro histórico. Este candidato se rechazó el 12 de octubre por fallos de carga y problemas de música. La reparación se organizó en el [plan N00–N10](AUTONOMOUS_REPAIR_PLAN.md). El disco posterior está descrito en el [informe de entrega](../DELIVERY_REPORT.md).


Petición del usuario, 12 de octubre de 2026. Intervención E00–E04 sobre el prototipo existente, anterior a continuar T06. Las revisiones H0–H5 y la producción de la campaña narrativa siguen pendientes. Ejecutar una tarea habilitada cada vez; conservar su resultado en DELIVERY_STATUS.json. STATUS.json mantiene intactos los hitos de producción.

## E00 Conservar y reproducir

Depende de: ninguna. Conservar fuente, BIN, mapa y ambos DSK (build y dist), con hashes. Arrancar el emulador desde cero, registrar qué disco se abrió y capturar el fallo real. Un proceso vivo o un catálogo válido no constituye arranque. Cierre: copia recuperable y reproducción documentada.

## E01 Arranque que llega al menú

Depende de: E00. Unificar el lanzador y el disco que prueba el usuario; no entregar un dist antiguo mientras make run abre otro build. Ejecutar automáticamente RUN con Intro. Ofrecer un archivo .command de doble clic y documentar el comando AMSDOS para otros emuladores. Arrancar tres veces desde CPC recién reiniciado, sin snapshots ni inyección de RAM; ver menú y empezar a jugar. Conservar captura y hash de cada disco probado. Probar también ruta inexistente y fallo del emulador: deben devolver error claro.

## E02 Corregir el bucle jugable y hacerlo comprobable

Depende de: E01. Revisar el código realmente entregado: dirección del papel devuelto, límites de pantalla, cadencia sin desbordamientos, correspondencia de máquinas y dibujo, ruta a cada objetivo y salida, pausa, muerte, reinicio, transición y final visible. Reutilizar la física ya corregida. Compartir la simulación entre pruebas host y Z80; no mantener una segunda implementación de las reglas. Pruebas dirigidas deben fallar ante las regresiones detectadas. Cada arena debe tener una secuencia de entradas que la resuelva con las reglas normales. No usar invulnerabilidad, teletransporte, escrituras de estado o saltos de fase para acreditar una solución. El build Z80 debe depender de las cabeceras: cambiar tuning.h, niveles o replay obliga a recompilar. Comparar BIN y DSK incrementales con una compilación limpia; la reproducibilidad de un smoke aislado no prueba el juego.

Diseño mínimo observable: el jugador sabe qué devuelve, qué máquinas siguen activas, cuántas vidas tiene, dónde está la salida y si ha ganado o perdido. Los estados terminales tienen texto e instrucción de continuación. Mantener sprites canónicos y rejilla Mode 0. Las posiciones de arte deben corresponder a las colisiones; ningún marcador invisible sustituye a un objetivo.

## E03 Ejecutar hasta el final en el CPC emulado

Depende de: E02. Desde arranque en frío del DSK candidato: menú → jugar → todas las arenas incluidas → final → nueva partida. Conservar entradas, checkpoints de cada arena, estado final, capturas y hashes del DSK/BIN/configuración/ROM. Si se usa replay, sólo suministra las mismas entradas que el teclado y ejecuta el código de juego; documentar esa modalidad y comprobar también controles manuales. Una prueba del recorrido de plataformas no acredita combate ni campaña. Comprobar ayuda, música ON/OFF, pausa/reanudación sin avance de simulación, muerte/reintento, reinicio, límites y nueva partida. Los screenshots aislados o un test host no sustituyen esta ejecución. El OSD de Caprice mide emulación, no FPS del juego.

Medir por separado incidencias de audio, velocidad y vídeo; no certificar escucha ni hardware físico si no se han probado. Segundo emulador y CPC físico siguen sus hitos T33/T34. Si alguna arena no se completa, E03 falla y se vuelve a E02; no empaquetar como completo.

## E04 Publicar exactamente el disco probado

Depende de: E03. El empaquetador debe rechazar evidencia ausente, fallida o de otro SHA-256. Copiar los bytes probados, verificar hash de destino y proporcionar DSK, lanzador y guía breve. Repetir el arranque desde dist con el lanzador de entrega. Publicar alcance real y fallos pendientes. Archivos provisionales pueden existir bajo build; no presentarlos como entrega validada. Cierre: todas las pruebas de E03 y arranque de dist registrados para el mismo binario. No cerrar tareas narrativas, arte, optimización o hardware pendientes por esta reparación.

## Secuencia reproducible del candidato

1. `make test`: juego compartido con ASan/UBSan, dependencias de cabeceras, compilación limpia idéntica, recursos, geometría, física, mapa, fixtures y contenedor DSK. Revisar código de salida.
2. `make run-candidate`: esperar menú, comprobar controles manuales. Desde arranque frío, D ejecuta las entradas completas de `tests/fixtures/campaign-replay.json` en el propio Z80. R cancela; no usarlo en la partida acreditada.
3. Guardar capturas y snapshots nativos del emulador. `python3 tools/check_game_snapshot.py RUTA.sna --complete` debe acreditar las 24 arenas y el final. Verificar luego Espacio → nueva partida. No escribir memoria para obtener esos estados.
4. Registrar checks observados, suite y hashes en `research/release-validation.json`; conservar también fallos y experimentos rechazados. `python3 tools/test_release_gate.py` prueba que un hash distinto, prueba pendiente o evidencia alterada bloquean la entrega.
5. `make package`: sólo copiar candidato acreditado. Doble clic en `Jugar.command`, esperar carga automática y comprobar arranque de `dist`. Guardar hash y captura finales.

Las revisiones de diversión, arte, audio audible, un segundo emulador y CPC físico mantienen sus gates propios. Este recorrido no los aprueba.
