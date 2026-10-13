# Pruebas y evidencia exigida

Esta matriz define pruebas **por implementar y ejecutar**. Ningún caso se considera pasado por estar escrito aquí. Las comprobaciones host ya realizadas pertenecen a `research/` y `assets/cpc-studies/manifest.json`; no sustituyen los casos Z80.

## Ejecución y resultados

Cada runner genera `results.json` con ID, `pass/fail/blocked`, comando, exit code, hashes, entorno, evidencia y motivo. Ausencia de emulador, ROM o captura requerida = `blocked`; salida global no cero. Guardar cada ejecución en `research/runs/<fecha>-<tarea>-<build-id>/`. Build-id por contenido, no sólo SHA Git: el repositorio inicial contiene archivos todavía no versionados.

Host: compilar el mismo C de simulación, con avisos estrictos y sanitizadores de memoria/UB cuando estén disponibles; documentar lo que no soporte el compilador. Exportadores Python usan fixtures válidos/incorrectos. CPC: ejecutar el binario SDCC y recuperar estado/VRAM/guardas con un mecanismo verificado. La emulación rápida sólo sirve a tests funcionales; tiempos, latencia y escucha usan velocidad real sin atajos.

Un test fallido conserva entrada, estado previo, primer tick diferente y resultado esperado/obtenido. No actualizar el esperado a partir del resultado fallido. Para corrección visual, referencia host compone píxeles directamente y no reutiliza el blitter Z80; para física, añadir casos pequeños con resultados calculados por separado, además de comparación host/Z80.

## B Build, arranque y memoria

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| B01 | Invocar versiones de herramientas, compilar un C y un ASM mínimos, localizar empaquetador/emulador; repetir con una ruta inexistente | Informe real; dependencia ausente rechazada, sin fallback silencioso |
| B02 | Diez arranques desde reset CPC 6128 128K y DSK limpio; ejecutar función C→ASM con argumentos/retorno conocidos | Marca de build correcta, stack/registros preservados, sin colgarse |
| B03 | Parsear mapa real y regiones; guardas de stack/BSS; fixture con sección 1 B fuera, solape y bootstrap que pisa datos | Build normal cabe; tres negativos fallan; pila conserva al menos 256 B libres de la reserva de 768 B en el ensayo completo |
| B04 | Dos builds desde directorios vacíos independientes con mismas entradas y toolchain; comparar BIN/DSK/recursos | Bytes iguales; timestamps y orden de archivos normalizados. No usar `git clean` sobre archivos del usuario |

El test B03 se repite cuando cambian código, recursos residentes o linker, no sólo al crear el arranque. Debe incluir ISR sobre un camino profundo. Un número de RAM calculado desde PNGs no satisface este caso.

## A Arte y exportación

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| A01 | Codificar/decodificar todas las parejas de tintas M0 y direcciones de borde; PNG indexado, `.scr` y tiles/mapas | Píxeles idénticos; 16.384 B por página, 16.000 direcciones visibles únicas, ≤16 posiciones de paleta clásica |
| A02 | Inyectar paleta inválida, máscara incoherente, frame truncado, dimensión excesiva y tile/mapa fuera de índice | Exportador falla con archivo/campo/causa, sin arreglos silenciosos |
| A03 | Extraer VRAM y tintas del CPC para las cuatro pantallas y nuevos sprites | Coinciden con recursos esperados; anclajes y colores canónicos preservados; captura visible adjunta |

## P Reloj y entrada

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| P01 | Contar ticks y VSYNC durante 3.000 intervalos nominales, con perfil registrado y audio cuando esté integrado | Relación de servicio estable; jitter y periodo real registrados, ninguna cadencia inferida del reloj host |
| P02 | Mantener, soltar y volver a pulsar cada botón; izquierda+derecha, salto+abajo y diagonales de joystick | Un flanco por transición; prioridad de C3; mantener no genera acciones nuevas |
| P03 | Mismo replay con presentación cada 1 y 2 ticks; pausa y cambio de ritmo de dibujo | Estado de simulación idéntico por tick; pausa no avanza física/bonus; flancos no se duplican |
| P04 | Forzar acumulación de >2 ticks y wrap de contadores/expiraciones | Overrun registrado y recuperación controlada; sin bucle infinito, pérdida silenciosa o acción repetida; wrap correcto |

## K Bancos y punteros

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| K01 | Patrones diferentes RAM1/RAM4/RAM5/RAM6/RAM7 y lectura selectiva | Banco esperado, RAM0/2/3 intactas y vídeo en RAM principal |
| K02 | Selecciones anidadas y salidas por error; 10.000 ciclos con ISR activa | Configuración/sombra e interrupt enable vuelven a sus valores iniciales |
| K03 | Copia entre bancos vía scratch; ID/rango inválido y handle caducado | Copia válida exacta; inválidos rechazados sin escritura; guardas y recursos fijos intactos |

## R Renderer

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| R01 | Dibujar frames a X pares/impares y ocho fases `y & 7`, cruzar fila de carácter, recortar en cuatro bordes | 0 diferencias frente a compositor por píxeles; guardas fuera de VRAM intactas |
| R02 | Pitu y Alberto cruzan, cambian pose/dirección y se separan; tres actores en estrés posterior | Ningún actor borrado por restauración ajena, orden estable |
| R03 | Crear, mover, eliminar y reutilizar slots de papel/efecto; objeto parcialmente visible | Sin restos, lecturas fuera del frame o píxeles transparentes convertidos en negro opaco |
| R04 | Apagar máquina debajo de actor, cambiar HUD y retirar actor; reintentar escena | Fondo persistente correcto; estado viejo no reaparece; reintento restaura estado inicial |
| R05 | Capturar vídeo de recorrido con presentación a velocidad real | Sin tearing/parpadeo observado en la captura; registrar límites de captura y confirmar en hardware después |

Para R01 barrer, entre otros, X = −16, −15, −1, 0, 1, 143, 144, 145, 159, 160 y Y = −32, −1, 0, 7, 8, 15, 16, 167, 168, 191, 199, 200. El compositor puede probar fuera del área jugable para validar clipping; la lógica limita dónde se mueve Pitu. No restringir el test al caso que admite la primitiva genérica.

## S Física y apoyos

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| S01 | Serializar estado en host/Z80; enteros negativos, límites y campos centinela | Mismos bytes explícitos; sin padding o UB |
| S02 | Caja contra paredes, esquina y techo; cruce exacto del suelo | No penetración, igualdad de borde tratada según contrato, velocidad normal anulada |
| S03 | Subir a través de plataforma y bajar sobre ella; movimiento horizontal sin solape | Sólo aterriza al cruzar hacia abajo con solape |
| S04 | Arrancar/frenar/invertir; extremos de arena; 100 ticks de trayectorias conocidas | Velocidad y posiciones discretas esperadas; sin desbordamiento |
| S05 | Pulsar salto y mantener; soltar pronto/tarde; aterrizar manteniendo | Salto corto y largo distintos, sin auto-bunny-hop ni doble salto |
| S06 | Pulsar en ticks límite de coyote y buffer, dentro y justo fuera | Se acepta/rechaza exactamente según ventana; una pulsación se consume una vez |
| S07 | Descender entre dos plataformas, soltar abajo, caer en suelo sólido | Sólo ignora plataforma origen; siguiente apoyo sigue colisionando; timeout anómalo detectado |
| S08 | Replay de recorrido a 50/25 presentaciones, reinicio desde cada estado de salto | Mismos estados por tick; reseteo completo, sin dependencia del render |
| S09 | Plataforma móvil: extremos, reversión, transporte, salto/descenso, techo y lateral, pausa/retry | Sin hundirse, teletransporte o empotramiento; fase y delta deterministas; regla de caso límite documentada |

## U Sonido

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| U01 | Saltos, pasos, marcas y sello al aire a ambas cadencias de presentación | Un evento por acción; efectos reconocibles al escucharlos; servicio de audio estable |
| U02 | Solicitar pasos, salto, devolución y daño simultáneamente | Prioridad de C10; ningún paso oculta éxito/daño; overflow de cola detectado |
| U03 | Leer teclado/joystick mientras suenan efectos; pausa y reintento | Sin interferencia PPI/AY, notas colgadas o repetición de efectos de un intento anterior |
| U04 | Música + SFX durante 12.000 ticks, incluido peor tick musical | 0 ticks omitidos en gameplay y jitter medido; escuchar grabación; carga silenciosa reportada aparte |

## M Máquinas

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| M01 | Contar espera→aviso→disparo desde reset, pausar a mitad | Cadencia exacta, aviso completo; papel se mueve desde tick siguiente a spawn |
| M02 | Llenar cuatro slots; intentar avisar/disparar tres máquinas; liberar uno | Sin quinto papel ni borrado de uno visible; reserva válida antes de aviso |
| M03 | Apagar/reiniciar máquina con slot reservado; apagar todas | Reserva liberada, sin disparo tardío de máquina apagada |

## D Devolución y barridos

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| D01 | Pulsaciones en inicio/fin de ventana y recuperación; acción mantenida | Seis ticks activos y ocho de recuperación iniciales, sin repetir gesto por held |
| D02 | Papel ante sello, detrás, por encima/debajo, con Pitu saltando | Sólo volumen y dirección correctos devuelven; respuesta no inmoviliza |
| D03 | Papel y Pitu cruzan entre ticks; contacto sello/cuerpo empatado | Barrido relativo detecta contacto; sello válido tiene prioridad, sin daño de ese papel |
| D04 | Papel atraviesa boca estrecha, sólido y panel; dos contactos en un paso | Primer contacto y desempates de C6, sin tunneling; sin iteración infinita |
| D05 | Dos papeles ante sello en ventana; devuelto choca después con Pitu | Ambos pueden devolverse; retornados inocuos; resto de movimiento al convertir se consume |

## F Estado de arena y puntos

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| F01 | Dos fuentes dañan mismo tick; golpes dentro/fuera de los 50 ticks de invulnerabilidad | Máximo un impacto/tick; segundo daño válido sólo tras expirar ventana |
| F02 | Morir con acción mantenida; soltar, pulsar y repetir 100 veces | No reinicio accidental; reset completo, guardas intactas, 0 lecturas |
| F03 | Apagar última máquina y recibir golpe mismo tick; entrar a salida cerrada/abierta | Finalización prioritaria; salida sólo permite terminar abierta; hostiles desaparecen |
| F04 | Ganar puntos y morir, cobrar repetidamente mismo objetivo/plaza y reintentar | Restaurar puntos de entrada; máquina paga una vez; enemigo máximo tres por plaza/intentona |
| F05 | Reset desde aviso, recuperación, aire y pantalla con regiones sucias | Sin reservas, eventos o píxeles anteriores; checkpoint aplicado consistentemente |
| F06 | Bonus llega a cero, pausa, retry y salida | No muerte por tiempo; sólo decrece en PLAY; suma una vez; sin farmeo por retry |
| F07 | Morir antes/después de cada checkpoint de fase final y terminar | Retoma fase correcta con recursos residentes y score de entrada de fase; sin duplicación de recompensa |

## E Enemigos

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| E01 | Pitu cambia de lado durante aviso/carrera; Alberto llega al borde | Compromiso temporal, aviso de giro y conducta de C7 |
| E02 | Papel devuelto atraviesa enemigo y luego máquina | Enemigo apartado, papel continúa hasta boca; multiplicador correcto |
| E03 | Reaparición con Pitu encima del spawn; abrir salida durante espera | No daño instantáneo; spawn pospuesto; ninguna reaparición con arena resuelta |
| E04 | Enemigo recorre cuerpo de Pitu entre ticks; dos enemigos coinciden | Barrido detectado, daño máximo uno/tick; ID estable y límite de puntuación |
| E05 | Carro anunciado, cruce de ruta, pausa/retry y pool lleno | Aviso completo, ocupación dentro del presupuesto, sin spawn invisible ni contador heredado |

## N Paneles

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| N01 | Cuatro direcciones entran en cada diagonal | Ocho salidas cardinales según C7, a velocidad devuelta |
| N02 | Hostil toca panel, retornado toca primero y segundo | Hostil no rebota; primer rebote válido; segundo consume sin bucle |
| N03 | Rebote→enemigo→máquina, incluyendo contactos de borde | Dirección, puntos, multiplicador y trayectoria coherentes |
| N04 | Cambiar panel con papel dentro/cerca, aviso, pausa y retry | Se pospone mientras la zona esté ocupada; nueva orientación legible, ruta aún resoluble |

## Q Rendimiento y comparación

Fixture congelado: 250 ticks de calentamiento + 12.000 medidos, tres runs desde reset por variante; la carga nueva más exigente debe sustituir al fixture cuando lo exceda. Guardar `frames.csv` y `summary.json` con mínimo, mediana, p95, p99, máximo, ID del peor cuadro, ticks/presentaciones y deadlines perdidos. Publicar trabajo y espera por separado. No grabar vídeo o volcar cada campo dentro del benchmark si altera su coste: usar una ejecución funcional separada y cuantificar instrumentación.

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| Q01 | G y H con hashes de escena, poses, input, audio y cadencia iguales | Estado/píxeles iguales; cambios de carga invalidan la comparación |
| Q02 | Medir peor cuadro real, ISR y audio incluidos; run con/sin instrumentación | Objetivo: 0 deadlines perdidos y trabajo máximo ≤80% del periodo real; si falla, decisión explícita, no promedio favorable |
| Q03 | Medir mapa, banco más lleno, pico de transición, pila/guardas y scratch | Conjunto simultáneo cabe; 256 B libres dentro de reserva stack de 768 B; ningún byte contado dos veces como libre |
| Q04 | Timestamps input muestreado→estado→render/evento AY, a 50/25 presentaciones | Mediana/p95/máximo y resolución del método; no presentar esto como latencia física de teclado a fotón |

La compatibilidad de CRTC y tearing tiene evidencia propia en R05/Z04. Medir sólo ciclos de una primitiva no cierra Q02. Si no hay instrumentación temporal fiable, el resultado queda `blocked` y el perfil funcional no se transforma en benchmark.

## C Contenedores y compresión

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| C01 | Empaquetar bloques de 0, 1, 4.095, 4.096 y 4.097 B según regla de formato | Cero se rechaza o define explícitamente; >4.096 se divide; expansión exacta |
| C02 | Alterar versión, rangos, sumas que desbordan, IDs duplicados y dependencias | Rechazo previo a escrituras de destino |
| C03 | Desempaquetar con lector host independiente; comparar hashes de recursos | Igualdad byte a byte, incluidos padding declarado y orden |
| C04 | Repetir build y calcular almacenamiento/residencia/pico de cada transición | Binarios iguales, cuotas reales y sumas sin solapes |
| C05 | ZX0/LZSA en builds Z80 separados con mismos bloques y guardas | Bytes exactos; tiempo, código y stack medidos, incluido validador |
| C06 | Truncar cada punto de streams cortos, longitudes/backreferences inválidas, CRC incorrecto/recalculado | Rechazo o error acotado; nunca lectura/escritura fuera de buffers |
| C07 | Raw, incomprimible, repetitivo y destino al final de banco | Selección correcta, nada cruza 16 KiB, fuente no desaparece por paginación |

## O Disco y transiciones

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| O01 | Leer sectores patrón del DSK final y compararlos con parser host | Sectores correctos, CRC igual, tablas basadas en colocación real |
| O02 | Ausente, incorrecto, sector no encontrado o comando que no termina | Timeout y máximo tres intentos totales; pantalla recuperable y entrada activa |
| O03 | 100 cargas alternadas + 10 arranques fríos por configuración | Recursos exactos; guardar distribución de tiempos/reintentos; ningún fallo oculto |
| O04 | Inyectar errores FDC en copias con música suspendida | Estado residente íntegro; ST0/ST1/ST2 reportados si el entorno los proporciona |
| O05 | Fallo tras primer/último bloque y justo antes de COMMIT | No activar media escena; paquete destino inválido; checkpoint conservado |
| O06 | Usar handle antiguo después de reemplazo y saltar viñeta durante carga | Handle rechazado; skip no salta verificación/composición |
| O07 | Volumen/build equivocado, cabecera o tabla corrupta | Rechazo antes de confiar en destinos/sectores; reintento manual viable |
| O08 | Banco ocupado y fuentes/destinos nunca simultáneamente visibles | Staging fijo correcto y pico real dentro de reserva, sin punteros caducados |
| O09 | Diez retries por arena/encuentro y cambio entre arenas normales | Contador de lecturas FDC y llamadas de carga no crece; tiempos de recomposición registrados |
| O10 | A→B, B sola con código, cara errónea y extracción de todos los recursos | Una vuelta en recorrido base; arranque independiente; checksums y capacidad física correctos |

`loads.csv`: recurso/volumen, bytes almacenados/expandidos, origen/destino de seek, estado frío/caliente, lectura, validación, depack, composición, primer frame jugable, total, reintentos y estado. No sumar como mejora una carga acelerada por emulador. Objetivo inicial ≤2 s caliente para paquete de 16 KiB; si no se cumple, registrar distribución y revisar paquete/transición. El cambio humano de cara se mide aparte.

## I Interfaz y continuación

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| I01 | Redefinir teclas, duplicarlas, mezclar con joystick y usar un solo botón | Acciones accesibles, conflictos rechazados y esquema visible |
| I02 | Código válido/incorrecto, capítulo de otra cara, cambio de versión | Sólo validado modifica partida; pide cara correcta; historia no crea score de arcade |
| I03 | Pausar en salto/aviso, continuar, morir y volver al menú mínimo | Estado consistente, sin avance oculto ni acceso a recurso descargado |

## L Niveles y campaña

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| L01 | Reproducir solución desde reset para cada nivel; dos rutas en M2 | Victoria real en binario CPC con inputs guardados, sin manipular estado |
| L02 | Probar órdenes de apagar máquinas y situación de última activa; probar spawns y caída de cada ruta | Siempre existe una devolución/recorrido de solución previsto; no bloqueos irreversibles |
| L03 | Morir/reiniciar en cada estado especial, salida, fase y viñeta | Checkpoint, puntos, reservas y recursos coherentes; sin cargas por retry |
| L04 | Inspeccionar gráficos/tintas y jugar cada nivel con audio | Personajes/papeles legibles; límites de actores y recursos respetados; revisión humana registrada |

## H Revisiones humanas

H0 movimiento; H1 devolución; H2 M2 con arte/audio; H3 muestra con cargas; H4 primer capítulo; H5 campaña completa. Los capítulos 2–4 y el reparto también registran su revisión en la tarea correspondiente.

Formulario mínimo:

```text
Build, fecha, persona que jugó y dispositivo:
Controles usados y recorrido/intentos:
Qué acciones entendió sin explicación adicional:
Dónde esperaba otra respuesta y qué ocurrió:
Peligros/objetivos que no pudo leer:
Momentos de espera o repetición sin decisión:
Respuesta a «¿te apetece repetir?» y por qué:
Cambios solicitados, en prioridad:
Decisión: aprobado / necesita cambios / no evaluado:
```

No inventar personas, duración ni opiniones. Una evaluación negativa es información útil, no un error del runner. La revisión queda pendiente hasta que haya una decisión real. Presentar siempre el artefacto antes de pedir jugarlo.

## Z Candidato final

| ID | Procedimiento | Resultado exigido |
|---|---|---|
| Z01 | Ejecutar suites y todos los replays de nivel en candidato congelado | Sin fallos críticos; pruebas pendientes identificadas, nunca mezcladas con PASS |
| Z02 | Segundo emulador y perfiles CRTC que realmente implemente | Matriz por versión/ROM/CRTC; discrepancias investigadas |
| Z03 | Controlar emulador: arranque frío → menú → todas las fases sin saltos → final → nueva partida; arranque cara B y paquete desde copia limpia | Mismo SHA-256 del DSK entregado; entradas y checkpoints reales, capturas y estado final; controles manuales, pausa, derrota/reintento. Replay sin escrituras de estado. Instrucciones suficientes y archivos presentes |
| Z04 | CPC 6128 físico: arranque, control, scanout, AY, disco frío/caliente y errores | Evidencia real con modelo/CRTC/unidad/medio; sólo certificar lo ensayado |
| Z05 | Revisar contenido de entrega, hashes, procedencias y notas | Etiqueta emulación/hardware fiel al estado de T34; ninguna publicación implícita |

## Qué ejecutar después de cada tipo de cambio

| Cambio | Regresión mínima |
|---|---|
| Física o input | P, S, D03, F y replays afectados |
| Renderer o asset con dimensiones nuevas | A, R, B03, Q02/Q03 si cambia coste |
| IA, panel o geometría | S/D/F relevantes, E/N, L01/L02 y estrés de slots |
| Audio o ISR | P, K02, U, B03, Q02/Q04 |
| Packer/decoder/FDC/bancos | B03, K, C, O según fase disponible |
| Nuevo paquete/capítulo | A, L, O09, Q02/Q03 y ocupación final |
| Sólo documentación | Enlaces, dependencias, IDs y coherencia; no repetir benchmarks |

Las suites largas se ejecutan en sus gates, después de cambios que afecten su riesgo o al candidato. No repetir 100 cargas por una corrección de un rótulo sin cambios de formato/ocupación.
