# 008 — Tema original de 16 compases para AY

Estado: candidato N06; PCM de Caprice y revisión de escucha aún pendientes en N07.

La melodía temporalmente usada de «Holiday» se conserva como antecedente privado, documentado en `006-holiday-ay-local.md`; el juego pasa a un tema original porque la secuela necesita una identidad musical propia y más clara que el ritmo aislado. No se distribuye ni se transforma el MIDI fuente en este arreglo nuevo.

El arreglo dura 16 compases a 125 BPM. La forma alterna un gancho de cuatro compases, su respuesta más aguda, un puente de cuatro compases y una resolución. El canal B lleva la melodía sincopada. El canal C alterna raíces graves con notas de arpegio y terceras del acorde. El canal A conserva los SFX con prioridad. Así hay melodía, bajo y armonía rítmica sin fingir cuatro voces simultáneas ni cortar los efectos.

Cada semicorchea ocupa seis ticks de la simulación de 50 Hz (120 ms); las 256 entradas forman un loop de 30,72 s. `tools/build_pop_ay.py` genera `src/platform/music.s` de forma determinista. Su prueba host verifica longitud, rangos, variación, volumen y direccionamiento de las 256 entradas. Esto acredita la secuencia y el ABI ensamblado previsto, no que el emulador saque PCM, que se oiga por los altavoces o que la valoración artística sea satisfactoria. La salida del runtime, convivencia con SFX y música al entrar desde la portada se validan por separado en N07.
