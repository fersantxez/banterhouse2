# 006 — Arreglo local de «Holiday» para AY

Fecha: 2026-10-11

## Decisión

Tras la petición del usuario, sustituir el bucle original de la decisión 004 por un arreglo corto basado en la pista MIDI de «Holiday» enlazada por el propio usuario en [Midis101](https://www.midis101.com/free-midi/82532-madonna-hollyday). La conversión toma ocho compases de la pista «Madonna» y la pista «Bass», cuantiza ambas a semicorcheas y las reproduce en los canales B y C del AY; los efectos siguen reservados en el canal A.

El usuario ha autorizado también usar, para esta copia personal y exclusiva, estos MIDIs como candidatos para futuras versiones del arreglo: [Like a Virgin (90532)](https://www.midis101.com/free-midi/90532-like-a-virgin-madonna), [La Isla Bonita (82543)](https://www.midis101.com/free-midi/82543-madonnalaislabonita), [Like a Virgin (82544)](https://www.midis101.com/free-midi/82544-madonnalikeavirgin) y [Holiday (82532)](https://www.midis101.com/free-midi/82532-madonna-hollyday). La integración y escucha de alternativas se hará al habilitar T17; no se afirma que estas páginas otorguen licencia de redistribución.

El 2026-10-12 se descargaron las otras tres opciones a la carpeta privada ignorada por Git y se comprobó su estructura SMF: 90532 tiene pistas «Melody» y «Bass»; 82543 y 82544 contienen notas, pero sus pistas no tienen nombre y son fragmentos mucho más cortos. Sus tamaños y SHA-256 están en `research/runs/20261012T-madonna-midi-intake/results.json`. Este inventario no cambia la selección musical ni acredita una escucha; T17 decidirá qué fragmentos funcionan en AY.

El archivo MIDI fuente permanece en `assets/audio/private/`, ignorado por Git. `tools/build_holiday_ay.py` genera la tabla ensamblador local `src/platform/music.s`; esa tabla ya basta para compilar el candidato. El fragmento se reproduce a seis ticks de 50 Hz por semicorchea (125 BPM), cerca de los 123 BPM del MIDI. Se conserva el fragmento instrumental original como datos del build personal; no se empaqueta ni publica el MIDI fuente.

## Derechos y alcance

La ficha ofrece el archivo como descarga gratuita, pero no encontramos una licencia expresa que autorice redistribuir la composición o el MIDI. La petición se entiende como autorización para integrar el material en la copia privada y exclusiva del usuario. No subir el MIDI, el DSK con esta música ni el código de tablas a un repositorio o publicación pública. Esta nota registra el alcance de producto y no es una conclusión jurídica sobre excepciones de derechos de autor.

## Verificación pendiente

- El generador valida que existan las pistas nombradas y que el fragmento incluya notas de melodía y bajo.
- `make build`, `make test` y el empaquetado deben pasar después de regenerar la secuencia.
- La música debe escucharse en un CPC o emulador con audio funcional. El Caprice de esta máquina había reportado fallo de `AudioQueueStart`, así que compilar la secuencia no demuestra que el sonido resulte rápido, reconocible o agradable.
- T17 y la aceptación humana del audio siguen pendientes conforme al plan.
