# Estado del proyecto

Fecha de esta revisión documental: 13 de octubre de 2026.

## Qué existe

Un prototipo arcade CPC 6128 de 24 arenas. Hay movimiento, salto, devolución, máquinas, persecución, pausa, reintento, menú, música AY y final de campaña. El disco contiene el programa y cuatro recursos de capítulo; el motor reutiliza memoria al cargarlos.

La primera arena incorpora la reparación de física y colisión continua. Parte de la campaña conserva reglas heredadas para mantener el replay de validación. No debe interpretarse el número de arenas como 24 composiciones narrativas finales distintas.

## Qué se verificó anteriormente

El [informe de entrega](DELIVERY_REPORT.md) registra dos recorridos completos en Caprice32 y uno en 1984, una sesión de estabilidad, arranques fríos, controles y salida PCM. Es evidencia asociada a un disco concreto, no una certificación automática de cada modificación futura.

El DSK de referencia tiene SHA-256 `034efbab917c1ec318cf25312aa7842d4ff74a4c306a3f48f6890f4995dc1f8c`. El [manifiesto de validación](../research/release-validation.json) enumera las pruebas. Las capturas, ROM, audio y registros completos permanecen en el archivo externo local `banterhouse2-archive`, fuera del repositorio. Un clon público no contiene ese archivo y no puede volver a validar sus hashes sin obtenerlo o generar pruebas nuevas.

## Qué queda pendiente

- Pruebas en CPC físico y distintas variantes de CRTC.
- Evaluación de diversión, control y calidad musical con jugadores.
- Producción narrativa y artística del alcance descrito en la historia.
- Prueba completa y medición de la versión web publicada: la versión 7 se desplegó, pero el navegador de prueba quedó en el inicio de sesión.

La cadencia objetivo de simulación de 50 Hz, los cuadros del navegador y el FPS del emulador son medidas distintas. No se publica aquí un rendimiento real del juego que no se haya medido.

## Cómo leer los planes antiguos

Los documentos de investigación describen hipótesis. Los estados T/O, E, F y N corresponden a distintas etapas y pueden conservar bloqueos históricos. Para la entrega del prototipo prevalecen el informe citado y el seguimiento N00–N10; para un cambio nuevo deben generarse pruebas nuevas. [Índice del seguimiento](implementation/README.md).

[Volver a la guía](README.md)
