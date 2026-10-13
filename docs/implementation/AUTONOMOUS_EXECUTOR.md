# Instrucción lista para implementar y probar de forma continua

Este documento prepara la ejecución solicitada. No crea una automatización ni acredita que haya empezado. Copiar el bloque completo al ejecutor; no requiere preguntas técnicas al usuario para arrancar.

```text
Implementa y prueba de principio a fin la reparación autónoma de Banterhouse 2
exclusivamente en ..

Lee AGENTS.md, docs/IMPLEMENTATION_PLAN.md y los estados de producción,
entrega y docs/implementation/AUTONOMOUS_STATUS.json. Lee
AUTONOMOUS_REPAIR_PLAN.md completo una vez; después consulta la ficha activa.
El usuario rechaza el candidato anterior: los BIN fallan, la primera fase
suena sólo a beats y quedan ventanas de pruebas abiertas. No uses el PASS
histórico E00–E04 para declarar resuelto ese reporte.

Ejecuta N00–N10 secuencialmente, una tarea habilitada cada vez. Continúa con
la siguiente sin pedir confirmación ni terminar después de la primera.
Esta instrucción de ejecución continua prevalece sobre el antiguo prompt
que decía ejecutar sólo una tarea por sesión. No delegues sin autorización.
Marca execution_started=true al comenzar N00. Una nueva sesión reanuda
substep/remaining del estado actual, no empieza de nuevo ni repite a ciegas.

Primero conserva artefactos/reportes, retira aceptación y aísla pruebas.
Después reproduce cada fallo, corrige causas, verifica launcher y teclado,
juego, música, campaña completa, empaquetado y limpieza final. La entrega
es el DSK del juego: los BIN de diagnóstico se prueban por su propio DSK y
comando, fuera del paquete para Fernando. No culpes al usuario por cargarlo.

No necesitas intervención humana para pulsar teclas, capturar resultados,
cerrar ventanas ni continuar las tareas técnicas autorizadas. Usa Computer
Use para UI y APIs/CLI documentadas para herramientas no interactivas.
No eludas restricciones de Computer Use con AppleScript u otra inyección.
Si aparece bloqueo de pantalla, aplica la skill de desbloqueo únicamente
cuando se cumplan sus condiciones de autorización; si no, registra bloqueo
externo y continúa trabajo independiente. No cambies seguridad del Mac.

Cada run tiene configuración y carpeta privadas, hashes, inputs,
aserciones y evidencia. Un solo emulador propio a la vez, identificado por
PID, hora de inicio, argumentos y ventana. No confundas el raw cap32 de
otra tarea con el bundle del juego. No mates por nombre. Si una ejecución
ajena modifica los inputs del candidato, invalida la prueba y usa una copia
congelada. No reconstruyas ni cambies el disco mientras lo estás validando.

En finally, tanto PASS como FAIL: suelta teclas, detén capturas, guarda
logs, cierra emulador/visores propios, libera bloqueo y verifica inventario.
No vuelvas a seleccionar una app cerrada para verificar: puede relanzarla.
No abras cada PNG en Preview. No dejes capturas en raíz o Escritorio. No
borres evidencias antiguas ni archivos personales para hacer espacio.
Comprueba cuota de disco antes de build/vídeo; usa capturas acotadas.

Música obligatoria: motivo tonal temprano, bajo, acompañamiento y variación
A/B de 16 compases con carácter pop/funk de los 80. Verifica PCM de la
salida real del runtime, no sólo tablas de notas, ON/OFF ni log del driver.
Comprueba convivencia de SFX y recuperación de canales, mute y pausa.
No certifiques escucha humana ni altavoces desde una traza AY. Reutiliza
las fuentes musicales existentes respetando procedencia; no introduzcas
migración de player sin evidencia de necesidad y ABI comprobada.

Reutiliza harness y checkers disponibles. Los comandos futuros descritos
en N01/N07/N09 deben implementarse antes de invocarlos; no inventes flags.
Host no sustituye Z80, snapshot final no sustituye teclado/audio/scanout.
Prueba los validadores con negativos: deben detectar averías, evidencia
vieja, disco distinto, silencio o canal tonal roto y residuos de limpieza.

Mantén un registro por hipótesis/fix/regresión. Tras dos intentos sin avance,
reduce el caso y revisa diagnóstico; no pares por ese número ni repitas sin
información. Si falta capacidad externa imprescindible, registra bloqueo
con prueba concreta; nunca conviertas null/timeout en PASS. Guarda fallo
y siguiente acción. No cambies esperados desde el resultado defectuoso.

La revisión artística humana y el CPC físico siguen pendientes, sin frenar
la reparación técnica del prototipo ni ser aprobados automáticamente.
Completar 24 arenas no implementa las escenas narrativas aún ausentes.
No tocar ../banterhouse; no compras, publicación ni mensajes.

Sólo N10 puede declarar ready_for_user, tras campaña, audio, negativos,
arranque del paquete final y cero ventanas/procesos propios residuales.
Entrega DSK, lanzador, hashes y resumen de pruebas realmente ejecutadas.
No dejes abierto el juego al acabar: el usuario lo abrirá cuando lo pida.
No prometas que estará listo a una hora si quedan casos sin resolver.
```
