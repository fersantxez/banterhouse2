# Banterhouse 2 · ¡Devuelto!

Banterhouse 2 es un arcade para el **Amstrad CPC 6128 de 128 KiB**. Pitu y Alberto vuelven a la agencia de [Banterhouse](https://github.com/fersantxez/banterhouse), aunque esta vez se juega de otra manera: hay que saltar entre plataformas y devolver los papeles que disparan las máquinas hasta conseguir apagarlas.

La idea viene de las ganas de hacer un juego como los que recordamos del CPC: rápido, con controles sencillos y un sonido para cada salto y cada acierto. Chuckie Egg fue una de las primeras referencias. Los personajes vienen de *Creatas y Ejecutas*; el color y los guiños a Prince, del pop de los ochenta.

![Pantalla de carga de Banterhouse 2](assets/loading/banterhouse2-loading-preview.png)

*Pantalla de carga en Mode 0, ampliada a proporción 4:3.*

## Jugar

El [disco incluido](release/Devuelto-CPC6128.dsk) contiene **24 pantallas repartidas en cuatro capítulos**, música, efectos y una demostración que recorre la campaña. Monta el DSK en un emulador configurado como CPC 6128 y escribe:

```basic
RUN"DEVUELTO.BIN"
```

Deja el disco montado: el juego carga el fondo de cada capítulo cuando lo necesita. En la [guía para jugar](docs/game/PLAYING.md) están los controles y las instrucciones completas.

Es un prototipo. Se ha completado en emuladores, pero queda trabajo de diseño, gráficos e historia y todavía no se ha probado en un CPC físico. El [estado del proyecto](docs/STATUS.md) recoge lo que funciona y lo que falta.

## La historia

Alberto ha prometido una campaña en todos los formatos para antes de las seis. El Presidente pone en marcha una máquina para organizar el trabajo, y cada corrección acaba generando más encargos. Pitu decide devolver el original a quien lo firmó.

La historia pasa por reprografía, producción y la calle antes de llegar a la presentación al cliente. [El argumento y los personajes](docs/game/STORY.md) están descritos aparte; aún no está todo incorporado al juego.

## Desarrollo

Está escrito en C y ensamblador Z80, con CPCTelera. Incluimos el código, los recursos y las herramientas necesarias para reconstruir el disco.

- [Compilar el juego](docs/development/GETTING_STARTED.md)
- [Código y funcionamiento](docs/development/ARCHITECTURE.md)
- [Gráficos y música](docs/development/ASSETS_AND_AUDIO.md)
- [Pruebas](docs/development/TESTING.md)
- [Índice de documentación](docs/README.md)

[Colaborar](CONTRIBUTING.md) · [Créditos](THIRD_PARTY.md) · [Licencias](COPYING.md)
