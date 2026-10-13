# Decisión 003: recursos CPC canónicos y galería

## Resultado

Se congela una copia verificable de 35 recursos de `assets/cpc-studies/` en
`assets/source/canonical/`. Los builds posteriores consumen esas copias y su
manifiesto; no reconstruyen ni ejecutan Banterhouse 1. La exportación conserva
pantallas `.scr`, paletas, tiles, mapas y sprites en sus formatos nativos.

La validación host reconstruye cada pantalla por tiles/mapa, comprueba las 256
combinaciones de byte Mode 0, las 4 pantallas comprimidas ZX0 y las variantes de
los 3 actores canónicos. Ocho fixtures inválidos se rechazan con el recurso y
campo responsables. Cuatro perfiles CPC autónomos enlazan una página de VRAM
completa y 16 tintas, cargan a `&0100` y verifican en ejecución los 16.384 bytes
copiados a VRAM frente al recurso de origen. La galería queda separada del juego.

## Evidencia en Caprice32

Caprice32 4.6.0, modelo CPC 6128/128 KiB. Se ejecutaron `GAL01.BIN` a
`GAL04.BIN`. Las cuatro pantallas visibles corresponden a Copias, Producción,
Calle y Purple Paper; cada perfil permanece ejecutándose después de la carga y
su bucle compara toda la página de VRAM en cada arranque. La pantalla de error
de comparación no apareció. Los perfiles y sus bytes se verifican con
`make smoke-gallery`.

La tabla de tinta se conserva byte por byte en el binario canónico y se pasa a
`cpct_setPalette(..., 16)`. Para comprobar el estado programado del Gate Array,
se guardó un snapshot SNA con Shift+F3 en cada escena. Caprice32 escribe en el
header SNA los 17 valores `GateArray.ink_values` (16 tintas y borde): así lo
confirma el código de guardado de snapshots en Caprice32
[commit `6c12c4c`](https://github.com/ColinPitrat/caprice32/blob/6c12c4c92360065cdc229ac9ada7551f941436b8/src/slotshandler.cpp#L323-L329)
y el orden de campos del header packed
[en `cap32.h`](https://github.com/ColinPitrat/caprice32/blob/6c12c4c92360065cdc229ac9ada7551f941436b8/src/cap32.h#L103-L127).
El comprobador extrae directamente los 16 registros de tinta del snapshot y los
compara con la paleta canónica enmascarada a cinco bits. Las cuatro escenas
coinciden byte por byte; un fixture que altera una tinta se rechaza. Los
snapshots y hashes están en
`research/runs/20261012T234446Z-T03-snapshot-palette/`; el procedimiento se
repite con `make test-gallery-snapshots`.

Esto acredita el estado del emulador, no la señal analógica de un CPC físico.
La captura visible tampoco certifica CRT o hardware.

## Decisión

Se conservan los perfiles, comprobadores y fixtures. A03/T03 se cierra con la
extracción del estado del Gate Array en SNA. No se usa la galería como prueba de
movimiento, fluidez ni jugabilidad.
