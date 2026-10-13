# Cómo jugar a ¡Devuelto!

[Documentación](../README.md) · [La historia](STORY.md)

## Objetivo

Eres Pitu. Las máquinas de la agencia escupen encargos y tú llevas un sello: **DEVUELTO**. Muévete entre plataformas, salta para colocarte y devuelve el papel en el momento adecuado. Los encargos devueltos sirven para apagar máquinas. Al resolver la arena puedes pasar a la siguiente.

El prototipo tiene 24 pantallas en cuatro capítulos. Faltan los encuentros, las viñetas y parte de los personajes previstos en el guion.

## Cargar el disco

Necesitas un emulador configurado como **Amstrad CPC 6128 clásico, 128 KiB**, o el equipo objetivo. El funcionamiento en hardware físico aún no está verificado.

1. Descarga [el DSK incluido](../../release/Devuelto-CPC6128.dsk) y móntalo en la unidad A. Si lo has compilado tú, está en `build/campaign/DEVUELTO.dsk`.
2. En la pantalla BASIC escribe `RUN"DEVUELTO.BIN"` y pulsa Intro.
3. Espera a la portada y al menú. Selecciona jugar y confirma con Espacio.

**Deja el disco montado.** El juego lee `CH01.BIN`–`CH04.BIN` al cambiar de capítulo. Una copia suelta del BIN no contiene toda la campaña.

El emulador y sus ROM se instalan aparte. Si quieres compilar el juego, sigue [estas instrucciones](../development/GETTING_STARTED.md).

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

También puedes usar el joystick 0: direcciones y botón de disparo. D reproduce una partida grabada como secuencia de controles; R sale de la demostración y vuelve al inicio.

## Al empezar

Observa de dónde sale el papel. Acércate para aprender la distancia del sello, devuélvelo mirando hacia la máquina y prueba otra posición si el disparo pasa por encima. El sello tiene una breve recuperación: pulsarlo sin parar no equivale a mantener un escudo.

Si pierdes, suelta y vuelve a pulsar la acción para reintentar. Si aparece un error de disco, comprueba que sigue montado el DSK correcto y pulsa acción para reintentar la carga.

## Edición web

La [web del juego](https://banterhouse-2-devuelto.freshkid64.chatgpt.site/) ejecuta el disco en el navegador. El acceso requiere la cuenta autorizada, aunque el repositorio de GitHub sea público. La prueba completa de rendimiento web sigue pendiente; está anotada en [Estado](../STATUS.md).
