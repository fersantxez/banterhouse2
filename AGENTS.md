# Banterhouse 2

## Alcance

- Trabajar en la raíz de este repositorio, proyecto independiente de Banterhouse.
- Consultar `../banterhouse` en modo de sólo lectura; no modificarlo al trabajar en esta secuela.
- Plataforma principal: CPC 6128 clásico de 128 KiB. Distinguir explícitamente capacidades de Plus y expansiones.
- La primera etapa histórica fue investigación y validación técnica; el estado actual está en `docs/STATUS.md`. Leer `docs/KICKOFF_PROMPT.md` y tratar `docs/INITIAL_RESEARCH.md` como hipótesis iniciales.
- No asumir que abandonar CPCTelera mejora el rendimiento. Comparar técnicas con escenas equivalentes y mediciones reproducibles.
- Documentar en español fuentes primarias, supuestos, límites, herramientas utilizadas y resultados realmente medidos.
- No presentar objetivos de FPS, compatibilidad de hardware o mapas de memoria propuestos como resultados verificados.

## Dirección creativa aclarada por el usuario

- Para implementar, leer `docs/IMPLEMENTATION_PLAN.md` y `docs/implementation/STATUS.json`; ejecutar una tarea habilitada cada vez, con sus contratos y pruebas. Los comandos previstos no existen hasta que su tarea los cree. No marcar revisiones humanas o hardware como aprobadas por haber pasado tests host. El plan no autoriza modificar el proyecto original ni convierte los estudios estáticos en juego ya implementado.

- Leer `docs/CREATIVE_DIRECTION.md`: la secuela conserva personajes e incorpora nuevos, pero debe diseñar una jugabilidad nueva desde cero.
- `docs/GAME_DESIGN.md` contiene la propuesta actual «¡Devuelto!» y `docs/GAME_REFERENCES.md` sus fuentes. Probar M0/M1/M2 antes de producir campaña; reglas, física y alcance siguen pendientes de validación jugable.
- Priorizar diversión, respuesta al control, movimiento, feedback audiovisual y reintento ágil junto con ambición técnica y artística.
- Dirección estética del usuario: el sprite canónico de Pitu es la base visual; videojuego de los 80, súper pop. Construir escenarios, reparto y efectos con ese lenguaje, conservando identidad, proporciones y legibilidad.
- No tratar habitaciones, reglas, cámara, HUD ni ritmo del primer Banterhouse como requisitos. La escena heredada es sólo un fixture técnico.
- Explorar microprototipos jugables antes de fijar cámara, renderer y arquitectura. No equiparar FPS con diversión ni dar por validada una sensación de control sin jugar.

- Incorporar referencias a Prince e iconos de los 80, según la petición del usuario. Pitu sigue siendo la base visual; las referencias culturales se integran en el mundo y se documentan en `docs/GAME_REFERENCES.md`.
- Ampliar el reparto desde las referencias individuales de Creatas y Ejecutas, con los sprites de Pitu y Alberto como anclas de estilo. Las propuestas de reparto se conservan en el archivo creativo externo; no son sprites CPC finales ni nuevas fuentes canónicas.

- Tras la revisión del usuario, usar `assets/cpc-studies/README.md` como referencia de fidelidad gráfica. Las maquetas generadas anteriores exageraban el detalle. Toda nueva pantalla presentada como realizable debe respetar rejilla, tintas y tamaños nativos, y declarar qué se ha verificado; un bitmap válido no acredita fluidez ni jugabilidad.
- `docs/STORY_STRUCTURE.md` y `docs/DISK_CONTENT_PLAN.md` desarrollan la campaña y su planificación en disquete. Las cuotas de dos caras y los paquetes residentes son propuestas; no confundir su aritmética con empaquetado, cargas ni memoria real verificados.

## Reparación autónoma y limpieza de pruebas

- Para continuar la reparación y consultar su revalidación, priorizar `docs/implementation/AUTONOMOUS_REPAIR_PLAN.md` y `AUTONOMOUS_STATUS.json`. Los resultados E00–E04 son históricos; la entrega posterior se describe en `docs/DELIVERY_REPORT.md`; cualquier nueva build requiere sus propias pruebas.
- La ejecución continua se prepara en `AUTONOMOUS_EXECUTOR.md`: una tarea habilitada cada vez, continuando sin solicitar intervención humana para pruebas técnicas. La planificación no pone en marcha esa ejecución.
- Cada prueba debe guardar evidencia y cerrar sus procesos, ventanas y visores propios en éxito, error o timeout. Verificar limpieza antes de abrir otra instancia; no terminar procesos ajenos por nombre ni borrar evidencia.
- La primera fase necesita música melódica pop ochentera, bajo y acompañamiento; validar la salida de audio del runtime y la convivencia con SFX, no sólo indicadores ON/OFF.

## Preparación pública

- Empezar por `docs/README.md`; mantener README orientado a jugadores.
- Ejecutar `make public-check` antes de preparar un commit. No añadir archivos ignorados a la fuerza.
- El sitio web está en el repositorio hermano `../banterhouse2-site`; no copiarlo ni convertirlo en un gitlink accidental.
- La limpieza deja la evidencia histórica en `../banterhouse2-archive`. Las nuevas sesiones pueden usar `research/runs/` ignorado; preservar las evidencias necesarias fuera del contenido público.

## Redacción de documentación

- Usar títulos descriptivos: «Compilar el juego», «Pruebas», «Gráficos y música». Evitar eslóganes, metáforas y preguntas retóricas como títulos.
- Escribir en español directo, con archivos, comandos y ejemplos concretos. Quitar frases de relleno y advertencias repetidas.
- Conservar las fechas, resultados, fuentes y límites de las pruebas. Explicar lo pendiente una vez, en el lugar donde afecta al lector.
- No inventar experiencias personales ni testimonios para dar un tono más humano.
