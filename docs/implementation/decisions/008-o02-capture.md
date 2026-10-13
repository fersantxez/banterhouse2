# O02: captura CPC y cronómetro

O02 deja un camino de captura reproducible para el CPC6128 clásico emulado. El backend fijado es Caprice32 4.6.0, fuente oficial en el commit `15dd50d7bc498ff0d509e8b78c827f98d1f28a5a`, perfil de 128 KiB y ROM con SHA-256 `31c3668c67bea027dab698ece233c9434d9324f9ba7dac84db58f400b6689562`. La compilación instrumentada vive en `build/caprice-timing/`; no reemplaza la aplicación Caprice instalada ni el ejecutable del juego.

## Qué captura

`tools/run_cpc_case.py` construye el probe y su DSK, escribe un archivo de marcadores desde símbolos del mapa, lanza Caprice y exige tanto `cycles.csv` completo como un SNA CPC válido. El PC se observa en el host al comienzo de cada instrucción. El backend acumula los T-states del Z80 en el host y escribe la traza fuera de la memoria invitada. El volcado SNA aporta 128 KiB de RAM física, cabecera de máquina y 16 KiB de VRAM visible. La firma y build-id en `0x3C00`, contador 42, centinelas `00 55 AA FF`, byte `done=A5`, firma de código y guarda de 128 bytes son comprobados antes de aceptar el caso.

Los marcadores PC se ignoran hasta que la firma y el build-id del probe estén escritos. La terminación requiere también `done=A5`. Esto evita aceptar direcciones coincidentes mientras BASIC arranca o ejecuta otros comandos. La prueba negativa del backend rechaza build-id equivocado, símbolo ausente, timeout, traza sin marcadores y SNA corto.

## Calibración observada

Ejecución final: `research/runs/20261013T-O02-final/results.json` y `summary.json`. Dos secuencias ensambladas fijas de uno y dos `NOP` midieron 4 y 8 ciclos. Ocho flancos de VSYNC del PPI sumaron 638.960 ciclos, 79.870 por intervalo frente a los 80.000 nominales: error de 0,1625%, dentro de la tolerancia de 1%. Resolución del contador: 1 T-state. Un par CPC de marcas begin/end (dos cargas inmediatas y dos escrituras a `0x3FFF`) costó 48 ciclos; el intervalo entre escrituras fue 24 ciclos. Ese coste pertenece al probe y no se resta de otras mediciones.

`TELEMETRY_PHASE_BEGIN/END` usa IDs 1–8 para `restore`, `persistent`, `sprites`, `hud`, `sim`, `audio`, `banks` y `frame`; el bit alto indica salida. Sin `BH2_TELEMETRY_PHASE_MARKERS`, las macros se compilan a no-op. El backend valida el anidamiento, calcula tiempo inclusivo y exclusivo, y resta a cada padre la duración inclusiva de sus hijos. Así, audio dentro de sim/frame es un subconjunto y no se suma dos veces. El tiempo de una fase incluye el trabajo de interrupciones que ocurra mientras está abierta. El ISR no recibe todavía una subfase propia, por lo que su servicio durante una espera no se informa por separado hasta instrumentar esa ruta en una tarea posterior.

## Límites y siguientes usos

Los resultados son del modelo Z80 de Caprice fijado, no de un CPC físico. El probe deshabilita IRQ durante la secuencia de calibración; O02 demuestra extracción y escala temporal, no valida deadlines del juego. La captura de fase de prueba verifica un par `restore`; los costes de producción para sprites, HUD, simulación, audio y bancos siguen sin medir y se añadirán a las cargas congeladas de O03/O05. El wall time del proceso Python queda registrado sólo como duración de ejecución del emulador, nunca como ciclos CPC.

P01/P04 y sus límites de entrada se reutilizan del cierre de T04: 3.000 VSYNC/ticks, cola y wrap probados en Caprice; acorde completo y hardware físico siguen sujetos a sus registros de T04. B03 del probe pasa con `tools/check_link_map.py`: código `0x0100–0x023A`, datos hasta `0x3C0F`, pila reservada separada y páginas de vídeo fuera de código/datos.
