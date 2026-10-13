# 004 — Bucle pop original para AY

> Decisión histórica: esta melodía original fue sustituida el 2026-10-11 por el arreglo local de «Holiday» documentado en la decisión 006, tras recibir el MIDI del usuario.

## Decisión

Sustituir el bucle lento de una sola voz por una composición original para el AY-3-8912. El canal B lleva una frase aguda de 16 pasos en Do mayor; el canal C marca las raíces C–G–Am–F. Cada paso dura cinco interrupciones de 50 Hz, es decir, una semicorchea a 150 BPM. La melodía usa acentos de volumen por paso y el bajo cambia cada cuatro pasos.

La referencia de energía es el pop bailable de los 80 solicitado por el usuario, incluida la energía asociada a «Holiday». No se copian melodías, MIDI, grabaciones ni datos de canciones comerciales. Los efectos conservan el canal A.

## Verificación

- `make package`: compila ensamblador Z80, valida mapa, campañas, assets, catálogo del DSK y reproducibilidad; paquete producido en `dist/Devuelto-CPC6128.dsk`.
- Caprice32 muestra el menú con `MUSICA ON`; el usuario había confirmado que el audio era audible en su entorno.
- La duración y las frecuencias se derivan de los divisores programados; no se hizo una captura o medición acústica independiente de tempo, timbre o volumen.

## Límite

La melodía nueva es una prueba técnica y compositiva pendiente de escucha del usuario. Caprice32 en esta máquina no proporciona una captura de salida AY que permita certificar la calidad percibida. La melodía no es una adaptación de Madonna; incorporar una grabación o composición licenciada requiere que el usuario aporte el activo con derechos de uso para el juego.
