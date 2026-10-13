# Plan de reparación de la física de Pitu

12 de octubre de 2026. Alcance: corregir la suspensión al abandonar plataformas y consolidar movimiento, colisiones y geometría en las 24 arenas del prototipo de Banterhouse 2. Plataforma objetivo: CPC 6128 clásico de 128 KiB. El estado de cada tarea está en `PHYSICS_STATUS.json`.

La prioridad es entregar primero una corrección pequeña y comprobable del borde. Después se unifican las reglas y se verifica cada arena. La reparación no espera a que se complete el renderer bancado, a una lectura de paleta o a una prueba humana de acordes del teclado.

## Diagnóstico en el código actual

En `src/main.c`, `update_player()` mueve X pero no comprueba si Pitu sigue teniendo apoyo. La integración vertical está dentro de `if (!grounded)`. Al abandonar una plataforma, `grounded` conserva el valor 1, no se aplica gravedad y se renueva además el contador de coyote. Esto explica directamente la suspensión descrita por el usuario.

Reproducción mínima deducida del código: plataforma `[42,70)` a Y=160; Pitu en X=69, Y=128, velocidad horizontal interna 3, vertical 0 y `grounded=1`. Con Derecha pasa a X=70,5. Ya no solapa la plataforma, pero Y sigue en 128 y `grounded` sigue en 1. Sin salto ni descenso, los ticks posteriores tampoco la hacen caer. El caso se dedujo leyendo el código y queda pendiente de convertir en una prueba ejecutable.

Otros problemas que la reparación debe cubrir:

- Las 24 entradas de `campaign` usan los mismos seis `ledges`, aunque hay cuatro fondos. Hay que verificar correspondencia visual por arena, no presuponerla.
- El aterrizaje elige la primera plataforma de la tabla que cruza; el suelo aparece primero. La resolución debe elegir el primer contacto físico, independientemente del orden del array.
- Los pies se convierten a `u8` antes de algunas comparaciones; la lógica debe conservar coordenadas con signo y precisión suficiente.
- Existe un suelo implícito en Y=184. Debe convertirse en geometría explícita para que un futuro hueco no se convierta en suelo invisible.
- El descenso sólo desplaza a Pitu 1,5 píxeles. Falta identificar y excluir exclusivamente la plataforma que está abandonando.
- La física actual usa medios píxeles y una caja de 16 píxeles de ancho. El contrato C4 propone 128 unidades por píxel y C2 una caja corporal más estrecha. La migración se hará por separado del arreglo inicial para identificar qué cambia cada resultado.
- `tools/check_playable_campaign.py` inspecciona texto y coordenadas de máquinas. Su mensaje PASS no demuestra gravedad, saltos, rutas ni una partida completada.

La cabeza atravesando una plataforma requiere distinguir dos casos: pasar por debajo de una plataforma atravesable durante el ascenso es una regla prevista; permanecer encajada al estar de pie es un problema de geometría o presentación. Las superficies tienen diferencias de altura de 24 píxeles y Pitu mide 32; se auditarán los solapes horizontales reales antes de decidir qué recolocar.

## Reglas que debe cumplir el juego

1. La decoración, muebles, máquinas y dibujos del fondo no soportan a Pitu. Sólo la geometría de colisión declarada puede hacerlo.
2. Una plataforma atravesable sostiene por arriba y permite atravesarla subiendo. Un sólido explícito bloquea caras superiores, inferiores y laterales. No convertir todas las plataformas en bloques sólidos.
3. Pitu está apoyada sólo cuando los pies coinciden con una superficie válida y existe solape horizontal positivo de su caja corporal. El mero contacto entre dos extremos no constituye apoyo.
4. Al perder el apoyo se declara en el aire en ese tick. La tolerancia para saltar tras un borde permite saltar; nunca suspende la gravedad.
5. En el aire se integra velocidad vertical y se aplica gravedad hasta la caída máxima. La única detención vertical procede de una colisión resuelta, un estado explícito de pausa/muerte o un límite declarado.
6. Aterrizar coloca exactamente los pies en la superficie y anula velocidad vertical. No hay imanes, correcciones por proximidad ni apoyos deducidos de la animación.
7. Saltar necesita una pulsación nueva o una pulsación almacenada válida. Mantener la tecla no produce saltos automáticos al aterrizar. Salto tiene prioridad sobre Abajo si llegan juntos.
8. Todos los niveles emplean la misma función de física. Los niveles cambian datos, no excepciones de gravedad.
9. El estado de física se calcula con paso fijo nominal de 50 Hz. Dibujar cada uno o dos ticks no modifica sus resultados.

## Orden de ejecución y relación con el plan general

Ejecutar F00 a F08 secuencialmente. Cada ficha exige pruebas y evidencia antes de cerrar. Una prueba fallida requiere conservar el caso, arreglar su causa y repetir las pruebas afectadas; no modificar el esperado para aceptar el fallo.

El plan general tiene una dependencia práctica circular: T04 exige P03, P03 necesita simulación T07 y T07 depende transitivamente de T04. F00 separará las capacidades requeridas de las certificaciones pendientes. T04 y las revisiones humanas conservarán sus resultados reales. El cierre de estas fichas sólo acredita sus criterios, no todas las tareas T ni la campaña futura.

Los comandos nuevos que aparecen a continuación son interfaces propuestas. La ficha indicada debe crearlos antes de invocarlos. `make test`, `make package` y `python3 tools/check_implementation_plan.py` ya existen, pero no sustituyen las nuevas pruebas de física.

## F00 Conservar el candidato y habilitar la reparación

**Entrada:** código y DSK actuales; `STATUS.json`, contratos C1–C4 y pruebas S01–S08.

1. Guardar en `research/runs/<fecha>-F00-<hash>/` hashes del código, recursos, herramientas, BIN y DSK, configuración de Caprice y copia del candidato. Incluir los archivos no versionados; no usar limpieza destructiva del repositorio.
2. Registrar en una decisión las diferencias entre física actual y contratos: precisión, cuerpo, integración, suelo y reloj.
3. Añadir F00–F08 a un seguimiento explícito e integrarlo con el selector/validador del plan. Habilitar esta reparación desde la base de build existente T02. Ninguna ficha exige cerrar P02, T03, T05 o T06 completos.
4. Mantener T04/P02 pendiente para lo que realmente falta. Separar prueba lógica de acordes, prueba del escáner CPC y generación de eventos del sistema operativo. P03 se cierra después de F06.
5. Reservar T07/T08 como receptoras de evidencia compatible; no marcarlas terminadas automáticamente por completar un arreglo parcial.

**Cierre:** candidato recuperable, seguimiento sin ciclo de dependencias y validador documental pasando. Ningún cambio de comportamiento todavía.

## F01 Reproducir el fallo con el código que ejecuta el juego

**Crear:** `src/core/player.*`, `tests/host/test_player.c`, `tests/fixtures/physics/`, `tools/test_physics.py`, target `make test-physics-host`.

1. Extraer la actualización del jugador a una función C compartida por host y SDCC. Pasar estado, entrada y plataformas como argumentos. Sustituir la llamada directa al sonido por un evento que el adaptador actual reproduce una vez.
2. Conservar en esta extracción la precisión Q1, caja actual, parámetros y orden de operaciones. Eliminar la implementación duplicada de `main.c`: el juego debe llamar a la función que prueba el runner.
3. Antes de corregir, comparar trazas de la versión anterior y la extraída en caminar sobre suelo, salto mantenido, salto corto, aterrizaje y descenso. Se permiten sólo diferencias de serialización documentadas, no de estado.
4. Crear el caso mínimo X=69, Y=128 descrito arriba y su equivalente saliendo por la izquierda. La especificación exige perder apoyo y caer; conservar el resultado fallido del código anterior.
5. Guardar por tick: entrada, posición y velocidad internas, caja, `grounded`, apoyo si existe, coyote, buffer y fase de salto. El primer error muestra estado previo, esperado y obtenido.

**Cierre:** mismo código en juego y runner, extracción equivalente y prueba de regresión roja que detecta la suspensión. Esta es la única ficha cuyo cierre exige un fallo esperado documentado; no publicar el binario como reparado.

## F02 Corregir la pérdida de apoyo sin retocar el salto

**Depende de:** F01. **Modificar:** función compartida del jugador, adaptador de `main.c` y fixtures de borde.

1. Añadir una consulta de apoyo geométrico. Validar el apoyo al iniciar el tick y después de mover X; no fiarse del `grounded` del tick anterior.
2. Si desaparece el solape o el soporte deja de existir, limpiar apoyo y `grounded`. No alterar Y para disimularlo. Empezar a integrar caída en ese mismo tick según el orden vigente.
3. Conceder coyote sólo a partir de un apoyo real recién abandonado. No renovarlo en el aire; salto y descenso lo consumen o desactivan según contrato.
4. Hacer que salto gane a descenso simultáneo; una comprobación posterior de soporte no puede volver a pegar a Pitu a la superficie de la que acaba de saltar. El soporte sólo se acepta con velocidad vertical cero y sin una acción de despegue/descenso vigente.
5. Cubrir salida izquierda/derecha con y sin tecla mantenida, frenado tras salir y límite de solape exacto. El primer tick sin soporte debe tener `grounded=0` y aceleración descendente; no exigir todavía un píxel visible en ese primer tick porque la integración usa la velocidad anterior.
6. Compilar y ejecutar el caso en Caprice mediante un pequeño fixture autocontenido que empiece en el borde y aplique una secuencia de entradas. Capturar antes, primer tick sin apoyo y caída. No usar una tecla mantenida por CUA como reloj del experimento.

**Cierre:** pruebas de borde verdes en host y fixture CPC, salto previo sin cambios no previstos y candidato intermedio donde abandonar el borde provoca caída. Conservar este DSK antes de ampliar el motor.

## F03 Declarar las superficies de cada arena

**Depende de:** F02. **Crear:** `assets/levels/arena_01.json` a `arena_24.json`, `tools/build_levels.py`, target `make levels-check` y tablas generadas.

1. Cada arena declara `visual_id`, geometría, spawn y objetos. Puede referenciar una geometría compartida por ID; la reutilización debe ser explícita y validada.
2. Cada superficie lleva ID estable y tipo. Sólidos: rectángulo. Plataformas atravesables: X, ancho, plano superior y espesor físico definido. El espesor no se deduce del dibujo y permite determinar cuándo se ha abandonado completamente al bajar.
3. Convertir el suelo actual en sólido declarado. Declarar límites de arena y qué ocurre al salir por abajo: muerte/reintento en arenas con huecos. Retirar el clamp universal que crea suelo en Y=184.
4. Generar de los mismos datos las tablas de colisión y un overlay de diagnóstico con IDs, caja, pies y apoyo. Nunca leer colores de VRAM para decidir colisiones.
5. Superponer geometría sobre los cuatro fondos y revisar las 24 asociaciones. Recolocar plataformas o corregir el arte de la secuela cuando no coincidan. No modificar las fuentes del primer Banterhouse.
6. Validar IDs duplicados, ancho/alto nulos, rangos, spawns dentro de sólidos, referencias inexistentes y capacidad máxima de tablas. Definir el máximo tras inventariar el nivel más exigente y comprobar RAM real; rechazar exceso en el exportador.
7. Actualizar el validador de campaña para consumir estos datos en lugar de mantener otra tabla de apoyos escrita a mano. Su salida distinguirá validación estática de recorridos ejecutados.

**Cierre:** las 24 arenas seleccionan geometría explícita, cada apoyo visible coincide con ella y los fixtures de datos incorrectos se rechazan. La validación del esquema no se presenta como prueba de accesibilidad.

## F04 Consolidar colisión e integración numérica

**Depende de:** F03. **Crear o completar:** `src/core/state.*`, `collision.*`, `tuning.h` y serialización de estado conforme a C1.

1. Migrar de Q1 a 128 unidades por píxel y caja `[x+3,x+13) × [y+4,y+32)`, por un cambio separado. Centralizar parámetros en `tuning.h`; registrar hash de parámetros en cada replay.
2. Usar `int16_t` para estado e intermedios `int32_t` donde sean necesarios. Comparar cajas en unidades internas; convertir a píxeles sólo para dibujar. Probar redondeo negativo explícito y límites sin overflow.
3. Orden obligatorio: validar apoyo previo; procesar intención y salto/descenso; ajustar velocidad X y corte de salto; integrar X y resolver sólidos; revalidar apoyo tras X; integrar Y y resolver contactos; aplicar gravedad para el tick siguiente si queda en el aire; publicar estado y eventos. Determinar descenso por el desplazamiento vertical usado, no por una velocidad ya incrementada después.
4. Resolver sólidos por ejes con barrido entre posiciones anteriores y nuevas. Elegir el contacto más próximo de ese eje y anular sólo su componente de velocidad. Documentar X antes que Y como convención para esquinas y probarla.
5. En plataformas atravesables aceptar sólo cruce descendente del plano con solape horizontal. Si se cruzan varias alturas en un paso, elegir la primera desde arriba; empates por ID. Reordenar el array no puede cambiar la salida.
6. Guardar `support_id`; `grounded` se deriva de un contacto válido, no es un permiso persistente para saltarse la gravedad. Borrar apoyo en salto, caída, retirada del soporte y cambio de arena.
7. Separar ID ignorado durante descenso del ID de apoyo. Ignorar sólo la plataforma de origen hasta que la parte superior del cuerpo haya rebasado su cara inferior. Otro apoyo sigue colisionando. Si una plataforma inferior impide completar ese despeje y se supera el timeout de C4, fallar el fixture y corregir geometría; no desactivar colisiones globalmente.
8. Probar con resultados calculados independientemente. Por ejemplo, desde reposo sin apoyo con gravedad 23 y orden C4: desplazamientos acumulados tras 1, 2, 3 y 4 ticks = 0, 23, 69 y 138 unidades; velocidades = 23, 46, 69 y 92. Así se verifica caída aun cuando el primer tick no cambie el píxel dibujado.

**Cierre:** S01–S03 y casos de borde pasan; ningún clamp crea apoyos fuera del nivel; contacto estable, orden de tablas irrelevante y acuerdo numérico host/Z80 en fixtures. Revalidar el mapa de memoria del binario.

## F05 Afinar saltos y eliminar encajamientos en todo el recorrido

**Depende de:** F04. **Modificar:** parámetros, geometrías que lo requieran y pruebas S04–S08.

1. Empezar con C4: velocidad X 166, aceleración 83, salto −410, gravedad 23, caída máxima 384, corte −192, coyote 3 ticks y buffer 4. Son valores iniciales, no una promesa de buena sensación.
2. Medir en el código ejecutado altura del ápice, ticks hasta ápice, duración y alcance horizontal de salto corto y largo. Generar trazas y una tabla; no diseñar plataformas usando sólo fórmulas continuas.
3. Ensayar coyote en el último tick permitido y el primero prohibido; buffer justo antes de aterrizar, en su límite y expirado. Aplicar expiraciones C4 sin perder/ganar un tick por el orden de decremento. Consumir cada flanco una vez.
4. Comprobar inversión aérea, frenado en el borde, salto junto a pared, golpe de techo sólido, esquinas y aterrizaje parcial. Evitar enganches laterales en plataformas atravesables.
5. Para cada par de plataformas próximo, buscar posiciones de reposo donde la imagen de Pitu quede atravesada por la superior. Corregir separación vertical, separación horizontal o diseño visual según el caso. Toda corrección obliga a regenerar rutas y revalidar máquinas/spawns.
6. Conservar el sprite canónico. La caja corporal puede ser más estrecha que el pelo, pero no justificar una cabeza enterrada de forma permanente como si fuera una mejora de colisión.
7. Añadir rutas reproducibles de subida y bajada a todos los apoyos alcanzables, y al menos una ruta válida hasta los objetivos de cada arena. Un apoyo intencionadamente inaccesible no se puede usar como spawn u objetivo obligatorio.

**Cierre:** saltos corto/largo distintos, respuesta por flanco, ventanas exactas, recorridos alcanzables y ausencia de encajamientos de reposo. Registrar los parámetros finales y las razones de cada ajuste; diversión y aprobación humana siguen siendo una evaluación separada.

## F06 Integrar reloj y estados del juego

**Depende de:** F05. **Modificar:** bucle de `main.c`, adaptación a reloj/entrada existentes, modos y emisión de eventos.

1. Consumir ticks del reloj con paso fijo; presentar cada uno o dos ticks. El renderer no escribe posiciones, velocidades, apoyo ni temporizadores de simulación.
2. Consumir entradas y flancos una sola vez por tick. Respetar límites de backlog/overrun de C3; no ocultar lentitud descartando ticks ni multiplicar saltos al recuperar retrasos.
3. Pausa congela física. Reanudar no produce un salto atrasado ni una caída acumulada. Reinicio limpia velocidades, apoyo, ID ignorado, buffer, coyote y eventos; validar el spawn mediante geometría.
4. Repetir reinicio en ascenso, ápice, caída, aterrizaje, descenso e impacto. Repetir transición de arena para impedir que sobreviva un ID del nivel anterior.
5. Comprobar que daño y animación no detienen la gravedad en PLAY. Diagnosticar por separado posibles desapariciones del sprite comparando estado, cajas restauradas y VRAM; no deducir posición a partir de una captura negra aislada.
6. Mantener música y SFX integrados con un propietario claro del PPI/AY. Probar teclado durante música y eventos; un menú que muestra ON no acredita salida audible.

**Cierre:** P03/S08 pasan con estados iguales por tick a ambas cadencias de presentación, pausa/reintento correctos, entrada y audio sin regresiones observadas. Medir la cadencia en Caprice a velocidad real; un test acelerado sólo acredita función.

## F07 Ejecutar la regresión automática de las 24 arenas

**Depende de:** F06. **Crear:** `tests/cpc/physics/`, runner de replays, `make test-physics-cpc`, `make test-physics-campaign` y `make test-physics` como agregador.

El runner CPC se introduce inicialmente en F02 para el borde y se amplía aquí. Inyecta `InputFrame` en la misma función de producción. No contiene otra implementación de física. Las pruebas host usan el mismo C; los casos de referencia tienen resultados razonados independientemente para evitar validar el mismo error dos veces.

| Grupo | Casos mínimos | Aserción obligatoria |
|---|---|---|
| Bordes | Cada extremo transitable de cada plataforma; posiciones dentro, justo en límite y fuera; quieta, velocidad máxima y frenado | Primer tick sin apoyo en aire; gravedad activa; caída hasta apoyo real o muerte |
| Ascenso y aterrizaje | Salto desde abajo, caída desde arriba, solape mínimo, borde exacto y cruce de varias alturas | Sólo colisión válida; pies ajustados al primer contacto; sin atravesar suelo |
| Superficies y decoración | Mismo trayecto con fondo diferente y misma geometría; geometría cambiada sin cambiar fondo | Estado depende sólo de colisiones declaradas |
| Sólidos | Pared, techo, esquina, posición negativa y desplazamiento de estrés | Sin penetración final, overflow ni dependencia del orden de tabla |
| Descenso | Dos plataformas, plataforma sobre suelo, liberación de Abajo y Salto+Abajo | Ignora sólo origen; siguiente superficie funciona; salto prioritario |
| Entrada | Izquierda+Derecha, mantener salto, soltar/repetir, coyote y buffer en sus extremos | Orientación y flancos conforme C3/C4; sin salto infinito |
| Ciclo de partida | 100 reintentos por fixture de fase, pausa, daño y cambio de arena | Estado limpio y sin apoyo heredado |
| Determinismo | Replay host/Z80 y dibujo cada uno/dos ticks | Igualdad de todos los campos serializados por tick |
| Recorridos | Subir y bajar de cada apoyo utilizable y alcanzar objetivos en las 24 arenas | Secuencia completada, sin teletransporte durante la ruta |
| Estrés | Entradas pseudoaleatorias con semillas guardadas y límites de pasos | Invariantes geométricas permanentes; primer fallo reducido a replay pequeño |

Los fixtures pueden colocar a Pitu en una plataforma al comenzar para probar un borde aislado. Las rutas de accesibilidad deben comenzar en el spawn y llegar mediante entradas normales: colocarla arriba no prueba que pueda subir.

Implementar un watchdog de flotación: en PLAY sin soporte, sin colisión y sin nueva acción que cambie Y, la trayectoria debe seguir la aceleración contratada. Usar el cálculo discreto y contemplar el ápice; no fallar por dos frames con el mismo píxel entero.

Para obtener evidencia CPC, primero verificar las capacidades reales de Caprice. Usar exportación de memoria/snapshot si está disponible y validada; alternativa: comparación en el propio CPC con estados esperados y panel final estable de caso, tick y valores divergentes. Un CRC final aislado no sustituye comparación por tick. No inventar flags CLI ni reintentar indefinidamente una combinación que la API de teclado no admite.

Lotes acotados si las trazas no caben en RAM: reiniciar fixture, comparar durante ejecución y conservar primer fallo. Registrar hash de fixture, nivel, parámetros, binario y herramientas. Añadir 10.000 ticks por semilla con al menos diez semillas en host y una selección idéntica en CPC; reducir y conservar cualquier fallo antes de corregirlo.

La inyección demuestra la lógica de acordes. No acredita pulsación simultánea a través del teclado físico del Mac. Esa cobertura pendiente se registra aparte y no bloquea ni invalida una corrección de gravedad demostrada en Z80.

**Cierre:** matriz completa con resultado por arena/caso y sin fallos físicos. Si un acceso de campaña está bloqueado por otra mecánica, declararlo explícitamente; no etiquetar un recorrido de laboratorio como partida completa.

## F08 Verificar el candidato y dejarlo jugable en Caprice

**Depende de:** F07.

1. Integrar la nueva regresión host en `make test` y una comprobación de evidencia CPC vigente en el empaquetado. Una evidencia con otro hash de física, nivel o parámetros no cierra el candidato.
2. Ejecutar `make test-physics`, `make test` y `make package`; conservar informes separados de función, visuales y rendimiento. Verificar linker, tamaño, stack y guardas con el nuevo código.
3. Arrancar el DSK de distribución desde reset en CPC 6128 clásico. Verificar identidad del build dentro del juego, no sólo el nombre del fichero.
4. Recorrer menú inicial, opciones, controles, música, inicio, movimiento, salto, pausa y reintento. Capturar un recorrido a velocidad real con música y efectos y comprobar salida de audio; corregir configuración si no suena.
5. Comprobar en el candidato las 24 selecciones de arena con geometría correcta. El selector de diagnóstico y los replays no quedan activados en la versión de juego normal.
6. Reproducir en la versión final el borde que originó el informe y conservar capturas y traza. Verificar que las herramientas de captura no estén mostrando frames incompletos antes de atribuirlo al renderer.
7. Cargar el DSK final en Caprice, iniciar partida normal, liberar todas las entradas inyectadas, enfocar la ventana y dejar Pitu en un lugar seguro listo para teclado. Informar del archivo exacto y controles.

**Cierre:** candidato identificado, pruebas aprobadas y emulador funcionando. Una limitación real de captura/audio/hardware se declara con precisión; no se sustituye por una aprobación inventada. No exigir que el usuario haga las pruebas automáticas.

## Evidencia y criterio de aceptación

### Resultado medido de F05 (12 de octubre de 2026)

Con Q7, gravedad 23 y salto final −450, el `player_step` de producción alcanza 3.567 unidades Q7 (27,87 px) con liberación inmediata y 4.630 unidades (36,17 px) manteniendo el salto; las duraciones medidas hasta volver al apoyo son 34 y 41 ticks simulados. Cada secuencia produjo un único evento de salto. Coyote acepta pulsación tras 0, 1 y 2 ticks desde perder el borde, y la rechaza tras 3; buffer acepta una pulsación que llega un tick antes del contacto y expira antes de una caída larga.

Para evitar el cruce visual al estar de pie, la plataforma inicial se ajustó a X=42, Y=150, ancho 24 frente al suelo Y=184. El barrido del sprite canónico de 16×32 en cada posición entera que conserva solape positivo de la caja corporal no encuentra una plataforma atravesando el sprite en reposo. La simulación de producción encuentra 14 transiciones de salto y rutas desde el suelo a las seis superficies; los objetivos estáticos de las 24 arenas siguen sobre apoyos alcanzables. El fixture Z80 ejecutado en Caprice muestra `FFFF` para 16 comprobaciones (PASS). Esto valida la lógica y geometría del prototipo, no una aprobación humana de la sensación de salto.

Evidencia reproducible: `research/runs/20261012T233000Z-F05-jump-geometry/results.json` y `caprice-f05.png`.

### Resultado observado de F06 (12 de octubre de 2026)

El ejecutable de juego ahora consume el reloj CPC mediante `clock_pop_tick()`, obtiene una muestra `InputFrame` por cada tick y separa `game_tick()` de `game_present()`. No descarta ticks pendientes: los procesa todos y `telemetry` registra los lotes que superan dos. La pantalla de Caprice indicó 50–51 FPS durante la prueba; es el contador del emulador, no una medida de ticks por segundo del código de juego. T04 conserva la medición independiente de 3000 flancos VSYNC.

La rama de pausa vuelve antes de física, máquinas y proyectiles; música/entrada mantienen su servicio. En Caprice el indicador visual cambió a pausa y Pitu conservó posición durante un segundo; reanudar y pulsar R restauró el spawn del suelo. El host también serializa el estado antes/después de una espera pausada y compara la traza de física a cadencias de presentación de uno y dos ticks. El mapa del juego sigue sin solapamiento entre código, datos residentes, pila y páginas de vídeo.

Límite: el log de Caprice no dio error de inicialización AY y el `music_tick` sigue el reloj fijo, pero esta prueba no mide el nivel acústico de salida. La verificación de audio audible permanece en F08.

Cada ejecución escribe `research/runs/<fecha>-Fxx-<hash>/results.json` con caso, arena, pass/fail/blocked, comando y salida, estado esperado/obtenido, primer tick divergente, hashes y rutas de evidencia. Los tests devuelven código no cero ante fallo o capacidad necesaria ausente. Capturas y logs se guardan fuera de las medidas de rendimiento cuando alteren su coste.

La reparación se acepta cuando salir por ambos bordes provoca caída; subir, aterrizar y bajar funcionan; sólo superficies declaradas soportan; no hay penetraciones de sólidos ni encajamientos permanentes de la imagen; todas las arenas pasan sus casos; host y Z80 coinciden; dibujar a distinta cadencia no cambia física; y el DSK final mantiene menú, teclado, música y reintento funcionando en Caprice.

Las nuevas arenas deberán aportar geometría validada y replays antes de incorporarse. Las plataformas móviles previstas para T30 requieren S09 y transporte, salto y retirada de apoyo propios antes de activarlas; no se certifican con las pruebas de plataformas estáticas. Tampoco se afirma compatibilidad de hardware físico por haber pasado Caprice.

## Instrucción para el ejecutor

Leer AGENTS.md, este plan, STATUS.json y C1–C4. Ejecutar F00 y continuar una ficha habilitada cada vez. Arreglar el borde y mostrar caída real en F02 antes de ampliar el sistema. No detener la física por un acorde que CUA no pueda generar. No marcar revisiones humanas como aprobadas. No cambiar el proyecto original. Para cada ficha, guardar prueba, build y resultado; ante error, conservar la reproducción y corregirla. Terminar F08 con el candidato final abierto y listo para jugar, describiendo únicamente lo demostrado.
