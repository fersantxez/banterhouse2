# Pruebas del disco de entrega

Fecha: 13 de octubre de 2026. Estado registrado: `ready_for_user`.

El informe describe el paquete que se probó entonces en `dist/`. El mismo disco está ahora en [release/Devuelto-CPC6128.dsk](../release/Devuelto-CPC6128.dsk). Los lanzadores y registros locales se archivaron al limpiar el repositorio.

## Archivos probados

- Disco: `dist/Devuelto-CPC6128.dsk` (204.544 bytes), SHA-256 `034efbab917c1ec318cf25312aa7842d4ff74a4c306a3f48f6890f4995dc1f8c`.
- Programa principal: 38.150 bytes; SHA-256 `dc1bfb7d54ac9aed9cf3a130b88ac297449ad9ba5730299b0446d4a5d05416c3`.
- Mapa usado para identificar la imagen ejecutada: SHA-256 `d96dcb4ea8f924011b0aafd2534931d7f102043a7540526b95215be938c34c1e`.
- Lanzador, guía y hashes del paquete: `dist/Jugar.command`, `dist/LEEME.txt` y `dist/SHA256SUMS.json`.
- Arranque usado en macOS: doble clic en `dist/Jugar.command`. Comando BASIC: `RUN"DEVUELTO.BIN"`.

El disco contiene el programa y cuatro archivos AMSDOS: `CH01.BIN`, `CH02.BIN`, `CH03.BIN` y `CH04.BIN`. Se cargan al cambiar de capítulo y reutilizan la memoria del fondo anterior. Las tres partidas completas pasaron por esas cargas. El disco debe permanecer montado durante el juego.

## Resultados

El manifiesto `research/release-validation.json` enlaza 10 casos en estado PASS: dos campañas completas Caprice32, una campaña en 1984 v0.4.20 configurado como CPC6128 de 128 KiB, estabilidad de 30:22, PCM, cargas modulares, controles manuales y tres arranques fríos del paquete. Cada campaña completó arenas 1–24 y llegó a la pantalla final; el código de ejecución se verificó contra el BIN y el mapa guardados como referencia. La sesión de estabilidad contiene nueve snapshots de checkpoint y terminó con código 0.

Los tres arranques fríos se hicieron sobre el DSK publicado por `Jugar.command`, no sobre una compilación distinta. Comprobaron menú/inicio, movimiento, salto, devolución, pausa y salida limpia. Además, el lanzador incluido en `dist` se ejecutó directamente: la sesión supervisada acabó con estado PASS y `process_group_absent=true`. El DSK se inspeccionó con `tools/check_campaign_dsk.py`: BIN idéntico, cabecera AMSDOS y checksums válidos, más los cuatro activos de capítulo.

La grabación de la fase inicial se tomó de la salida PCM de Caprice, estéreo S16LE a 48 kHz y 66 segundos. El análisis midió 19 bandas de melodía y 27 de bajo, paso estimado de 0,12 s, cero ventanas saturadas y cero silencios imprevistos mayores de 2 s. La captura independiente con música apagada detectó los efectos de salto y devolución; otra secuencia comprueba pausa y recuperación. El análisis comprobó melodía, bajo, pulso y mezcla. Quedó pendiente escucharla para valorar el arreglo y el sonido en altavoces.

El validador se probó con ocho casos inválidos: imagen de otra compilación, disco antiguo, sesión incompleta, checkpoints ausentes, lista ambigua de procesos, audio sin melodía, limpieza pendiente y hash de evidencia alterado. Los ocho se rechazaron sin tocar el disco publicado. Validación final:

```sh
python3 tools/validate_release_evidence.py
python3 tools/test_release_gate.py
python3 tools/check_campaign_dsk.py build/campaign/DEVUELTO.dsk build/campaign/DEVUELTO.bin build/campaign/DEVUELTO.map
```

Los informes, grabaciones, sesiones, snapshots y hashes se guardaron en `research/runs/`; el manifiesto principal los enumera. Después se trasladaron a `banterhouse2-archive`, conservando los archivos originales.

## Límites

La entrega es un prototipo técnico jugable con 24 arenas. No contiene todas las escenas narrativas, personajes con reglas propias ni el alcance de producción planeado. La partida completa usa replay determinista; movimiento, salto, devolución, pausa, reintento y nueva partida tienen además pruebas manuales independientes. Quedaron pendientes el CPC físico y las pruebas con jugadores para valorar gráficos, diversión y respuesta a los controles. La pantalla de FPS de Caprice no se usa como medición de rendimiento del juego.

Al finalizar, se cerraron las sesiones supervisadas y no quedó ventana de Caprice abierta. La salida de audio del Mac volvió a MacBook Air Speakers a volumen 0 y silencio activado, estado previo a la captura.
