# Banterhouse 2: investigación técnica del CPC 6128

> **Diseño e investigación históricos.** Este documento conserva propuestas y decisiones de su fecha; no describe por sí solo la build actual. Consulta [Estado](STATUS.md) y [la guía de lectura](README.md).

Consulta y comprobaciones: **10 de octubre de 2026**. Plataforma obligatoria: CPC 6128 clásico, 128 KiB y disquetera original. Primera etapa; no se ha construido ni medido el juego nuevo.

## Conclusión para decidir el siguiente trabajo

La aclaración del usuario cambia el orden de decisión: **primero diseñar y probar un juego nuevo, rápido, muy divertido y con respuesta inmediata; después elegir la arquitectura que lo sostenga con una presentación ambiciosa**. Se conservan personajes y se incorporan nuevos. La dinámica del primer juego no limita la secuela. Ver [dirección creativa](CREATIVE_DIRECTION.md).

El motor híbrido con SDCC/SDAS, Z80 y partes útiles de CPCTelera sigue siendo un candidato de ingeniería. Pantalla única, doble búfer y scroll se evaluarán según las reglas y la cámara elegidas. La recomendación anterior de empezar por habitaciones ilustradas deja de ser la dirección preferida del juego; la escena heredada sirve como fixture técnico.

Los mapas y tiempos del [documento de arquitecturas](ARCHITECTURES.md) son **[P] propuestas**, no decisiones ni mediciones del juego nuevo. El [plan](PROTOTYPE_PLAN.md) incorpora una fase jugable anterior a la comparación de renderers. La [matriz](TOOLCHAIN_MATRIX.md) cubre herramientas e integración. El [registro de comprobaciones](../research/README.md) conserva los resultados host realmente medidos: siguen siendo válidos para esos recursos, pero no fijan los requisitos de la secuela.

## Qué significa cada evidencia

- **[V] Verificado documentalmente o en código:** capacidad descrita por su autor o implementación local inspeccionada. No equivale a funcionar en nuestro CPC físico.
- **[M] Medido aquí:** recuentos, tamaños y comprobaciones ejecutadas en el Mac, con comandos y hashes.
- **[H] Histórico:** resultados que declara la documentación de Banterhouse; no se han repetido.
- **[I] Inferencia:** consecuencia razonada, dependiente de los supuestos indicados.
- **[P] Pendiente/propuesta:** objetivo, reserva o ensayo sin validar.

Todos los enlaces externos se consultaron en la fecha de cabecera. Las fuentes principales son documentación de autores, repositorios oficiales, el compendio experimental de Logon System y la documentación del fabricante del FDC. Las páginas de aficionados sólo se usaron para localizar fuentes, no para atribuir técnicas a juegos.

## Auditoría del Banterhouse actual

Referencia de sólo lectura: `../banterhouse`, HEAD `98ac5607cf1c4591bad0ffbcb74300b55c313e3c`. Había artefactos sin seguimiento antes de trabajar. Los hashes de los archivos realmente leídos están en [host-probe.json](../research/results/host-probe.json). No se ejecutó su Makefile ni se modificó ese proyecto.

| Evidencia local [V] | Consecuencia para Banterhouse 2 [I] |
|---|---|
| `src/game_render.c:27–44`, buffers bajo actores en `0x8000`, `0x8100`, `0x8200`; `draw_entities` restaura proyectil, Alberto y Pitu en orden inverso | Ya existe save-under. Cuatro actores exigirán ordenar y restaurar coherentemente sus solapamientos, no introducir por primera vez el concepto |
| `bh_game_render_frame`, desde línea 324, vuelve a dibujar oficina/jefe, HUD y overlays cuando cambia la clave | Separar invalidación de fondo, HUD y objetos tiene una justificación concreta |
| `BHRenderKey` incluye carga, cafés, puntuación y mensaje | El peor cuadro debe incluir cambios de estos valores; una media caminando oculta el problema |
| `src/game.c:608–628`: esperar VSYNC, audio, lógica, render y seleccionar página C0 | Gameplay muestra `0xC000`; no hay alternancia de dos páginas en ese bucle |
| `src/graphics.h` y cuatro matrices activas en `graphics.c`: 16×32 píxeles, dos poses por personaje y espejos generados en RAM | Más poses y alineaciones tienen coste de almacenamiento; no multiplican por sí mismas el número de actores dibujados |
| `src/main.c:27` desactiva firmware; configuración usa `--no-std-crt0` y `--sdcccall 0` en la cadena local | No vender quitar firmware o pasar de C a ASM como mejoras ya obtenidas |
| `cfg/build_config.mk:59`: código en `0x3D00`; `src/main.c:26` fija pila en `0x7FFF` | La ventana `0x4000–0x7FFF` contiene código/pila: no se puede paginar durante gameplay sin relocalizar |
| `src/audio.c`: API `cpct_akp_*`, un canal para SFX y prioridades; tick llamado desde el bucle | No es ya un reproductor AT3/AKG con servicio autónomo a 50 Hz. Si el cuadro tarda dos VSYNC, el tick no sigue mágicamente a 50 Hz |
| `tools/expanded_kernel.s`: núcleo bajo, pila `0x3FF0`, canarios RAM4–7, CRC, lecturas de pantalla y sala | Es un slice de laboratorio; no prueba lógica, sprites y música concurrentes |
| `storage_fdc_lab.s`: `DI` en preparación/seek/lectura, polling y validación de resultados | Integrarlo como está pausa el servicio por interrupciones; hay que definir explícitamente la política de audio |
| `resource_manager.c`: identificador, banco, tamaño y generación; backend debe conservar destino si falla | Leer directamente sobre el recurso activo y fallar a mitad contradice ese contrato. Hace falta staging o invalidación/recuperación explícita |

[H] `docs/IMPLEMENTATION_STATUS.md` declara 4.350 frames en 173 s (25,1 Hz), 50 ciclos/100 cargas de 16 KiB y pruebas de fallos FDC. Son pruebas históricas de escenarios concretos. No acreditan peor cuadro, compatibilidad de todas las variantes de CRTC ni tiempo físico de carga. El propio documento separa release Classic e infraestructura Expanded.

## Hardware y límites que sí condicionan el diseño

[V] El Gate Array del CPC clásico ofrece 27 colores físicos; los modos estándar usan 16, 4 o 2 tintas a 160, 320 o 640 píxeles horizontales con 200 líneas. No hay sprites hardware en el clásico. Cambiar tintas durante el barrido aumenta la variedad visible por bandas, pero impone cuándo puede aparecer cada tinta. Fuente: [Gate Array, documentación técnica de Kevin Thacker](https://cpctech.cpcwiki.de/docs/garray.html).

[V] La CPU ve 64 KiB y el vídeo obtiene datos de los 64 KiB principales aunque la CPU pagine RAM adicional. Las configuraciones C4–C7 sustituyen únicamente `0x4000–0x7FFF` por RAM4–7; C0 vuelve a RAM1. Esto permite dejar ISR, pila y audio fijos en RAM0, y pantalla en RAM3. C2 cambia todo el espacio: no es una extensión inocua del esquema anterior. [Tabla de paginación de CPCTelera](https://lronaldo.github.io/cpctelera/files/memutils/cpct_pageMemory-asm.html).

[I, cálculo] Una imagen estándar ocupa 80×200 = 16.000 bytes visibles en una reserva de 16.384. Los 384 bytes restantes están repartidos por la organización del vídeo; no son un bloque contiguo de código libre. Para pantalla estándar sin scroll, una dirección de píxel empaquetado es `base + (y & 7)*0x800 + (y >> 3)*80 + x_byte`. Cambiar parámetros del CRTC invalida asumir esa fórmula sin revisar stride y envoltura.

[V] El compendio actual es **ACCC 1.11, agosto de 2026, 296 páginas**. Se descargó y extrajo su texto; se consultaron clasificación de CRTCs, direccionamiento, sincronía e interrupciones. El antiguo enlace 1.8 devolvía HTML. CRTC 3 corresponde al ASIC Plus; CRTC 4 al ASIC de CPC clásico de coste reducido. El plan prueba 0, 1 y 2, y 4 como cobertura de clásicos adicionales; 3 se registra aparte como Plus. No se afirma que toda combinación estuviera instalada de fábrica en un 6128 concreto. [Logon System, ACCC 1.11](https://shaker.logonsystem.eu/ACCC1.11-EN.pdf), capítulos 4, 7, 19, 24 y 27.

[P] Sincronizarse a VSYNC y contar las interrupciones exige considerar el reinicio del contador del Gate Array y bloques con `DI`. No basta un contador módulo seis arrancado en una fase arbitraria. El prototipo básico evita escrituras CRTC a mitad de imagen; split y scroll tienen una matriz propia de compatibilidad.

[I, cálculo] A 4 MHz, 20 ms equivalen nominalmente a 80.000 T-states. Para un modo de 312 líneas×64 µs, son 19,968 ms y 79.872 T-states. Los presupuestos usan 20 ms redondeados para comunicación; el ensayo debe utilizar el periodo real. La contención/WAIT del CPC exige medir instrucciones efectivas. Una copia lineal ideal de 16 KiB con LDIR cuesta `21*N-5` = 344.059 T-states, 86,015 ms a 4 MHz **antes** de adaptar tiempos CPC. Es un cálculo de instrucciones, no un benchmark: copiar toda una página con ese método cada cuadro no es viable a 50 Hz. Referencia de instrucciones: [manual Z80 de Zilog](https://www.zilog.com/docs/z80/um0080.pdf).

## Técnicas gráficas y su beneficio visible

Las siguientes elecciones son propuestas propias, apoyadas en las operaciones descritas en [sprites por software de Kevin Thacker](https://cpctech.cpcwiki.de/docs/sprites.html) y contrastadas con el renderer local. Las cifras de RAM son cálculos para nuestra escena.

| Técnica | Qué ganamos | Coste y condición |
|---|---|---|
| Más poses, sin cambiar tamaño del actor | Caminar con peso, anticipación, reacción y gestos | 8 poses×2 direcciones×512 B = 8 KiB por personaje alineado. Arte y memoria crecen; el blit conserva su superficie |
| Variante a un píxel en Mode 0 | Movimiento horizontal menos escalonado | El sprite desplazado de 16 píxeles puede abarcar **9 bytes**, no 8. Con dos alineaciones: 8×2×(8+9)×32×2 = **17.408 B por personaje** con máscara intercalada. No cabe en un solo banco |
| Máscara genérica | Transparencia y reutilización compacta de rutinas | Por byte: leer máscara, datos y fondo; AND/OR; escribir. Un byte negro opaco debe dibujarse: no confundir color 0 con transparencia |
| Sprite compilado | Saltar huecos, escribir opacos y enmascarar sólo bordes | Código dependiente del frame. Tamaño y velocidad dependen de runs, registros, dirección y clipping. Versionar x/y arbitrarios evita generar cientos de copias por posición |
| Tiles + piezas singulares | Habitaciones ricas con reutilización | 8×8 píxeles M0 = 32 B/tile. 256 tiles = 8 KiB; mapa 20×25 con índices de un byte = 500 B. Más máscaras, colisiones y piezas únicas se suman aparte |
| Save-under | Fondo caro compuesto una vez | Guardar/restaurar rectángulos y ordenar actores; cuatro de 9×32 necesitan 1.152 B por juego de buffers. Animar el fondo obliga a invalidar correctamente esos datos |
| Fondo limpio + regiones sucias | Recuperación independiente de solapamientos | Una copia limpia de pantalla cuesta 16 KiB; fusionar regiones evita redibujos repetidos. A gran cobertura puede convenir regenerar tiles |
| Doble búfer con regiones por página | Mostrar un cuadro terminado | 32 KiB físicos de vídeo; cada página conserva su historial de actores/HUD de hace dos presentaciones. No basta una sola lista de posiciones antiguas |
| Oclusión por muebles | Profundidad, personajes pasando detrás de objetos | Dibujar fondo, actores ordenados y máscara de primer plano. Sólo refrescar intersecciones. Separar máscara visual de colisión |
| Animación de decorado | Máquinas, luces, café, pequeños efectos | Añadir sus rectángulos a la invalidación; cadencia de 6–12 poses/s puede bastar, sin obligar a actualizar todo el render a ese ritmo |
| Scroll por dirección CRTC | Recorrido continuo sin desplazar todo el framebuffer por CPU | Hay que rellenar bordes, gestionar wrap y posiciones físicas de sprites; scroll grueso estándar no equivale a desplazamiento fino de un píxel |
| Split de HUD / modos mixtos | Texto fino en Mode 1 con escena Mode 0 | ISR en instante preciso; paleta y coordenadas de cada banda; no usar espera ocupada que robe todo el presupuesto de actores |
| Rasters moderados | Iluminación por bandas y transiciones | Reservar tintas y posición de actores. Un actor que cruce la banda puede cambiar de color; resolver con arte o descartar el efecto |
| Overscan | Imagen más grande, presentación espectacular | Aumentan píxeles, memoria y superficie a restaurar. Un ejemplo de 96×272 bytes visibles ya son 26.112 B antes de los huecos de direccionamiento; necesita otro mapa |
| EGX/entrelazados y CRTC intensivo | Imagen de título o escena dirigida | Dependencia de scanlines, paleta y monitor. Se ensayan aparte; no se asigna su coste a cero por funcionar en una demo |

[M] Sobre cuatro poses actuales, de 1.024 posiciones de byte: **380 transparentes, 517 opacas y 127 parciales**. Una especialización podría evitar 380 escrituras y conservar AND/OR sólo en 127 posiciones; siguen existiendo coste de direccionamiento, restauración, saltos, bancos e ISR. Se comprobó equivalencia de la selección por byte sobre 262.144 combinaciones de fondo. No se generó ni ejecutó un sprite compilado Z80 y no se deduce un porcentaje de aceleración de esos recuentos.

[P] El primer generador deberá comparar también inversión en runtime frente a frames preinvertidos, recorte de cajas y variantes sólo para poses frecuentes. Con ocho poses en dos direcciones y dos alineaciones, no presupuestar cuatro personajes completamente diferentes como si todos cupieran en RAM4. Permitir compartir frames de NPC, mantener sólo un conjunto activo o aceptar paso de dos píxeles hasta medir.

## Disco, compresión y recursos

[P] Empezar con DATA, **40 pistas, 9 sectores de 512 B, una cara activa**, identificadores C1–C9. Son 184.320 B brutos; 182.272 B tras 2 KiB de directorio, antes de cabeceras AMSDOS de 128 B y redondeos a bloques. Un archivo no usa necesariamente todos sus bytes asignados. El packer debe inspeccionar la asignación real del DSK y exportar tabla de sectores; no basta asumir que BHRES empieza siempre en C5. El laboratorio sí usa esa ubicación en su disco conocido.

[P] Varias caras implican cambio manual y un identificador de volumen y generación de pack. Colocar paquetes completos de zona en una cara y duplicar recursos pequeños compartidos puede evitar cambios repetidos. No exigir 80 pistas, doble cara automática, M4, HxC/Gotek ni una segunda unidad. Las imágenes para expansiones serían salidas opcionales; validación obligatoria sobre disquete/unidad original.

| Camino | Evidencia | Recomendación |
|---|---|---|
| AMSDOS/firmware | Disponible en la máquina; z88dk documenta CAS/file I/O y sus buffers | Útil para bootstrap. Mantener su workspace durante todo el juego tiene un coste incompatible con varios mapas propuestos |
| FDC del laboratorio | Código disponible, timeouts/resultados y pruebas históricas; interrupciones desactivadas | Primer candidato para transición bloqueante. Auditar contrato de fallo y medir en unidad real |
| Trackloader Arnoldemu distribuido con Phortem | Autor publica fuentes del proyecto y toolchain; Windows 7+ histórico | Referencia concreta para estudiar colocación y música, no biblioteca ya integrada ni compatible por decreto |
| Loader musical de Batman Forever | Autor explica ventanas entre comando y datos, errores y reintentos | Prueba documental de viabilidad. No confundir entrevista con una API reutilizable disponible y validada |

Fuentes: [z88dk CPC, file I/O](https://github.com/z88dk/z88dk/wiki/Platform---Amstrad-CPC), [publicación de Phactory/Phortem, 21-02-2014](https://www.norecess464.com/es/index.html), [entrevista al equipo de Batman Forever](https://memoryfull.net/articles.php?id=23).

[V] El µPD765A distingue fases comando/ejecución/resultado y bits de disponibilidad/dirección. Servir datos tarde puede producir overrun; una ISR musical arbitraria durante transferencia no es una solución. Referencia del fabricante: [NEC µPD765A/µPD7265](https://cpctech.cpcwiki.de/docs/upd765a/necfdc.htm). [I] A una tasa nominal de 250 kbit/s, 512 bytes necesitan 16,384 ms de datos, sin gaps, búsqueda ni rotación. Para 16 KiB el límite ideal de datos es 524,288 ms; **no es latencia de carga medida**. Motor, seek, posición angular, gaps, reintentos, CRC y descompresión aumentan el tiempo.

[P] Primera política de audio durante carga: fade/pausa deliberada y reinicio coherente. Después, comparar un loader que programe música entre transferencias y valide jitter. No llamar a un AKG completo dentro del bucle de bytes del FDC. Los resultados históricos del laboratorio no contienen esa integración.

[M] Compresión ejecutada con ZX0 y LZSA raw 1/2, seguida de descompresión host idéntica byte a byte:

| Corpus | Sin comprimir | ZX0 | LZSA1 | LZSA2 |
|---|---:|---:|---:|---:|
| 4 poses fuente con máscara | 2.048 | 384 | 469 | 412 |
| Pantalla de carga real de Banterhouse | 16.384 | 6.292 | 7.328 | 6.516 |
| Pantalla sintética del laboratorio | 16.384 | 2.337 | 2.708 | 2.457 |
| 6 salas del laboratorio concatenadas | 711 | 474 | 582 | 530 |

No elegir algoritmo sólo por esta tabla: concatenar salas mejora diccionario pero pierde acceso independiente; el fixture no representa arte nuevo; comprimir máscaras ahorra disco, no RAM activa si se expanden. ZX0 ganó tamaño en estos cuatro corpus. **No se midió la descompresión Z80**, memoria de pila del descompresor ni carga FDC. Fuentes de formatos/código: [ZX0](https://github.com/einar-saukas/ZX0), [LZSA](https://github.com/emmanuel-marty/lzsa).

[P] Comparar decoder ZX0 pequeño frente a variantes rápidas y LZSA1/2. Fijar versión de formato (ZX0 moderno frente a clásico), dirección forward/backward, distancia máxima, pila, código y solape permitido. Cada bloque tendrá tamaño comprimido, expandido, destino, banco y CRC. Un bloque comprimido puede crecer: el packer debe conservar opción raw. BitBuster y Exomizer quedan como controles secundarios por su presencia documentada en Phactory/Phortem, sin extrapolar tiempos. No introducir cuatro decoders en el núcleo final.

[P] Carga entre zonas antes de streaming: precargar animaciones y mantenerlas listas; nunca descomprimir una pose larga dentro de un cuadro crítico. Overlays de código sólo para menú, transición o escenas excluyentes cuando el mapa real lo exija. Requieren ABI, checksum y prohibir retorno hacia un overlay ya sustituido.

## Audio, entrada y simulación

[V] Arkos Tracker 3 separa editor, exportación y reproductores. Su autor recomienda AKG o AKM para juegos; AKY intercambia tamaño musical por trabajo del reproductor y FAP se orienta a demos. El coste depende de configuración, canción y SFX. No usar «12 scanlines» publicado para AKY como máximo medido de nuestro AKG. Sus players RAM pueden automodificarse y deben estar en RAM escribible. [Comparativa oficial](https://www.julien-nevo.com/arkostracker/index.php/players-overview/).

[P] Probar AKG con una exportación mínima de funciones usadas, canción y efectos simultáneos. Guardar player y datos calientes en memoria fija. Si no caben, evaluar AKM, fragmentos precargados o una breve paginación desde ISR que restaure exactamente el banco anterior. El último camino complica reentrancia del banco y acceso a recursos; no es la primera elección.

[V] CHIPNSFX es una alternativa compacta con código y suite publicada por CNGSoft; el autor anuncia players de 550–950 B según configuración, que aquí no se han ensamblado. WYZ figura entre los recursos de 8BP. Comparar expresividad musical y SFX, además de bytes. No se verificó en esta sesión una licencia completa de redistribución de CHIPNSFX/WYZ. [CHIPNSFX del autor](http://cngsoft.no-ip.org/chipnsfx.htm), [8BP](https://github.com/jjaranda13/8BP).

[P] Música y lectura de controles a 50 Hz nominales; simulación fija a 25 o 50 Hz elegida antes del ensayo; render independiente. Para comparar render a 25 Hz, conservar la misma simulación a 50 Hz y renderizar cada dos ticks. Si se pierde un deadline, registrar el fallo; no ralentizar silenciosamente música y juego ni añadir pasos ilimitados de recuperación. En teclado/AY, coordinar PPI y selección de registros para que la ISR no interrumpa una transacción incompatible. Reservar canales/prioridades de SFX y medir el tick más caro de la canción completa.

## Casos que sí aportan evidencia trasladable

| Caso y fuente primaria | Qué consta | Qué podemos trasladar / qué no consta |
|---|---|---|
| [Batman Forever, entrevista a Rhino](https://www.norecess464.com/articles/interview-rhino/index.html) | Describe herramientas de producción y modificación del player AYC para consumo seleccionable constante | Storyboard, preparación de recursos y audio predecible; no acredita un motor general de actores ni fuente completa disponible |
| [Loader de Batman Forever, Arnoldemu](https://memoryfull.net/articles.php?id=23) | Explica sectores de 512 B, gaps, reintentos y música antes de la fase de datos; reconoce no disponer de tasa precisa | Diseño de transiciones con audio. No copiar una cifra de velocidad inexistente ni suponer fiabilidad con cualquier drive |
| [Phortem, autor](https://www.norecess464.com/productions/phortem/index.html) | Versiones clásico/Plus, fuente publicada, loader y compresor acreditados | Composición, transiciones y cadena de recursos; distinguir paleta Plus. No trasladar el presupuesto completo de una secuencia pasiva al gameplay |
| [Mørketid, fuente en TRSE](https://github.com/leuat/TRSE/blob/master/Publish/tutorials/AMSTRADCPC/Morketid/main.ras) | Autor identifica demo CPC 464, código íntegro TRSE y configuración de música AKG; advierte diferencia entre lanzamiento por inyección y disco | Ejemplo concreto de CRTC, arte y audio generado. Aquí se leyó, no se compiló ni se validó en 128K |
| [Pinball Dreams, mensaje de su desarrollador](https://www.cpcwiki.eu/forum/games/pinball-illusions-new-game-from-batman-group%21%21/175/) | El autor explica producción cruzada con WinAPE y fuente de más de 350 KB en ese momento | El volumen de fuente host puede superar RAM objetivo. No se encontró en esta revisión un motor público reutilizable ni evidencia para atribuirle nuestro algoritmo de sprites |
| [8BP, GameExamples](https://github.com/jjaranda13/8BP/tree/master/GameExamples) | Código y juegos de ejemplo distribuidos por el autor; NOMWARS incluye edición DSK | Base para evaluar una librería real, no sólo vídeo. No se midió su renderer ni se dio por validado su mapa para Banterhouse 2 |

[P] Dos demostradores artísticos alternativos: sala de cómic con 4 actores, primer plano y HUD; pasillo con la misma carga y cámara móvil. Comparar área útil, legibilidad, expresividad, peor cuadro y horas de conversión de arte. La cámara móvil sólo debe ganar si mejora el juego lo suficiente para pagar su motor, clipping, bordes y compatibilidad.

## Flujo de producción en este Mac

[P] Arte maestro editable en Aseprite (comercial, no comprado) o editor existente; exportación PNG indexado con transparencia explícita, paleta y metadatos. Aseprite es editor, no conversor CPC ni motor. Mapas Tiled/JSON con capas separadas de colisión y oclusión; seguir el JSON local si ya evita una conversión innecesaria. [Aseprite FAQ](https://www.aseprite.org/faq/), [Tiled](https://www.mapeditor.org/).

[P] Conversor propio pequeño y determinista para píxel/máscara/alineaciones, inspirado o contrastado con [Martine](https://github.com/jeromelesaux/martine). Validar previsualización de píxeles CPC, paleta global y aspecto en monitor 4:3; no aprobar arte únicamente ampliando píxeles cuadrados. Martine convierte recursos; sus opciones de Plus no crean capacidad del clásico.

[P] Build con versiones/commits fijados: exportar → validar → generar C/ASM/binario → comprimir bloques → asignar bancos → enlazar → verificar mapas/ABI → empaquetar DSK → hashes. El orden importa; serializar escrituras al DSK. Fallar si cambia el formato, un frame falta, un bloque cruza banco, se solapan regiones o el bootstrap sobreescribe lo que aún necesita. Dos builds limpios deben producir los mismos bytes; no incluir timestamps variables en el contenedor.

[P] Depuración: ACE-DL y símbolos para inspección, Caprice32 para automatización y segundo emulador independiente. El emulador nativo de Banterhouse está presente, pero no se lanzó ni se midieron nuevos cuadros aquí. ACE-DL publica Mac Intel/ARM y API; se verificó disponibilidad documental, no instalación operativa. [ACE-DL](https://roudoudou.com/ACE-DL/), [Caprice32](https://github.com/ColinPitrat/caprice32).

[P] Perfilado: marcas de borde por fase, contadores de ciclos del emulador y traza de eventos de música/presentación/FDC. Instrumentación condicionada a build; cuantificar su overhead. Mantener instantáneas y entradas deterministas. En hardware, vídeo lento o captura y cronometraje de carga; para tiempos de ISR precisos usar analizador lógico si está disponible. No hay CPC físico accesible en esta sesión.

## Cambios respecto a las hipótesis iniciales

1. Conservar CPCTelera es una opción principal, no un residuo de una migración decidida.
2. La ubicación actual del código es `0x3D00`; no usar cifras históricas de mapa como ocupación del build nuevo.
3. Un personaje de 8 poses, 2 direcciones y 2 alineaciones con máscara ocupa 17 KiB, no 16 KiB exactos: el desplazamiento añade una columna.
4. La ISR de audio debe ser trabajo nuevo; el tick actual está en el bucle y el FDC usa `DI`.
5. La ventana bancaria impide descomprimir ingenuamente RAM7→RAM4 si ambas usan `0x4000`.
6. El compendio de referencia es 1.11; los tipos CRTC 3 y 4 no deben agruparse como «Plus».
7. ZX0 ahorra más disco en el corpus ensayado, pero faltan los tiempos CPC para decidir el decoder.

Las decisiones pendientes y el orden de implementación están en [PROTOTYPE_PLAN.md](PROTOTYPE_PLAN.md). Esta investigación proporciona una base verificable para esa implementación; no certifica FPS, carga musical continua ni compatibilidad física.
