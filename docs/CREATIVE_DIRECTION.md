# Dirección creativa

> Notas de diseño del 10 de octubre de 2026. El [estado del proyecto](STATUS.md) indica qué se ha implementado.

## La secuela

Banterhouse 2 conserva los personajes y añade otros, pero su forma de jugar se diseña desde cero. Las habitaciones, reglas, cámara, contadores y ritmo del primer juego no son requisitos para esta segunda parte.

La petición es hacer un juego rápido, divertido y con respuesta inmediata, y dedicar el mismo cuidado a los gráficos y al sonido. Chuckie Egg fue la referencia que puso el usuario: moverse y saltar resultaba agradable incluso con gráficos sencillos. Ese recuerdo sirve para orientar las pruebas; no se han medido aquí sus tiempos ni se ha revisado su audio.

## Aspecto

El sprite de Pitu es la referencia principal. Hay que conservar su identidad, sus proporciones y su silueta al dibujar poses nuevas. El resto del reparto, los fondos y los efectos deben encajar con él.

La estética pedida es la de un videojuego de los ochenta, muy pop: colores planos, cian, magenta, amarillo y lima, con negro y blanco para separar figuras. Las paletas se ajustan al CPC y se comprueban junto a Pitu, a tamaño de juego.

Prince es la referencia cultural principal. Se proponen también guiños a Madonna, Bowie, Haring y Memphis en carteles, objetos y escenarios. Están detallados en [GAME_REFERENCES](GAME_REFERENCES.md). El apartado de [arte](GAME_DESIGN.md#10-arte-y-puesta-en-escena) describe su uso por capítulo.

## Controles y ritmo

- Moverse, frenar, cambiar de dirección y saltar debe resultar predecible. La animación no debe retrasar la acción.
- Cada acción necesita una señal visual y sonora breve. La música debe dejar oír saltos, aciertos y avisos de peligro.
- Las amenazas deben verse con tiempo para reaccionar. El jugador debe poder entender por qué ha perdido.
- Tiene que haber motivos para moverse: elegir una ruta, colocarse para devolver o evitar un perseguidor. Subir la velocidad de Pitu no basta.
- El reintento debe ser rápido. Las cargas y animaciones de derrota no deben repetirse en cada intento si se pueden evitar.
- Las reglas deben ser fáciles de aprender y permitir mejorar con la práctica.

Estos criterios se comprueban jugando. Siguen pendientes las pruebas con jugadores.

## Propuesta elegida

[¡Devuelto!](GAME_DESIGN.md) propone saltar, esquivar y devolver proyectiles para apagar máquinas. Primero se prueban tres versiones pequeñas:

| Prueba | Contenido |
|---|---|
| M0 | Movimiento, salto y sonidos |
| M1 | Devolución contra una máquina |
| M2 | Tres máquinas, un perseguidor y un rebote opcional |

El [plan de prototipos](PROTOTYPE_PLAN.md) describe las pruebas. Los parámetros, la cámara y el alcance de la campaña se ajustarán con sus resultados.

Antes se consideraron dos alternativas: recoger objetos y escapar, o transportar y lanzar objetos entre puntos. Se conservan por si devolver proyectiles no funciona. No hay que producir tres juegos a la vez.

En cada prueba se anotan dudas sobre los controles, errores que no se entienden, rutas distintas entre intentos y ganas de repetir. Después se añade el arte y el sonido de una pantalla completa y se vuelve a probar: las animaciones y efectos pueden cambiar la respuesta o dificultar la lectura.

## Decisiones técnicas

Pantalla fija, scroll, doble búfer y motor híbrido siguen siendo opciones que hay que comparar con la misma escena. La oficina del primer juego puede servir para ensayos técnicos, pero no fija el diseño de la secuela.

Hay que medir por separado el tiempo entre pulsar y cambiar el estado, ver la acción y oírla. Leer el teclado a 50 Hz no asegura que la imagen responda a esa frecuencia. También influyen el emulador y sus buffers.

La presentación a 50 Hz es un objetivo por comprobar. Si una versión sólo alcanza 25 Hz, hay que probar su respuesta y ajustar dibujo, efectos o cantidad de objetos antes de aceptarla.

Al comparar con otros juegos, indica la versión CPC, cómo se consultó —jugando, viendo una grabación o leyendo instrucciones— y qué se observó. Las [referencias](GAME_REFERENCES.md) conservan las fuentes usadas hasta ahora.
