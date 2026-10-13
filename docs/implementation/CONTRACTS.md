# Contratos iniciales de implementación

Estos son los requisitos de implementación. Los valores iniciales se pueden ajustar después de probarlos, registrando el motivo. Mantener los parámetros en un único `src/core/tuning.h` y exportar sus valores al manifiesto del build. Un cambio de contrato actualiza sus casos de prueba y la decisión correspondiente.

## C1 Separación de módulos

La simulación en `src/core/` no incluye CPCTelera, reloj, AY, VRAM ni FDC. Se compila como el mismo C para host y Z80. Usar `stdint.h`, tamaños explícitos, arrays acotados y ninguna asignación dinámica, recursión o coma flotante durante gameplay.

Interfaces propuestas para el juego, que habrá que implementar:

```c
void sim_reset(GameState *s, const LevelData *level, const Checkpoint *cp);
void sim_tick(GameState *s, InputFrame input, GameEvents *events);
void render_present(const GameState *s, const GameEvents *events);
void audio_submit(const GameEvents *events);
LoadStatus package_load(uint16_t package_id);
```

`LevelData` contiene datos calientes residentes en RAM fija; no es un puntero a un banco que se oculta. Eventos: lista fija de 16 entradas, IDs estables, sin punteros; el caso de máximo tráfico debe demostrar capacidad. Un overflow incrementa contador y falla la prueba de estrés, nunca corrompe memoria. Los efectos de juego se aplican en simulación y no dependen de que se reproduzca un sonido.

Los formatos guardados y el hash de estado serializan campos uno por uno en little endian. Nunca volcar una `struct`: SDCC y el compilador host pueden diferir en padding, enum y tamaño de `int`. Fixtures y replays incluyen versión, hash del nivel y hash de parámetros. La primera implementación no necesita aleatoriedad; si se añade, estado y semilla explícitos forman parte del replay.

Contador lógico de simulación `uint32_t`; expiraciones con comparación modular documentada para intervalos menores de medio rango. Leer/escribir un contador compartido con ISR requiere sección atómica. Mantener funciones de serialización y comparación temporal comunes a host y Z80.

## C2 Imagen y geometría

Pantalla lógica 160×200, HUD `y=0..15`, zona jugable `y=16..191`, franja decorativa `y=192..199`. El estudio gráfico dibuja suelo a 184; es una coordenada del fixture, no el borde obligatorio de todos los niveles. PNG ampliado no aporta coordenadas nuevas.

Sprite canónico de Pitu: caja visual de 16×32; posición `(x,y)` es su esquina superior izquierda. Primera caja de cuerpo: `[x+3,x+13) × [y+4,y+32)`, pies en `y+32`. Las cajas son semiabiertas: bordes que sólo se tocan no son penetración. Suelo/plataforma se resuelven por cruce del plano de pies, incluso cuando hay igualdad al aterrizar. Colisión independiente de recortes, pelo o animación.

Sello mirando a la derecha: `[x+13,x+21) × [y+12,y+26)`; izquierda: `[x-5,x+3) × [y+12,y+26)`. Son propuestas visibles en debug, no píxeles de la pose. Papel inicial: 4×6, hitbox igual a su rectángulo. Boca de máquina: rectángulo propio en el nivel, no toda la carcasa. Los adornos y la moto no son colisiones.

El JSON de nivel separa `solids`, `one_way_platforms`, `spawn`, `exit`, `machines`, `enemy_spawns`, `panels` y `visual_id`. ID estable por objeto; coordenadas enteras lógicas; no colisiones inferidas de colores. El exportador valida rangos, límites de tablas y referencias, pero no afirma que el nivel sea resoluble sólo por pasar el esquema.

La geometría de los cuatro estudios es provisional. En M0 se reubican plataformas según el salto realmente ejecutado. Antes de aprobar un nivel hay que completar una ruta en el binario y conservar su replay.

## C3 Tiempo y entrada

Paso fijo nominal de 50 Hz. La configuración de vídeo determina el periodo real y se registra. `sim_tick` no recibe tiempo de pared ni duración del último render. Una presentación a 25 Hz muestra uno de cada dos estados; nunca divide velocidades, gravedad o temporizadores.

`InputFrame`: `held`, `pressed`, `released`, bits `LEFT`, `RIGHT`, `JUMP`, `DOWN`, `ACTION`, `PAUSE`, `RESTART`. `pressed = held & ~previous`; `released = previous & ~held`. Al consumir un tick, consumir también sus flancos: un retraso del renderer no puede repetir una pulsación.

Izquierda y derecha simultáneas dan velocidad objetivo cero y conservan orientación. Salto y abajo simultáneos priorizan salto. Pausa y reinicio son teclas separadas; reinicio requiere confirmación local mediante soltar y volver a pulsar, sin lectura de disco. Joystick: arriba salta, abajo baja y fuego devuelve. La redefinición de teclado llega en T26.

Una dirección horizontal única cambia la orientación del sello en ese mismo tick, aunque la velocidad tarde en invertirse. Si movimiento y acción llegan juntos, aplicar primero la nueva orientación. Un gesto ya activo sigue la orientación actual; no congelar una pose a costa de la respuesta del control.

El reloj, captura de entrada y audio tienen un único propietario por recurso. El acceso PPI/AY se serializa para que la ISR de audio no interrumpa a mitad una selección de teclado o registro. T04 documenta el mecanismo exacto y su coste. No poner FDC, renderer o cambios de banco en la ISR.

Reloj inicial: contador de ticks producido por el servicio de interrupciones, calibrado contra VSYNC; no asumir fase inicial ni número correcto de ticks sólo por dividir un contador. El scheduler consume ticks pendientes, captura cada muestra una vez y registra retrasos. Si hay más de dos pendientes, registrar overrun y entrar en diagnóstico recuperable en el build de prueba; no ocultarlo descartando ticks ni mantener un bucle de recuperación infinito. El comportamiento release se decide en T20 con cero overruns como objetivo de aceptación.

Las lecturas multibyte del reloj y cambios banco/sombra son atómicos. Las secciones críticas conservan el estado previo de interrupciones; no terminar siempre con `EI`. Esperar VSYNC sólo organiza presentación: no prueba por sí solo ausencia de tearing.

## C4 Movimiento inicial

Posiciones y velocidades: enteros de 16 bits con signo y **7 bits fraccionarios**, 128 unidades por píxel. Rango representable de posición: −256 a menos de +256 píxeles, suficiente para esta arena. Antes de cualquier suma que pueda salir de rango usar intermedio de 32 bits y resolver límite/despawn; no permitir overflow con signo. Las conversiones negativas a píxel tienen función explícita de redondeo hacia abajo, comprobada en host/Z80, sin depender de desplazamiento de enteros negativos.

| Constante inicial | Unidades internas | Significado aproximado |
|---|---:|---|
| Velocidad horizontal | 166 | 1,297 px/tick |
| Aceleración/freno | 83 | Alcanzar velocidad en dos ticks |
| Impulso de salto | −410 | −3,203 px/tick |
| Gravedad | 23 | +0,180 px/tick² |
| Caída máxima | 384 | 3 px/tick |
| Corte al soltar salto | −192 | Limitar ascenso a −1,5 px/tick |
| Coyote | 3 ticks | Tolerancia tras abandonar borde |
| Buffer de salto | 4 ticks | Pulsación anterior al aterrizaje |
| Papel hostil / devuelto | 115 / 205 | 0,898 / 1,602 px/tick |

Cada tick: leer intención; resolver salto o descenso; ajustar velocidad horizontal hacia objetivo; limitar ascenso si se soltó salto; integrar X y resolver sólidos; integrar Y usando la velocidad actual y resolver sólidos/plataformas; aplicar gravedad para el próximo tick si sigue en aire. Aterrizar pone `vy=0`. Saltar consume buffer y coyote una sola vez. Mantener salto no salta de nuevo al aterrizar.

Los contadores se expresan por fechas de expiración: una concesión en tick `t` de `N` ticks está activa en `t..t+N-1`. Actualizar expiraciones antes de aceptar nuevas acciones evita restar un tick inmediatamente. Las pruebas incluyen extremos `N-1` y `N`. Contadores largos y comparación de expiraciones deben soportar wrap, comprobado con tick cercano al máximo.

Plataforma atravesable: colisiona sólo bajando si los pies anteriores estaban encima o en su plano y los nuevos lo cruzan con solape horizontal. Atravesarla subiendo no pega a Pitu. Bajar ignora **sólo el ID actual** hasta que los pies y el cuerpo hayan pasado su cara inferior; limpiar el ID al quedar libre. Un timeout de seguridad de 30 ticks detecta una geometría imposible y falla el fixture, no desactiva todas las plataformas. No usar la altura teórica de salto como prueba de alcance real.

## C5 Máquinas y proyectiles

Pools iniciales fijos: 3 máquinas, 4 papeles y 3 plazas de enemigo; M2 activa sólo un enemigo. No llenar plazas para cumplir una cifra visual. Máquina: `IDLE → WARNING → FIRE → IDLE`, o `OFF`. Parámetros iniciales de M1: espera 50 ticks y aviso 15. El aviso completo precede al disparo.

Al empezar aviso, reservar una plaza libre de papel. Si no la hay, permanecer en espera; no borrar un papel visible. Una máquina apagada devuelve su reserva. `FIRE` activa el papel reservado y lo mueve desde el tick siguiente; no depende de que se haya dibujado ya el aviso. Las direcciones y bocas salen del nivel, no se orientan automáticamente hacia Pitu.

Papel: `FREE`, `RESERVED`, `HOSTILE`, `RETURNED`; dirección cardinal; flag de rebote consumido; máscara de enemigos ya puntuados en esa devolución. Expulsarlo al cruzar el borde jugable o chocar con sólido. Un enemigo golpeado no lo consume; una boca activa golpeada lo consume y apaga su máquina. Una carcasa apagada no bloquea papel salvo que el nivel tenga sólido explícito.

Sello: pulsación nueva, activo en ticks `t..t+5`; recuperación `t+6..t+13`; siguiente gesto posible desde `t+14`. Un `pressed` durante recuperación se ignora, no se acumula. Puede devolver varios papeles que entren durante su ventana; una pulsación no crea varias ventanas. El movimiento continúa durante todas esas fases.

Al devolver, poner `RETURNED` en el punto de contacto y dirección horizontal de Pitu. Consumir el desplazamiento restante de ese tick; empezará a viajar devuelto en el siguiente. Feedback visual/sonoro se solicita en el tick del contacto. El gesto al aire emite su sonido suave al comenzar, sustituible por el de acierto con mayor prioridad.

## C6 Colisiones simultáneas y puntuación

Usar barrido de segmentos contra rectángulos expandidos por el tamaño del papel. Para Pitu/enemigos en movimiento usar desplazamiento relativo anterior→actual; un cruce entre dos posiciones no puede desaparecer por dibujar a 25 Hz. Como base clara, comparar tiempos de contacto racionales con productos de 32 bits; optimizar después de perfilar. Prohibido comparar sólo la posición final.

Resolver contactos por menor tiempo de impacto. Empates de un mismo papel: sello válido antes que cuerpo; boca antes que panel; panel antes que enemigo; sólido al final de empate. Tras pasar por un enemigo, continuar el tramo restante con ID ya visitado; máximo de contactos acotado por el número de objetos. Los papeles se procesan por ID estable. Pruebas específicas fijan empates; no debe depender del orden de dibujo.

Orden global de un tick:

1. Entrada, estados de pausa y acción; movimiento y apoyos de Pitu.
2. Actualizar enemigos y máquinas; los papeles nuevos no se desplazan aún.
3. Resolver trayectorias de papeles y devoluciones; registrar candidatos de daño.
4. Aplicar máquinas apagadas y puntuación. Si se apagó la última, abrir salida, retirar hostiles/reservas y suspender daño de ese tick y siguientes.
5. Si quedan máquinas, aplicar como máximo un daño a Pitu entre papel y contacto de enemigo. Contacto de enemigo también usa barrido relativo.
6. Resolver salida, muerte y eventos audiovisuales; publicar estado para render.

Esta prioridad de finalización es una decisión provisional explícita: **la última máquina apagada en el mismo tick que un golpe permite terminar la arena**. Una devolución válida protege contra ese papel, no contra otro peligro salvo invulnerabilidad o finalización.

Historia: 2 impactos disponibles; tras el primero, 50 ticks de invulnerabilidad desde ese tick, sin retroceso ni ocultación completa de Pitu. Tras el segundo: estado `DEAD`, congelar amenazas; soltar acción y pulsar de nuevo permite `RETRY`. El checkpoint conserva puntuación de entrada y estado de inicio, no los puntos ganados durante el intento fallido. Reiniciar limpia pools, reservas, eventos, timers y regiones sucias; no accede al disco.

Puntos base: 500 por máquina y 100 por enemigo. Una devolución comienza con multiplicador 1. Al acertar un objetivo nuevo, sumar base × multiplicador y luego incrementar hasta 5; un rebote válido incrementa antes del próximo objetivo. Cada plaza de enemigo puntúa como máximo tres veces por intento, aunque reaparezca; después sigue pudiéndose apartar. Marcar objetivos ya visitados para impedir que un mismo papel puntúe dos veces por el mismo enemigo.

El bonus temporal se implementa en T26, no se usa para validar M1. No añadir aumento de presión al agotar bonus sin una prueba específica posterior.

## C7 Paneles y Alberto

Panel fijo `/`: derecha→arriba, arriba→derecha, izquierda→abajo, abajo→izquierda. Panel `\`: derecha→abajo, abajo→derecha, izquierda→arriba, arriba→izquierda. Sólo `RETURNED` rebota. Tras el primer panel, marcar rebote consumido; un segundo panel consume el papel. El panel se reconoce por forma y flecha, sin depender exclusivamente del color.

Alberto, primera IA: permanece en su plataforma; aviso de 12 ticks, carrera de 50, giro/pausa de 12. Escoge dirección al empezar aviso si Pitu está en esa plataforma; si no, patrulla. No recalcular dirección cada frame. En borde sólido se detiene y avisa de giro, no cae sin señal. Al recibir devolución queda fuera 100 ticks; reaparición con aviso de 25 en una entrada segura. Si la entrada solapa a Pitu, posponer; ninguna aparición hace daño instantáneo. Al apagarse todas las máquinas, cancelar reapariciones y daño.

Estos tiempos son tuning inicial. La pose canónica puede ser estática en T15; el aviso debe seguir visible mediante un indicador nativo provisional, hasta disponer de animación propia.

## C8 Renderer y arte

Usar fondo limpio con decoración y estado persistente. Renderer G: restaurar todas las regiones antiguas desde ese fondo, actualizar regiones persistentes y después dibujar todos los actores actuales en orden fijo: enemigos, Pitu, papeles, sello/feedback, HUD. No intercalar restauración de un actor con dibujo de otro: borraría solapes.

Restaurar RAM1 con C0 y dibujar recursos de RAM4/6 con su banco seleccionado. RAM1 y RAM4–7 no comparten visibilidad CPU. Toda rutina que pagina vuelve a configuración/sombra inicial, incluso en error. El fondo modificado por una máquina apagada también se actualiza en RAM1; nunca debe reaparecer el estado viejo al pasar Pitu.

Convención de máscaras heredada: byte de máscara y byte de píxeles por pareja de píxeles; bit preservado=1; negro opaco distinto de transparente. Pose alineada 16×32=512 B; variante desplazada de 9 bytes por línea=576 B. Generar espejos/variantes en build o al cargar, fuera del tick. Contar todas las variantes residentes, no sólo el PNG.

Clipping antes de cualquier escritura; extremos y coordenadas impares siempre cubiertos. No llamar a una primitiva del SDK con un ancho o un destino que viole sus restricciones. Wrapper C/ASM probado con centinelas y registros preservados.

Fuente de píxeles: `assets/source/`, inicialmente importada y congelada desde el original con hashes. Una animación nueva no modifica silenciosamente la pose canónica. Exportador falla ante >16 índices, tinta no clásica, dimensión imposible, frame/máscara incompatibles o presupuesto excedido. Nada de reducir colores automáticamente sin revisión de arte.

## C9 Memoria y recursos

Comenzar con las reservas A de `docs/ARCHITECTURES.md`: RAM0 fijo para núcleo/ISR/audio/estado/pila; RAM1 fondo; RAM2 lógica/trabajo; RAM3 vídeo; RAM4 Pitu; RAM5 tiles; RAM6 reparto/FX; RAM7 mapas/caché. RAM2 mantiene inicialmente 8 KiB de lógica **sin overlay**; su subdivisión futura exige justificación. Cada región de linker tiene nombre y límite generados desde `cfg/memory.json`.

Un mapa de reservas no verifica el binario. T02 debe comprobar secciones reales, BSS, inicializadores, trampolines, código de librería, vectores, stack y temporales de arranque. Código ejecutado al paginar, ISR y pila jamás viven en 4000–7FFF. Arranque AMSDOS termina antes de ocupar sus áreas incompatibles; no volver al firmware después de tomar control sin un contrato nuevo.

Handle paginado: `{bank, offset, length, generation}` con anchuras explícitas, rango validado sin overflow. La generación cambia al invalidar paquete. Guardar un puntero a 4000 para usarlo después de devolver el banco es un error. Lectura entre dos bancos pasa por scratch fijo.

Durante una transición: fuente empaquetada ≤4 KiB y destino de bloque ≤4 KiB, ambos contados, además de stack y decoder. Input incomprensible o fuera de rango se rechaza **antes** de expandir. Validar la gramática del flujo comprimido con límites de lectura/escritura y backreferences o usar decoder con límites; checksum final solo no evita corrupción.

No reservar a la vez los beneficios incompatibles de dos mapas. Doble búfer requiere una decisión y manifest distinto. Margen/pila/guardas nunca se usan para hacer que el enlace «pase».

## C10 Audio

Una cola lógica alimenta un único propietario AY. Orden de prioridad inicial: daño/fin de arena, máquina apagada, devolución, salto, sello vacío, pasos. Un paso nunca tapa una devolución. Prioridad igual: orden estable del evento; no permitir que una fuente inundada retrase un efecto crítico. Sin asignación dinámica ni escritura AY desde la lógica del juego.

M0 usa tonos/SFX originales breves. Música se incorpora con un único player cuya revisión, ABI y opciones estén fijadas; T17 empieza por AKG de Arkos como candidato, sin mantener varios players residentes. Si no cabe o rompe deadlines, detener esa integración con medidas antes de evaluar AKM. Referencias culturales no exigen copiar canciones.

Pausa de juego congela simulación, conserva servicio de control y audio según política documentada. Carga bloqueante silencia/funde audio antes del FDC y reinicia su reloj después; esa pausa no cuenta como jitter de gameplay. El HUD y la música no gobiernan el reloj de la física.

## C11 Paquetes y carga

Contenedor propio versionado; serialización explícita. Cabecera: magic, versión, build-id, volumen, número de entradas, rango del directorio y checksum. Entrada: ID, tipo, codec, dependencia, offset almacenado, longitud almacenada/expandida, banco/rango destino permitido, CRC. T21 fija cada ancho/offset en un documento y crea vectores binarios antes del loader.

Validar sumas de offset+longitud con anchura suficiente; rechazar duplicados, solapes no declarados, destinos residentes protegidos, incompatibilidad de versión/build y dependencias ausentes. Sectores se obtienen del DSK final, con cabeceras y redondeos reales; nunca deducirlos sólo de la suma de payloads.

Máquina de estados: `PLAY → QUIESCE → SAVE_CHECKPOINT → INVALIDATE → CHECK_VOLUME → LOAD → VERIFY → COMPOSE → COMMIT → PLAY`. En error: `RECOVERY`, con fuente, texto y entrada residentes; reintentar o volver a menú mínimo. Una carga parcial invalida el destino. No prometer conservar un paquete viejo que ya se ha sobrescrito.

No volver desde una rutina descargada ni mantener referencias a su código. El primer loader sólo sustituye datos. Reintentos automáticos por operación: máximo 3 intentos totales, cada espera FDC con timeout; después recuperación controlable. El usuario puede reintentar manualmente sin límite. Los códigos ST0/ST1/ST2 y la causa quedan en evidencia técnica, no como jerga en el mensaje de juego.

Errores de volumen se detectan antes de escribir destinos. Para leer la cabecera de volumen usar una ubicación de bootstrap conocida del formato final; verificar magic/build/volumen antes de confiar en la tabla de sectores que contiene. La ubicación, firma y regla de descubrimiento quedan fijadas en T21/T23, no se inventan al cargar.

Sin FDC ni descompresión larga durante `PLAY`, `DEAD` o `RETRY`. Recursos de las cinco arenas normales y de todas las fases de un encuentro permanecen residentes mientras se reintenten. El formato de caras y las cuotas siguen el plan de disco; no hacerlas caber eliminando silenciosamente recursos.
