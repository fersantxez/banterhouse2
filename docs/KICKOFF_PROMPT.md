# Encargo inicial

El texto siguiente recoge el encargo de investigación. Las instrucciones posteriores están en [Dirección creativa](CREATIVE_DIRECTION.md).

Vamos a iniciar Banterhouse 2 como proyecto independiente. Trabaja directamente en esta carpeta.

> Nota de archivo. Algunas propuestas de este documento se descartaron o siguen pendientes. Consulta el [estado actual](STATUS.md).

Quiero una investigación técnica profunda y práctica de cómo extraer el máximo del Amstrad CPC 6128 clásico de 128 KiB para hacer una secuela de Banterhouse mucho más vistosa. Podemos aceptar una complejidad considerable, ensamblador Z80, herramientas poco didácticas y herramientas comerciales o cerradas si aportan ventajas reales. No des por hecho que CPCTelera es la limitación ni que otra biblioteca será automáticamente más rápida.

Lee README.md, AGENTS.md y docs/INITIAL_RESEARCH.md como contexto e hipótesis inicial, no como decisiones cerradas. Puedes consultar ../banterhouse en modo de solo lectura, especialmente su código actual de render, lógica y gráficos, y el laboratorio Expanded de bancos, FDC y recursos. Distingue lo que funciona en la campaña publicada de lo que sólo está demostrado en el laboratorio. No modifiques el proyecto original.

La plataforma obligatoria es un CPC 6128 original, sin Plus, aceleradores ni ampliaciones obligatorias. Separa claramente cualquier alternativa para Plus o hardware ampliado. Considera disco y varios discos/caras si conviene; no impongas compatibilidad con cinta o CPC 464 a costa del objetivo.

Investiga con fuentes primarias actuales, documentación de hardware y código de proyectos cuando esté disponible:
- Motores, bibliotecas, compiladores, ensambladores y entornos de producción: CPCTelera especializada, SDCC y Z80 propio, RASM, z88dk/cpcrslib, 8BP, TRSE, Phactory y otras alternativas relevantes. Diferencia editor, compilador, librería y motor. Verifica mantenimiento, disponibilidad, plataformas, licencias declaradas e integración; no confundas un juego espectacular con un motor reutilizable.
- Técnicas gráficas: sprites compilados y enmascarados, versiones desplazadas, tiles, restauración parcial, pantalla única frente a doble búfer, scroll por hardware, split de HUD, rasters, overscan, modos mixtos, oclusión y animación. Explica sus costes de RAM, CPU, contenido y compatibilidad CRTC.
- Arquitectura completa de 128 KiB: bancos físicos, mapa de direcciones, código residente, pila, ISR, audio y datos; acceso de vídeo a RAM principal; gestores de recursos y overlays si compensan. Todos los presupuestos deben sumar y distinguir memoria física de ventanas mapeadas.
- Disco y compresión: loaders existentes frente al FDC del laboratorio, geometría compatible, colocación de recursos, carga entre zonas frente a streaming, ZX0/LZSA y otras opciones, convivencia con audio y tiempos de carga reales.
- Sonido AY, Arkos y alternativas; coste de reproductores y efectos; cadencias independientes de música, simulación y render.
- Flujo de producción en nuestro Mac: pixel art, animación, mapas, generación de código, empaquetado por bancos, build reproducible, depuración, profiling y validación en emuladores y hardware.
- Casos de juegos y demos que expriman el CPC clásico: identifica qué está documentado por sus autores, qué código es accesible y qué efectos son trasladables a un juego interactivo. No atribuyas técnicas concretas sin evidencia.

Relaciona todo con Banterhouse: compara habitaciones de cómic muy elaboradas y personajes expresivos frente a scroll continuo u otras direcciones visuales. No fijes aún el diseño creativo. Explica qué mejora visible conseguiríamos con cada inversión y cuál sería su coste.

Entregables en este repositorio:
1. Investigación técnica en español con enlaces, fecha de consulta y separación clara entre hechos verificados, inferencias y experimentos pendientes.
2. Matriz de alternativas y recomendación argumentada, incluyendo la opción de conservar partes de CPCTelera.
3. Dos o tres arquitecturas candidatas con mapas de memoria y presupuestos temporales realistas; no prometas 50 fps sin medir.
4. Plan de un prototipo comparativo: misma escena, personajes, música y carga para comparar renderer genérico, híbrido y especializado; criterios de aceptación sobre peor cuadro, RAM, pila, artefactos visuales, cargas y CRTCs.
5. Próximos pasos priorizados para iniciar Banterhouse 2.

Avanza autónomamente en la investigación y en comprobaciones técnicas acotadas que ayuden a resolver dudas. Si haces micropruebas, guárdalas aquí con instrucciones reproducibles y reporta lo realmente ejecutado. No migres toda la campaña ni construyas el juego completo durante esta primera tarea. No compres herramientas, publiques contenido ni contactes con terceros. Si una medición requiere un CPC físico o software no disponible, déjala identificada sin inventar resultados. El objetivo es una decisión técnica sólida y verificable sobre cómo aprovechar al máximo el CPC, no una lista genérica de herramientas.


## Aclaración posterior del usuario · 10 de octubre de 2026

La dinámica de Banterhouse 2 se puede y se debe rediseñar desde cero. Se conservan personajes y se incorporan nuevos; no debe ser una nueva versión del primer juego. Se busca máxima diversión, rapidez y respuesta al control junto con un despliegue técnico, gráfico y artístico importante. El usuario cita Chuckie Egg como referencia de placer al moverse, saltar, recoger y recibir respuesta sonora. No implica clonarlo ni fijar ya un género. Esta aclaración prevalece sobre preferencias previas por continuar habitaciones o reglas. Véase `docs/CREATIVE_DIRECTION.md`.
