# Cómo jugar a ¡Devuelto!

[Volver a la guía](../README.md) · [La historia](STORY.md)

## La misión

Eres Pitu. Las máquinas de la agencia escupen encargos y tú llevas un sello: **DEVUELTO**. Muévete entre plataformas, salta para colocarte y devuelve el papel en el momento adecuado. Los encargos devueltos sirven para apagar máquinas. Al resolver la arena puedes pasar a la siguiente.

La campaña técnica tiene 24 arenas, agrupadas en cuatro capítulos. Todavía es un prototipo: la historia completa, los encuentros narrativos y buena parte del reparto ampliado son planes de producción.

## Cargar el disco

Necesitas un emulador configurado como **Amstrad CPC 6128 clásico, 128 KiB**, o el equipo objetivo. El funcionamiento en hardware físico aún no está verificado.

1. Descarga [el DSK incluido](../../release/Devuelto-CPC6128.dsk) y móntalo en la unidad A. Si lo has compilado tú, está en `build/campaign/DEVUELTO.dsk`.
2. En la pantalla BASIC escribe `RUN"DEVUELTO.BIN"` y pulsa Intro.
3. Espera a la portada y al menú. Selecciona jugar y confirma con Espacio.

**Deja el disco montado.** El juego lee `CH01.BIN`–`CH04.BIN` al cambiar de capítulo. Una copia suelta del BIN no contiene toda la campaña.

El disco validado está incluido en `release/`, junto a su manifiesto. No se incluyen ejecutables de emulador ni ROM. [La guía de compilación](../development/GETTING_STARTED.md) explica cómo reconstruirlo desde las fuentes.

## Controles

| Tecla | Acción |
|---|---|
| ← / → | Mover a Pitu y orientar la devolución |
| ↑ | Saltar; mantener influye en el salto |
| ↓ | Bajar de una plataforma que lo permita |
| Espacio / X | Devolver; confirmar en menús y entre arenas |
| P | Pausar o continuar durante la partida |
| R | Reiniciar la arena durante la partida |
| M, en el menú | Activar o desactivar la música |
| D, en el menú de campaña | Ejecutar el recorrido automático de demostración |

También se leen las direcciones y el botón de disparo del joystick 0. La demostración es una prueba determinista; no sustituye una partida con tus propias decisiones. R sale de ella y vuelve al inicio.

## Primer minuto

Observa de dónde sale el papel. Acércate para aprender la distancia del sello, devuélvelo mirando hacia la máquina y prueba otra posición si el disparo pasa por encima. El sello tiene una breve recuperación: pulsarlo sin parar no equivale a mantener un escudo.

Si pierdes, suelta y vuelve a pulsar la acción para reintentar. Si aparece un error de disco, comprueba que sigue montado el DSK correcto y pulsa acción para reintentar la carga.

## Edición web

La [página de desarrollo](https://banterhouse-2-devuelto.freshkid64.chatgpt.site/) ejecuta el disco en un emulador de navegador. Actualmente requiere acceso con la cuenta autorizada. Publicar este código en GitHub no cambia ese acceso. La medición completa de rendimiento de esa publicación sigue pendiente; consulta [el estado](../STATUS.md).
