# Disco jugable verificado en emulación

> **Entrega pendiente de reparación (12 de octubre de 2026):** el usuario informa fallos de los BIN y música insuficiente. La aceptación anterior está retirada. Las verificaciones descritas debajo son históricas y no certifican la entrega actual. Seguir el [plan autónomo](AUTONOMOUS_REPAIR_PLAN.md); su implementación todavía está pendiente.


Registro del 12 de octubre de 2026 (13 de octubre UTC). Sustituye el candidato anterior. Alcance: prototipo de 24 arenas para CPC 6128 clásico de 128 KiB; no cierra la campaña narrativa ni los gates humanos del plan.

## Abrir

Doble clic en `Jugar.command` desde Finder. Abre la aplicación local Caprice32 y monta **dist/Devuelto-CPC6128.dsk**. Esperar hasta 20 segundos; RUN e Intro son automáticos. `make run` abre ese mismo disco; `make run-candidate` abre build. En otro emulador CPC 6128: montar DSK y ejecutar `RUN"DEVUELTO.BIN"`.

Espacio empieza. Flechas mueven, Arriba salta, Abajo atraviesa plataformas, X/Espacio devuelve, P pausa y R reinicia. D en el menú ejecuta la demo completa; R la cancela. La última sesión quedó en la primera arena pausada: P continúa.

## Artefacto comprobado

- DSK: 204544 bytes; SHA-256 `667d79479f899607155e5de96c000f995b404ca8f7b56dd3c96b16763e41812a`.
- BIN: 30646 bytes; carga `&0100`, entrada `_main` en `&265F`.
- Código/recursos `&0100–&6EE1`; datos `&7800–&78B5`; tope de pila `&7FF0`. Mapa estático sin solapamientos; no constituye medición de máximo uso de pila.
- Caprice32 4.6.0, modelo 2 / 128 KiB / velocidad 4. Hashes de emulador, ROM y configuración en `research/runs/20261013T-E03-emulator-campaign/launch.json`.

## Pruebas realizadas

`make test` terminó con código 0. Incluye simulación del juego real con ASan/UBSan, combate, física, recursos, geometría, mapa, extracción AMSDOS y comparación del BIN/DSK incremental con una compilación limpia. `test_game_build.py` comprueba que cambiar cabeceras de física, niveles o replay recompila los objetos Z80.

Controlando el emulador se ejecutó el mismo DSK desde arranque frío y menú hasta **24/24 arenas, WIN, 36375 puntos, 7177 ticks de entrada y una vida restante**. La demo sólo alimenta controles al mismo `game_tick`; no teletransporta, desactiva daños ni salta fases. El snapshot final verifica todos los marcadores de fase y compara código/recursos cargados contra el BIN. Se comprobó después Espacio → nueva partida.

Además se probaron manualmente ayuda, música ON/OFF, movimiento, salto, pausa/reanudación, R, derrota y reintento. Dos snapshots separados durante pausa conservan idénticos jugador, papeles, máquinas, ticks, modo, vidas y puntuación. El inicio tras victoria vuelve a fase 1, puntuación 0 y dos vidas.

`test_release_gate.py` rechazó evidencia ausente, otro hash, suite fallida, control pendiente, evidencia alterada y snapshot final ausente. `package_release.py` copió los bytes acreditados. Se abrió el lanzador final desde Finder y se observaron menú automático y partida de **dist**. Los tres arranques del candidato final (recorrido, menú/ayuda y paquete) llegaron al juego.

Evidencia principal: [release-validation.json](../../research/release-validation.json), resultado final (`research/runs/20261013T-E03-emulator-campaign/campaign-final.json`; archivo local de evidencia), pantalla final (`research/runs/20261013T-E03-emulator-campaign/campaign-final.png`; archivo local de evidencia), arranque de entrega (`research/runs/20261013T-E04-packaged-boot/results.json`; archivo local de evidencia).

## Fallos corregidos y límites

El build omitía dependencias de cabeceras: el Z80 conservaba salto -410 y el host usaba -450. La traza detectó la primera divergencia en el tick 72; recompilar y comparar una build limpia corrigió la ruta. También se corrigieron devolución en dirección equivocada, cadencia desbordada, salida inaccesible por condición contradictoria, máquinas dibujadas fuera de sus posiciones, clipping de papeles, pausa y feedback terminal. Durante la reparación se detectó un HUD de 80 bytes incompatible con el máximo 64 de `cpct_drawSolidBox`; ahora son dos bloques de 40, con una aserción host que cubre la restricción.

El alcance sigue siendo cuatro escenarios reutilizados en 24 arenas. Faltan escenas narrativas, nuevos encuentros, carga de paquetes por caras y pulido de presentación. Hay actualización directa visible durante el dibujo; no se certifica ausencia de parpadeo/tearing ni una frecuencia de juego a partir del OSD de Caprice. Diversión, dificultad, escucha/mezcla AY, segundo emulador y CPC físico permanecen pendientes. El log actual indica `Sound buffer ready`, no una prueba auditiva.

El arreglo AY de Holiday y las referencias MIDI se mantienen para uso personal local; esta entrega no publica archivos ni los sube a servicios.
