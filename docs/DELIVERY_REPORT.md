# Informe de entrega técnica — ¡Devuelto!

Fecha: 13 de octubre de 2026. Estado: `ready_for_user` para probar el prototipo CPC 6128.

## Paquete

- Disco: `dist/Devuelto-CPC6128.dsk` (204.544 bytes), SHA-256 `034efbab917c1ec318cf25312aa7842d4ff74a4c306a3f48f6890f4995dc1f8c`.
- Programa principal: 38.150 bytes; SHA-256 `dc1bfb7d54ac9aed9cf3a130b88ac297449ad9ba5730299b0446d4a5d05416c3`.
- Mapa usado para identificar la imagen ejecutada: SHA-256 `d96dcb4ea8f924011b0aafd2534931d7f102043a7540526b95215be938c34c1e`.
- Lanzador, guía y hashes del paquete: `dist/Jugar.command`, `dist/LEEME.txt` y `dist/SHA256SUMS.json`.
- En macOS: doble clic en `dist/Jugar.command`. En BASIC CPC: `RUN"DEVUELTO.BIN"`.

El DSK modular contiene el programa de arranque y cuatro archivos AMSDOS: `CH01.BIN`, `CH02.BIN`, `CH03.BIN` y `CH04.BIN`. Se cargan desde el disco al cambiar de capítulo y se reutiliza memoria del paquete descargado; la campaña no necesita caber en una carga ni permanecer toda en RAM. Esta ruta se recorrió en las tres partidas completas. El DSK debe seguir disponible durante el juego.

## Verificación ejecutada

El manifiesto estructurado `research/release-validation.json` enlaza 10 casos en estado PASS: dos campañas completas Caprice32, una campaña en 1984 v0.4.20 configurado como CPC6128 de 128 KiB, estabilidad de 30:22, PCM, cargas modulares, controles manuales y tres arranques fríos del paquete. Cada campaña completó arenas 1–24 y llegó a la pantalla final; el código de ejecución se verificó contra el BIN y el mapa congelados. El run de estabilidad contiene nueve snapshots de checkpoint y terminó con código 0.

Los tres arranques fríos se hicieron sobre el DSK publicado por `Jugar.command`, no sobre una compilación distinta. Comprobaron menú/inicio, movimiento, salto, devolución, pausa y salida limpia. Además, el lanzador incluido en `dist` se ejecutó directamente: la sesión supervisada acabó con estado PASS y `process_group_absent=true`. El DSK se inspeccionó con `tools/check_campaign_dsk.py`: BIN idéntico, cabecera AMSDOS y checksums válidos, más los cuatro activos de capítulo.

La captura del audio de la fase inicial es PCM real de Caprice, estéreo S16LE a 48 kHz y 66 segundos. El análisis midió 19 bandas de melodía y 27 de bajo, paso estimado de 0,12 s, cero ventanas saturadas y cero silencios imprevistos mayores de 2 s. La captura independiente con música apagada detectó los efectos de salto y devolución; otra secuencia comprueba pausa y recuperación. Se probó señal melódica, bajo, pulso y mezcla a nivel de salida; no se afirma escucha subjetiva ni calidad de altavoces.

El gate se sometió a ocho negativos: rechaza imagen de otra compilación, disco antiguo, sesión incompleta, checkpoints ausentes, lista ambigua de procesos, audio sin melodía, limpieza pendiente y hash de evidencia alterado. Los ocho se rechazaron sin tocar el disco publicado. Validación final:

```sh
python3 tools/validate_release_evidence.py
python3 tools/test_release_gate.py
python3 tools/check_campaign_dsk.py build/campaign/DEVUELTO.dsk build/campaign/DEVUELTO.bin build/campaign/DEVUELTO.map
```

Los reportes completos, PCM, sesiones, snapshots y hashes se conservan bajo `research/runs/`; el manifiesto principal los enumera. No se limpió ni borró evidencia anterior.

## Límites

La entrega es un prototipo técnico jugable con 24 arenas. No contiene todas las escenas narrativas, personajes con reglas propias ni el alcance de producción planeado. La partida completa usa replay determinista; movimiento, salto, devolución, pausa, reintento y nueva partida tienen además pruebas manuales independientes. No se probó en CPC físico, ni se certificaron calidad artística, diversión o respuesta percibida por una persona. La pantalla de FPS de Caprice no se usa como medición de rendimiento del juego.

Al finalizar, se cerraron las sesiones supervisadas y no quedó ventana de Caprice abierta. La salida de audio del Mac volvió a MacBook Air Speakers a volumen 0 y silencio activado, estado previo a la captura.
