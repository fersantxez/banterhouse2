# Estado del proyecto

13 de octubre de 2026.

## Versión disponible

El [disco publicado](../release/Devuelto-CPC6128.dsk) contiene un prototipo para CPC 6128 con 24 pantallas: movimiento, salto, devolución de papel, máquinas, persecución, pausa, reintento, menú, música AY y final de campaña.

Hay cuatro fondos, uno por capítulo, que se cargan desde el disco y reutilizan la misma zona de memoria. Las 24 pantallas comparten parte de la geometría y todavía no tienen todos los encuentros e ilustraciones del guion.

La primera pantalla usa la física y la colisión continua más recientes. Otras partes conservan reglas anteriores para mantener la demostración que usamos en las pruebas.

## Pruebas realizadas

El [informe de entrega](DELIVERY_REPORT.md) recoge dos campañas completas en Caprice32 y una en 1984, una prueba de estabilidad, arranques desde frío, controles y grabaciones de audio.

El disco probado tiene SHA-256 `034efbab917c1ec318cf25312aa7842d4ff74a4c306a3f48f6890f4995dc1f8c`. El [manifiesto](../research/release-validation.json) enumera las pruebas. Las capturas y grabaciones se conservan en el archivo local `banterhouse2-archive`; para repetir su validación desde un clon hay que recuperarlas o generar pruebas nuevas.

También se ha reconstruido el disco desde una copia limpia, con idéntico resultado. La auditoría del repositorio y los tests de lógica pasaron en GitHub Actions. [Registro de publicación](development/PREPARATION_REPORT.md).

## Pendiente

- Probar en un CPC físico y en distintas variantes de CRTC.
- Jugar con más personas para ajustar dificultad, controles y música.
- Terminar la historia, el reparto y los encuentros descritos en el guion.
- Completar la prueba y la medición de rendimiento de la web publicada. El intento registrado sobre la versión 7 se quedó en el inicio de sesión.

El reloj apunta a 50 pasos de simulación por segundo. Aún no hay una medición publicada que permita afirmar que el juego mantiene esa frecuencia en todas las situaciones.

## Planes anteriores

Los registros T/O, E, F y N corresponden a distintas etapas. Conservan propuestas, fallos y bloqueos de su momento. Para esta entrega, consulta N00–N10 y el informe citado arriba. [Índice de planes](implementation/README.md).
