# T07 — Simulación compartida y colisión estática

**Resultado:** PASS para S01–S03 y el nivel M0 mínimo. **Fecha:** 2026-10-13.

El estado físico se conserva como campos tipados y la persistencia usa una codificación little-endian explícita de 19 bytes; no depende del padding de `struct`. `src/core/player.c`, `collision.c` y `state.c` son el mismo C para host y SDCC. La escena `assets/levels/m0.json` se creó para T07 con dos plataformas y después T08 la amplió a cinco marcas de recorrido. `tools/build_m0_level.py` valida IDs, tipos, límites, dimensiones, apoyo del spawn y coincidencia exacta con la geometría/spawn de `arena_01` antes de generar una tabla CPC fija. El juego conserva su campaña de 24 arenas.

`make test-sim` ejecuta el exportador y cinco casos negativos del JSON; compila el fixture M0 con ASan/UBSan; ejecuta las pruebas host de física; compila el fixture Z80 y verifica el DSK; y ejecuta el estrés host de 24 arenas.

Resultados:

- `make test-sim`: PASS. El estado serializado coincide con centinelas negativos/límites; no aparecen errores de ASan/UBSan.
- M0 con el `player_step` de producción: salir por el borde elimina el apoyo y aplica gravedad en el tick; la caída termina en el suelo sólido declarado. Las marcas son `one_way`. La corrida T08 amplió el caso a cinco marcas; resultados en `research/runs/20261013T-T08-motion/results.json`.
- Fixture Z80 de Caprice previo: `research/runs/20261012T230000Z-F04-core-physics/results.json` registra máscara `0FFF`, incluyendo codificación round-trip, gravedad, paso ascendente por one-way, aterrizaje descendente, paredes/techo y orden independiente de tabla. Los SHA-256 de `player.c`, `collision.c`, `state.c` y headers actuales coinciden con ese fixture. La configuración de salto y el test cambiaron después; por tanto, el resultado CPC se usa sólo para los casos comunes, no para afirmar esos cambios posteriores.
- `research/runs/20261012T235500Z-F07-physics-campaign/results.json`: el mismo core produjo 2.400.000 ticks de estrés host y una comparación host/Z80 de 256 ticks con 16 checkpoints iguales (`B0D5`). Es una prueba CPC emulada, no hardware real.

El target `test-physics-cpc` construye y valida el disco; no ejecuta Caprice por sí solo. La comparación CPC ejecutada está referenciada por F04/F07. Esto cierra T07, pero no acredita la sensación de control H0 ni resuelve todo el alcance de la campaña.
