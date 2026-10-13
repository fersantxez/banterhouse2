# Dirección de Banterhouse 2: un juego nuevo

> **Diseño e investigación históricos.** Este documento conserva propuestas y decisiones de su fecha; no describe por sí solo la build actual. Consulta [Estado](STATUS.md) y [la guía de lectura](README.md).

Aclaración del usuario, 10 de octubre de 2026. Este documento prevalece sobre las recomendaciones anteriores que favorecían continuar la dinámica del primer Banterhouse.

## Mandato creativo

Banterhouse 2 conserva los personajes e incorpora personajes nuevos. **Su dinámica se diseña desde cero y debe tener identidad jugable propia.** El primer juego aporta continuidad de personajes y material técnico que se puede estudiar; sus habitaciones, reglas, cámara, contadores, tamaño de sprites y ritmo no son requisitos de la secuela.

La aspiración es un juego CPC extraordinariamente divertido, rápido y con respuesta inmediata, acompañado de un despliegue técnico, gráfico y artístico importante. Las dos ambiciones deben convivir: construir una base jugable excelente y demostrar que mantiene sus cualidades al incorporar el arte, la animación, el sonido y los efectos finales.

El usuario señala **Chuckie Egg** como referencia de experiencia: placer al moverse, saltar, recoger y escuchar una respuesta a las acciones. Esta es la descripción y motivación del usuario, no una auditoría histórica de las reglas, sonidos o tiempos de ese juego. No implica hacer un clon ni decidir ya que Banterhouse 2 será de plataformas.

## Dirección estética fijada por el usuario

**El sprite de Pitu es la base. Estética de videojuego de los 80, súper pop.** Escenarios, reparto, efectos, tipografía y presentación deben compartir su lenguaje de bloques de píxel, siluetas fuertes y color contundente. Preservar identidad y proporciones del sprite canónico; construir el mundo a su alrededor.

La dirección visual utiliza masas planas, cian, magenta, amarillo y lima, contraste con negro y blanco, geometría atrevida y rótulos exagerados. Las combinaciones exactas se adaptan a la paleta CPC y se prueban junto a Pitu. El detalle y los efectos deben conservar la lectura de las acciones. El [diseño del juego, sección 10](GAME_DESIGN.md#10-arte-y-puesta-en-escena), concreta esta dirección para los cuatro capítulos.

El usuario pide además referencias a **Prince e iconos de los 80**. Prince será la referencia cultural principal, con guiños reconocibles en carteles, utilería, escenarios y dirección musical. Madonna, Bowie, Haring y Memphis son la selección secundaria propuesta. Pitu conserva su identidad y sigue fijando el lenguaje gráfico. El diseño concreta la pantalla «Purple Paper» y las [fuentes culturales](GAME_REFERENCES.md#referencias-culturales-y-visuales-de-los-80).

## Lo que debe funcionar desde el primer minuto

- **Control:** empezar a moverse, detenerse y cambiar de intención de forma predecible. Aceleración, inercia y control aéreo, si existen, se eligen por cómo se juegan; no se heredan del original.
- **Acciones satisfactorias:** cada verbo principal debe ser agradable de ejecutar incluso antes de sumar puntos. Si hay salto, explorar arco, altura y aterrizaje; si hay lanzamiento, explorar dirección, impacto y recuperación.
- **Respuesta audiovisual:** señales breves y reconocibles para acciones, éxito y peligro. Diseñar SFX desde el primer prototipo. La música, los pasos repetidos y otros sonidos deben dejar oír la información útil; no añadir ruido continuo por obligación.
- **Decisiones durante el movimiento:** rutas, riesgo, persecución, oportunidad o encadenamiento. La rapidez no se obtiene únicamente subiendo la velocidad del personaje.
- **Claridad y justicia:** leer amenazas, entender por qué se ha fallado y poder atribuir un acierto al propio control. El decorado y los efectos deben mantener claras las siluetas y superficies relevantes.
- **Reintento:** volver a jugar con pocas esperas; las cargas y las animaciones de derrota no pueden romper constantemente el ritmo.
- **Dominio:** reglas que se comprenden pronto y admiten aprender recorridos, afinar acciones y asumir riesgos mayores. La puntuación apoya ese aprendizaje, no lo sustituye.

Son criterios de diseño, todavía sin validar en pruebas de juego. No se declara «adictivo» un prototipo por tener coleccionables, combos o una tasa alta de cuadros.

## Propuesta concreta tras la petición de diseñar el juego

[¡Devuelto!](GAME_DESIGN.md) desarrolla la dirección de **esquivar y devolver** como plataformas arcade: salto libre, un gesto que devuelve proyectiles, máquinas que apagar, rutas alternativas y reintento breve. Es la propuesta actual del diseño, todavía pendiente de probar; no una aprobación del usuario a cada regla o parámetro.

La exploración se concentra ahora en tres pruebas sucesivas: M0 movimiento y sonidos, M1 devolución contra una máquina, M2 una pantalla con tres máquinas, perseguidor y rebote opcional. El [plan de prototipos](PROTOTYPE_PLAN.md) concreta ese orden. Cámara completa y campaña de cuatro capítulos son hipótesis condicionadas a las partidas.

## Exploración inicial conservada como alternativas

Antes de concretar ¡Devuelto! se propusieron los siguientes bucles. Se conservan como alternativas si falla la mecánica central; ya no se pide desarrollar los tres en paralelo:

| Experimento | Bucle a explorar | Pregunta principal |
|---|---|---|
| Recoger y escapar | Recorrer plataformas o rutas conectadas, recoger objetivos y evitar perseguidores | ¿Elegir y ejecutar un recorrido resulta divertido y permite mejorar? |
| Transportar y encadenar | Llevar/lanzar objetos entre puntos mientras cambian oportunidades y obstáculos | ¿Combinar movimiento y entregas produce decisiones ágiles y acciones satisfactorias? |
| Esquivar y devolver | Evitar amenazas, aprovechar ventanas y devolverlas o redirigirlas | ¿La relación entre movimiento, precisión y respuesta audiovisual sostiene el juego? |

Cualquier prueba de estas alternativas tendrá un espacio pequeño, uno o dos verbos, una amenaza, una condición de éxito/fallo, reintento inmediato y SFX básicos. Empezar con gráficos legibles y movimiento cuidado; no producir niveles ni arte final de tres juegos distintos. Los personajes deben aportar personalidad y posibilidades de interacción a las reglas que prosperen.

Probarlos con sesiones cortas y registrar observaciones: dudas sobre controles, acciones que se repiten por placer, errores incomprensibles, ocasiones de elegir otra ruta y ganas expresadas de repetir. Las pruebas automáticas verifican consistencia; **la diversión requiere jugar**. La evaluación del usuario y de jugadores reales queda pendiente, sin inventar testimonios.

Para la propuesta actual, construir después una muestra con arte y sonido ambiciosos y volver a probar. Una figura provisional muy ágil no demuestra que la versión con animación final conserve esa respuesta. La animación puede comunicar una acción inmediatamente sin obligar a esperar a que termine una pose decorativa para ejecutarla.

## Consecuencias técnicas

El motor híbrido, la pantalla única, el doble búfer y el scroll siguen siendo candidatos. Su selección depende de las reglas y de la cámara que las haga funcionar mejor. La escena anterior de oficina se conserva únicamente como fixture técnico reutilizable.

Priorizar latencia de entrada a acción, entrada a imagen y entrada a sonido; estabilidad del movimiento; coste del peor cuadro y rapidez de reintento. Medir por separado esas rutas: leer teclado a 50 Hz no demuestra respuesta visible a 50 Hz. Registrar también buffers del emulador y dispositivo de entrada al evaluar sensación de control.

50 Hz de presentación es un objetivo de exploración para la acción rápida, **no una prestación garantizada**. Un resultado a 25 Hz no se aprueba automáticamente porque permita más decorado: se debe juzgar su respuesta y legibilidad jugando. Ajustar coste visual, algoritmo y alcance antes de aceptar una pérdida perceptible del control. El resultado final debe reunir juego y presentación, no dar por terminada una mitad.

## Uso de referencias CPC

La investigación de juegos se centra en qué decisiones se toman y cómo responde el juego: movimiento, riesgo, ritmo, enemigos, sonidos, aprendizaje y reintento. Distinguir versión CPC de otras conversiones y documentar si se jugó, se observó o sólo se leyó una fuente. Ninguna lista de «mejores juegos» reemplaza esa comparación ni obliga a copiar una fórmula.

Las [referencias del diseño actual](GAME_REFERENCES.md) registran las instrucciones y el testimonio consultados, con sus límites.
