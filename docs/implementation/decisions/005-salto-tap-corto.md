# Ajuste experimental del salto por pulsación breve

Fecha: 2026-10-11

## Síntoma

En las pruebas de juego, Pitu parecía quedarse suspendida y no alcanzaba de forma fiable las plataformas. La implementación anterior recortaba la velocidad ascendente a −4 unidades Q1 tan pronto como se soltaba Arriba. Una pulsación breve podía terminar el ascenso antes de ganar la altura necesaria para salvar los 24 píxeles entre apoyos.

## Cambio candidato

Al aceptar un salto se conserva un mínimo de siete ticks de ascenso antes de aplicar el corte al soltar. El flanco sigue iniciando un único salto; mantener la tecla no genera saltos nuevos. El estado también recibe el nivel actual de Arriba del teclado o del joystick, y el contador se limpia al aterrizar o al tocar el límite superior.

Con las ecuaciones actuales de Q1 (impulso −10, gravedad +1 y corte −4), la reproducción discreta alcanza 28 píxeles de altura y puede cruzar el apoyo de 24 píxeles si existe solape horizontal. La cifra es una simulación de la lógica; no es una medición de la sensación de juego ni una aprobación H0. Las plataformas son unidireccionales y el aterrizaje aún necesita validar el recorrido completo en una sesión humana.

## Evidencia y límites

- `make build` y `make test`: exit 0; se ejecutan los validadores de assets, mapa, disco, lógica de plataforma y reproducibilidad.
- DSK empaquetado: `dist/Devuelto-CPC6128.dsk`, 204544 bytes, SHA-256 `d30ff7dfa378b58ae039379f958163c5ec64829e8c6650641450bdda9731b014`.
- Caprice32 4.6.0 arranca con música y menú; el escenario aparece y Pitu se muestra en el punto inicial. La captura retardada no ofrece una traza por tick del arco ni verifica aterrizajes en plataformas.
- T08 continúa pendiente: sus dependencias T07 y la revisión humana H0 no están cerradas. El ajuste es un arreglo provisional del prototipo, no un cierre de contrato ni prueba de que el recorrido M0 sea divertido o resoluble.
