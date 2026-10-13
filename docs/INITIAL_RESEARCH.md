# Investigación inicial del CPC 6128

> Nota de archivo. Algunas propuestas de este documento se descartaron o siguen pendientes. Consulta el [estado actual](STATUS.md).

> La idea inicial de conservar las habitaciones y las reglas del primer juego se descartó. La decisión posterior está en [Dirección creativa](CREATIVE_DIRECTION.md).

Investigación y propuesta técnica · 10 de octubre de 2026

Banterhouse 2 puede conseguir una mejora importante de animación, escenarios y presentación en un CPC 6128 clásico de 128 KiB. La opción recomendada es un motor específico, con las partes críticas en Z80, lógica selectiva en C y recursos preparados en el ordenador de desarrollo. RASM, ACE-DL, Arkos Tracker y un compilador de recursos propio formarían el entorno de trabajo. CPCTelera puede seguir usándose para las rutinas que necesitemos.

El objetivo de esta propuesta es el 6128 original, sin expansiones obligatorias. Las cifras de rendimiento futuro son objetivos para un prototipo, no resultados medidos. La revisión del proyecto corresponde al código disponible; las cifras de pruebas anteriores se atribuyen a su documentación y no se han vuelto a medir en esta investigación.

## Qué limita ahora a Banterhouse

CPCTelera ofrece C y ensamblador, control de vídeo, interrupciones y paginación. Su API no impone un techo de 64 KiB ni prohíbe efectos de hardware. Su propia documentación explica que la memoria de vídeo permanece en los 64 KiB principales aunque se cambie el banco visible para la CPU. [Descripción de CPCTelera](https://lronaldo.github.io/cpctelera/), [paginación](https://lronaldo.github.io/cpctelera/files/memutils/cpct_pageMemory-asm.html).

La arquitectura concreta del juego sí condiciona cuánto aprovechamos esas posibilidades:

| Evidencia local | Consecuencia para la secuela |
|---|---|
| `src/game_render.c` guarda el fondo oculto por cada actor en buffers desde `0x8000`; `src/game.c` muestra `0xC000` durante gameplay | Ya existe restauración parcial del fondo. El juego actual no hace doble búfer en ese bucle, aunque documentos históricos describan dos páginas |
| `bh_game_render_frame` recompone escenario, HUD y textos cuando cambia una clave que incluye puntuación, carga, cafés y mensajes | Separar la invalidación del HUD, decorado y objetos permitiría evitar reconstrucciones completas por cambios pequeños |
| `src/graphics.h` define dos frames fuente por personaje principal, de 16 × 32 píxeles, más sus versiones invertidas | Hay un salto visual posible ampliando animaciones y poses, sin aumentar necesariamente la superficie dibujada por frame |
| `src/main.c` ya desactiva el firmware; la configuración ya usa un arranque sin CRT estándar | Eliminar firmware o runtime no sería una optimización nueva por sí sola |
| Código alrededor de `0x4000` y pila desde `0x7FFF` en el build Classic | La ventana habitual de bancos requiere reorganizar el mapa antes de usarla durante el juego |
| `tools/expanded_kernel.s`, `src/storage_fdc_lab.s` y `src/resource_manager.c` contienen trabajo de kernel bajo, disco y gestión de recursos | Existe una base reutilizable, pero hay que integrarla con el gameplay y el audio |

El [estado documentado](https://github.com/fersantxez/banterhouse/blob/main/docs/IMPLEMENTATION_STATUS.md) registra 25,1 Hz en una prueba de galería de 4.350 frames, así como ensayos de bancos y cargas. Es una referencia histórica útil; no demuestra el peor caso de una nueva escena. El laboratorio Expanded está separado de la campaña distribuida. La [arquitectura de disco](https://github.com/fersantxez/banterhouse/blob/main/docs/DISK_RESOURCE_ARCHITECTURE.md) contiene una auditoría histórica que no debe confundirse con el renderer actual.

## Herramientas y alternativas

La valoración de encaje de esta tabla es una recomendación de diseño. No existe aquí un benchmark que ordene las bibliotecas por velocidad.

| Opción | Funciones | Uso posible en Banterhouse 2 |
|---|---|---|
| CPCTelera con motor propio | Rutinas de bajo nivel y entorno ya conocido | Buena transición. Sustituir las funciones críticas cuando una medición lo justifique |
| Z80 propio con RASM | Control del código, bancos, recursos y tiempos | Primera opción para el núcleo gráfico y de sistema; requiere construir el motor |
| C con SDCC y ensamblador propio | Reutilización de lógica y control de las zonas críticas | Mi combinación preferida para producir el juego |
| z88dk y cpcrslib | Otra cadena de compilación y biblioteca CPC de sprites y tiles | Alternativa real, pero cambiar de compilador no acredita una mejora gráfica automática |
| 8 Bits de Poder | Funciones en código máquina para juegos programados en BASIC o C | Productiva y capaz; elegirla si encajan sus convenciones, no como sustitución automáticamente superior |
| TRSE | Entorno integrado y lenguaje de alto nivel para varias máquinas | Interesante para otro flujo de creación; su soporte CPC publicado no demuestra por sí solo una arquitectura 128K adecuada para esta secuela |
| Phactory | Entorno de producción con conversión, compresión y empaquetado por bancos | Muy buena referencia de flujo de trabajo; su publicación de 2014 se anunció sin mantenimiento y para Windows |

Fuentes de las capacidades: [z88dk para CPC](https://github.com/z88dk/z88dk/wiki/Platform---Amstrad-CPC), [8BP de su autor](https://github.com/jjaranda13/8BP), [TRSE](https://lemonspawn.com/turbo-rascal-syntax-error-expected-but-begin/), [Phactory](https://www.norecess464.com/productions/phactory/index.html) y [anuncio de publicación de Phactory](https://norecess464.com/es/index.html).

RASM es un ensamblador, no un motor listo para usar. Resulta atractivo por sus macros, espacios de memoria, bancos, secciones comprimidas, salida EDSK y símbolos de depuración. Dispone de soporte para Mac Intel y ARM. La rapidez con la que ensambla en el Mac no significa que el juego resultante corra más rápido: eso depende de las instrucciones y algoritmos que generemos. [RASM](https://github.com/EdouardBERGE/rasm).

La integración C/ASM exige una decisión explícita: los objetos de SDCC/SDAS y RASM no se deben tratar como intercambiables. Para empezar conservaría SDCC/SDAS al enlazar C y usaría RASM en prototipos o módulos binarios con direcciones y ABI definidas. Adoptar un único ensamblador para todo el juego requeriría verificar conversión de fuentes, relocación, símbolos y convención de llamadas.

Las herramientas cerradas o gratuitas sin una distribución abierta completa también pueden ser útiles. [WinAPE](https://www.winape.net/) ofrece depurador y ensamblador integrados en Windows. Para nuestro Mac priorizaría [ACE-DL](https://roudoudou.com/ACE-DL/), que publica versiones macOS y herramientas de depuración, memoria y API web. No he identificado un motor comercial documentado que podamos comprar y que garantice superar a CPCTelera en este juego. Un motor privado de otro equipo requeriría conocer disponibilidad, condiciones y compatibilidad antes de considerarlo una dependencia.

## Límites del 6128 que siguen existiendo

En la configuración estándar, Mode 0 ofrece 160 × 200 y 16 tintas; Mode 1, 320 × 200 y cuatro; Mode 2, 640 × 200 y dos. La paleta física del CPC clásico tiene 27 colores. Podemos cambiar tintas y modos durante el barrido, pero eso no equivale a disponer de 27 colores arbitrarios en cualquier píxel. [Documentación del Gate Array](https://cpctech.cpcwiki.de/docs/garray.html).

El CPC clásico no tiene sprites por hardware. Los personajes necesitan escrituras de CPU sobre la pantalla. Las prestaciones del Plus pertenecen a otro objetivo de hardware; por ejemplo, el propio repositorio de RASM identifica R-GX como motor de Amstrad Plus. [Sprites en CPC y Plus](https://cpctech.cpcwiki.de/docs/sprites.html), [R-GX referenciado por RASM](https://github.com/EdouardBERGE/rasm).

Los 128 KiB tampoco forman un espacio lineal para el Z80. Hay que mapear bancos dentro de sus 64 KiB direccionables. La RAM adicional permite almacenar más animaciones, música y escenas, pero no duplica la velocidad de dibujo. El controlador de vídeo sigue leyendo la RAM principal. [Mapa y configuraciones](https://lronaldo.github.io/cpctelera/files/memutils/cpct_pageMemory-asm.html).

Para un cuadro de unos 20 ms a 50 Hz, el presupuesto nominal a 4 MHz ronda 80.000 T-states. La ejecución efectiva necesita medir los tiempos de CPC, incluidos accesos a memoria, interrupciones y sincronización. No basta con sumar tiempos de un Z80 ideal. Para efectos avanzados y compatibilidad entre CRTCs usaríamos como referencia el [compendio de investigación de Shaker](https://shaker.logonsystem.eu/ACCC1.8-EN.pdf).

## Dirección visual recomendada

Mantendría el juego de habitaciones y la identidad de cómic, con mayor riqueza de dibujo y animación. Es una elección artística y técnica: un fondo muy elaborado puede componerse al entrar en una sala y mantenerse mientras se actualizan pequeñas regiones.

La primera escena de la secuela debería mostrar personajes con siluetas claras, caminar más expresivo, anticipación de acciones, reacción al peligro y gestos propios. Probaría ciclos de seis a ocho poses como objetivo de contenido. No implica dibujar ocho veces más por cuadro: se muestra una pose cada vez; el coste adicional principal está en almacenamiento y preparación.

Añadiría decorados dibujados con tiles combinados con piezas singulares, muebles que oculten parcialmente al personaje, pequeñas animaciones de oficina, retratos para conversaciones y cambios de paleta por zona. Las paletas de personajes y decorados deben diseñarse juntas. El tratamiento del píxel alargado de Mode 0 debe revisarse en una presentación 4:3, no sólo en un PNG de píxeles cuadrados.

Compararía estas dos direcciones antes de decidir una cámara:

| Dirección | Ganancia | Coste principal |
|---|---|---|
| Habitaciones ilustradas con cambios de pantalla y transiciones puntuales | Más detalle, animación y composición de cómic por unidad de CPU | Diseñar transiciones y cargar paquetes al cambiar de zona |
| Escenario con scroll continuo | Sensación de recorrido y movimiento de cámara | Motor de scroll, entrada de tiles, bordes, sprites, HUD y compatibilidad CRTC |

El scroll por hardware puede ahorrar grandes copias, pero no resuelve el dibujo de bordes ni las interacciones con personajes. Si se elige scroll continuo, debe condicionar el diseño del juego desde el prototipo.

## Renderer propuesto

El primer cambio sería separar fondo, objetos persistentes, actores, efectos y HUD, con invalidación independiente. Un cambio de contador no debería forzar a reconstruir la sala.

Para los actores principales ensayaría sprites compilados: el ordenador de desarrollo genera instrucciones Z80 adaptadas a cada imagen. Las zonas transparentes se saltan, las opacas se escriben directamente y sólo los bordes que lo necesitan usan máscara. Esta técnica intercambia tamaño de código por trabajo evitado en ejecución. El resultado concreto depende de la silueta y del resto del renderer. [Explicación y técnicas de sprites](https://cpctech.cpcwiki.de/docs/sprites.html), [ejemplos ejecutables con fuente](https://cpctech.cpcwiki.de/source.html).

Mantendría un dibujador genérico compacto para objetos pequeños o poco frecuentes. También prepararía versiones invertidas y desplazadas cuando compensen: en Mode 0 dos píxeles comparten un byte, así que mover un píxel requiere resolver esa alineación. Cada variante aumenta el consumo de memoria; hay que presupuestar el conjunto de poses, direcciones y desplazamientos.

Compararía restauración de regiones sobre una pantalla con dos páginas de vídeo y seguimiento de regiones por página. Doble búfer permite presentar un cuadro completo, pero exige mantener ambas páginas coherentes; no debería convertirse en copiar 16 KiB enteros cada cuadro. El método actual de guardar el fondo sigue siendo un candidato válido si gana la comparación visual y temporal.

Rasters moderados y una banda de texto en Mode 1 serían experimentos posteriores. EGX, overscan amplio y cambios de CRTC muy agresivos los reservaría inicialmente para títulos o secuencias controladas. El presupuesto de CPU y las variantes de CRTC pueden hacer que una técnica espectacular en una demo no resulte conveniente durante una persecución interactiva.

## Memoria y carga de contenido

Este mapa es una hipótesis de doble búfer para el prototipo. Los tamaños son reservas propuestas y deben validarse con el binario real:

| Memoria física | Tamaño | Uso propuesto |
|---|---:|---|
| RAM0, `0x0000–0x3FFF` | 16 KiB | Núcleo, vectores, ISR, pila, estado imprescindible y audio accesible durante paginación |
| RAM1, `0x4000–0x7FFF` en configuración normal | 16 KiB | Trabajo temporal y datos que pueden quedar ocultos al paginar |
| RAM2, `0x8000–0xBFFF` | 16 KiB | Página de vídeo A |
| RAM3, `0xC000–0xFFFF` | 16 KiB | Página de vídeo B |
| RAM4 | 16 KiB | Animaciones principales o código gráfico especializado |
| RAM5 | 16 KiB | Recursos de habitación y colisiones |
| RAM6 | 16 KiB | Animaciones secundarias y contenido de zona |
| RAM7 | 16 KiB | Entrada de disco, datos comprimidos o caché |

RAM4–RAM7 se mapearían de una en una en la ventana de `0x4000`. La RAM1 física sigue existiendo cuando queda oculta. Los roles de los bancos pueden cambiar por escena, y cada paquete debe declarar sus dependencias y tamaños.

El núcleo de 16 KiB es el riesgo de esta distribución. Si no cabe con un margen razonable, probaría una pantalla en `0xC000` y más código residente en RAM2. La decisión debe salir de una escena completa. No cargaríamos toda la IA, el audio y el motor en un presupuesto imaginario sólo para conservar doble búfer.

La rutina de interrupción, su pila y los datos que use deben seguir accesibles al cambiar de banco. Los punteros a recursos paginados necesitan banco, desplazamiento y una política de validez; el gestor de generaciones que ya existe es una base. Los overlays de código vendrían después de estabilizar los recursos de datos.

Haría una edición principal en disco, con cargas entre zonas, ascensores o secuencias. Reutilizaría el trabajo FDC y `BHRES.BIN`, incorporando el nuevo contenido. Carga directa no significa carga simultánea gratuita: el servicio del FDC, la música y las interrupciones tienen que compartir tiempos estrictos. El primer objetivo sería una transición fiable; conservar música durante ella exigiría una prueba específica.

La geometría inicial sería compatible con disco estándar de 40 pistas y nueve sectores de 512 bytes por cara. Son 180 KiB brutos; en DATA con 2 KiB de directorio quedan 178 KiB asignables antes de cabeceras y redondeos de archivos. Varias caras o discos permiten ampliar contenido, no la memoria residente. Evitaría hacer obligatorio un formato de 80 pistas o una ampliación M4. La base de disco y las pruebas existentes están descritas en la [arquitectura local](https://github.com/fersantxez/banterhouse/blob/main/docs/DISK_RESOURCE_ARCHITECTURE.md).

Compararía [ZX0](https://github.com/einar-saukas/ZX0) y [LZSA](https://github.com/emmanuel-marty/lzsa) con nuestros recursos: tamaño comprimido, descompresor, RAM temporal y tiempo hasta mostrar la sala. LZSA ofrece descompresores Z80 y está orientado a descompresión rápida en micros de ocho bits. No elegiría por porcentajes publicados sobre archivos de otras máquinas. Descomprimiríamos contenido al cargar una zona; los frames activos deberían estar listos para dibujar.

## Audio y ritmo del juego

[Arkos Tracker 3](https://www.julien-nevo.com/arkostracker/index.php/players-overview/) ofrece AKG como equilibrio para juegos y AKM para ahorrar memoria. AKY reduce coste de reproducción a cambio de canciones mayores; el autor orienta AKY/FAP especialmente a demos. Probaría AKG primero y mediría AKM o AKY sólo si el presupuesto lo pide, incluyendo los efectos de sonido.

Música, lectura de controles, simulación y dibujo necesitan cadencias explícitas. La canción no debería cambiar de tempo por una escena más costosa. Propondría servicio musical a 50 Hz y movimiento/render a 50 Hz si la escena cabe, o un modo coherente de 25 Hz si la complejidad visual lo justifica. Las interrupciones adicionales del CPC no equivalen a cuadros completos disponibles para dibujar.

## Flujo de producción

El Mac debería hacer todo el trabajo que pueda resolverse de antemano: empaquetar píxeles, obtener máscaras, generar variantes, deduplicar tiles, compilar animaciones, calcular colisiones, comprimir y colocar recursos por bancos.

Los artistas trabajarían con imágenes y animaciones editables, y las habitaciones con un editor de mapas o los formatos JSON ya usados por Banterhouse. [Martine](https://github.com/jeromelesaux/martine) aporta conversión CPC, tiles, transformaciones y empaquetado diferencial, con versiones para macOS, Linux y Windows. Lo evaluaría como conversor o referencia para los exportadores; no sustituye al runtime.

El compilador de recursos propio produciría binarios, índices, presupuestos de memoria y una previsualización de lo que se verá realmente. El build fallaría si un paquete no cabe, usa colores incompatibles, deja una animación sin frame o solapa memoria reservada. RASM/SDCC generarían el ejecutable, y la misma compilación produciría el DSK y símbolos para depurar.

ACE-DL sería el depurador interactivo principal. Conservaría la automatización existente con Caprice32 y contrastaría el resultado en otro emulador y en CPC físico. Para rasters y scroll, la prueba de distintos CRTCs tendría que llegar antes de producir todas las salas. Una captura correcta en el navegador no demuestra sincronización correcta en hardware.

## Prototipo para decidir la arquitectura

Antes de migrar la campaña, construiría una sala exigente de Banterhouse 2. La carga inicial propuesta es Pitu de 16 × 32 píxeles, tres actores adicionales de tamaño comparable, pequeños efectos, HUD, música y un elemento de decorado animado. Esta carga es un ensayo, no una capacidad ya garantizada.

1. **Medir el punto de partida.** Registrar tiempos por rutina, cuadro peor, cuadros perdidos y coste de cambios de HUD en el Banterhouse actual.
2. **Comparar tres renderers.** Implementación genérica con CPCTelera, híbrida con sprites especializados y núcleo Z80 específico; mismos gráficos, trayectorias y música.
3. **Validar memoria.** Escena completa con bancos, pila medida, guardas y tiempos de interrupción. Comparar pantalla única y doble búfer sin copias completas indiscriminadas.
4. **Cambiar de zona.** Cargar dos salas desde disco, comprobar dependencias, errores, retorno a la anterior y convivencia con audio.
5. **Probar un efecto avanzado.** Un split de HUD o una transición con scroll; medir su coste y comprobar compatibilidad.
6. **Elegir por resultado.** Fijar herramienta, renderer y presupuesto de contenido a partir de las mediciones.

Los criterios iniciales serían 50 cuadros/s con un margen temporal deseado del 20% en la escena normal, o 25 cuadros/s estables si el salto visual lo compensa. Además del promedio, registraríamos el peor cuadro, errores de restauración, parpadeo, consumo por banco, máximo de pila y latencia real de disco. El objetivo de 50 Hz no es una promesa de rendimiento.

## Decisión propuesta

Adoptaría un motor híbrido especializado para un CPC 6128 de disco: Z80 para gráficos, bancos, interrupciones y carga; C para la lógica que resulte suficientemente eficiente; recursos compilados y medidos desde el inicio. Empezaría por habitaciones más ricas y personajes más expresivos, y decidiría el scroll continuo sólo después de ver su coste frente a esa dirección artística.

CPCTelera puede formar parte de esa solución. Lo que debe cambiar es quién define el mapa de memoria, cómo se preparan los gráficos y qué trabajo se permite en cada cuadro. La primera entrega de Banterhouse 2 debería ser esa sala de referencia, con una mejora visual evidente y un presupuesto demostrado.
