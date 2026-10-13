# Probar ¡Devuelto! en el CPC virtual

> **Diseño e investigación históricos.** Este documento conserva propuestas y decisiones de su fecha; no describe por sí solo la build actual. Consulta [Estado](STATUS.md) y [la guía de lectura](README.md).

## Ejecutar

En macOS, abre `dist/Jugar.command` (o el `Jugar.command` de la raíz del proyecto). El supervisor abre Caprice32, configura CPC 6128 y monta el mismo DSK publicado. El arranque es automático; espera a que aparezca el menú. Cierra la ventana de Caprice para terminar la sesión.

En CPC real u otro emulador, monta `dist/Devuelto-CPC6128.dsk` y ejecuta `RUN"DEVUELTO.BIN"`. Mantén el disco insertado: la campaña lee `CH01.BIN`–`CH04.BIN` al entrar en cada capítulo y reutiliza la memoria del paquete anterior. No se requiere que todo el contenido de la campaña quepa en una sola carga o permanezca a la vez en RAM.

## Teclas

- En el menú, ↑/↓ cambia la opción y Espacio o X confirma. D inicia la demo de 24 arenas; R vuelve al menú.
- ←/→ corre y orienta a Pitu; ↑ salta; ↓ baja atravesando una plataforma.
- Espacio o X usa el sello «DEVUELTO» y confirma las pantallas de avance.
- P pausa y reanuda; R reinicia la arena actual.
- Tras completar el juego, Espacio comienza una nueva partida.
- Joystick 0: direcciones; arriba salta; fuego devuelve.

## Qué se ha probado

La compilación distribuida completó las 24 arenas desde arranque frío en dos campañas independientes de Caprice32 y una en 1984 v0.4.20, configurado como CPC 6128 clásico de 128 KiB. La campaña recorrió los cuatro paquetes del disco. Tres arranques fríos adicionales verificaron el DSK empaquetado, el comienzo, controles, pausa, salida y limpieza. La suite también prueba reintento y nueva partida en la ruta de controles manuales.

La música se validó con PCM capturado de la salida de Caprice: 66 s con alturas cambiantes en melodía y bajo, pulso cercano a 125 BPM y sin silencios no previstos mayores de 2 s. Con música desactivada, la captura detectó los efectos de salto y devolución; la pausa silencia y luego recupera la salida. La presencia tonal está medida; no se ha certificado la escucha subjetiva ni el sonido de altavoces físicos.

Los resultados con hashes están en `research/release-validation.json`; el informe resumido está en `docs/DELIVERY_REPORT.md`. El prototipo no contiene aún todas las escenas narrativas del plan de campaña y no se ha probado en un CPC físico. La evaluación de diversión, dificultad y calidad artística necesita una sesión humana.
