# Disco del juego

[Descarga Devuelto-CPC6128.dsk](Devuelto-CPC6128.dsk). Configura tu emulador como **CPC 6128 de 128 KiB**, monta el disco en A y escribe en BASIC:

```basic
RUN"DEVUELTO.BIN"
```

Mantén el disco montado: la campaña carga cuatro recursos durante la partida. [Controles y guía](../docs/game/PLAYING.md).

Contiene las 24 pantallas del prototipo descrito en el [informe de entrega](../docs/DELIVERY_REPORT.md). La historia completa está pendiente, igual que las pruebas en CPC físico. [manifest.json](manifest.json) guarda el tamaño y el hash del disco.

SHA-256: `034efbab917c1ec318cf25312aa7842d4ff74a4c306a3f48f6890f4995dc1f8c`.

El disco se reconstruye con `make bootstrap` y `make`; el resultado queda en `build/campaign/DEVUELTO.dsk`. El repositorio incluye el código, los recursos y las versiones de las dependencias necesarias. [Instrucciones](../docs/development/GETTING_STARTED.md) · [Créditos](../THIRD_PARTY.md) · [Nota de distribución](../COPYING.md).

El binario enlaza CPCTelera y usa ZX0. Sus avisos se conservan en [LICENSES](../LICENSES/); las fuentes de CPCTelera se descargan desde el commit fijado por el bootstrap. Para reconstruir con una biblioteca modificada, recompila esa biblioteca y ejecuta `make clean` y `make`; no vuelvas a ejecutar el bootstrap sobre el checkout modificado.
