# Instrucción para 6.1 Luna

**Prioridad actual:** para la reparación solicitada usar [AUTONOMOUS_EXECUTOR.md](AUTONOMOUS_EXECUTOR.md) y [AUTONOMOUS_STATUS.json](AUTONOMOUS_STATUS.json). El bloque siguiente queda para tareas de producción posteriores; no debe detener la reparación tras una sola ficha.

Este prompt activa implementación cuando el usuario lo envíe. El plan por sí solo no ejecuta tareas. Copiar el bloque completo. Si el usuario pide una tarea concreta, seleccionarla sólo si sus dependencias están terminadas; explicar cuál falta y trabajar primero en el requisito habilitado cuando esté dentro del encargo.

```text
Implementa UNA tarea habilitada de Banterhouse 2 en
. siguiendo el plan v2.

1. Lee AGENTS.md, docs/IMPLEMENTATION_PLAN.md y
   docs/implementation/STATUS.json y DELIVERY_STATUS.json. Si queda E00–E04
   habilitada, ejecuta primero su ficha de DELIVERY_REPAIR_PLAN.md. Reanuda una tarea in_progress habilitada;
   si no hay, toma la primera pending cuyas dependencias sean todas done,
   respetando el orden del array tasks. El primer trabajo del plan es O00.
   No ejecutes toda la campaña en esta sesión.
2. Para ID T lee su ficha en docs/implementation/TASKS.md. Para ID O lee
   docs/implementation/OPTIMIZATION_PLAN.md y su ficha en
   docs/implementation/OPTIMIZATION_TASKS.md. Lee sólo contratos C y pruebas
   necesarios en CONTRACTS.md, TESTS.md y OPTIMIZATION_TESTS.md. OP01–OP20 son
   pruebas de optimización; O00–O16 son tareas, y O01–O10 en TESTS son pruebas
   de disco. No confundir esas tres nomenclaturas.
3. Lee cada archivo antes de editarlo. Ya hay prototipo C/CPCTelera, ASM de
   ZX0 y salidas BIN/DSK; no los borres por seguir una ficha antigua que dice
   crear. O00 conserva y reconcilia lo existente. Un .s con datos .db no es
   un renderer compilado y un DSK existente no acredita pruebas pasadas.
4. Marca tarea in_progress y substep con el paso numerado. Ejecuta los pasos
   en orden, un cambio de causa por experimento. Un subpaso estable puede
   ocupar la sesión: registra remaining y no marques toda la tarea done.
5. Los comandos futuros tienen tarea creadora. Comprueba scripts y rutas
   antes de invocarlos; una receta Make puede estar rota. Disponible ahora:
   python3 tools/check_implementation_plan.py
   Este comando sólo comprueba documentación. No inventes opciones CLI del
   emulador, callbacks del SDK ni contadores temporales que no hayas leído.
6. Mantén CPC 6128 clásico de 128 KiB, arte Mode 0 aprobado y reglas de los
   contratos. No cambies cámara, personajes, paleta, poses, audio, colisión
   ni cadencia para ganar un benchmark. Conserva C/SDCC/SDAS/CPCTelera y ABI
   mientras no haya una decisión técnica respaldada por la comparación.
7. ../banterhouse es SOLO LECTURA. No ejecutes allí make, pruebas,
   runners ni emuladores que puedan guardar configuración. Las referencias
   se copian de forma acotada a la secuela con hashes/procedencia. Conserva
   cambios del usuario. No compres, publiques, envíes mensajes ni hagas commit.
8. Ejecuta caso pequeño, regresiones afectadas y gate de la ficha. No crees
   otro harness si ya existe uno adecuado. Host no sustituye ejecutar Z80;
   framebuffer final no demuestra scanout; emulador no certifica hardware.
   Medir CPU requiere un backend temporal comprobado, no time.time() del Mac.
9. Cada run va en carpeta nueva research/runs/ con comandos/exit codes,
   hashes, entorno, resultados, fallos y siguiente acción. No sobrescribas
   baselines ni regeneres esperados desde una prueba fallida. Falta de dato
   es null/blocked, no cero/PASS. Sigue las reglas de epsilon y equivalencia
   antes de afirmar aceleración. Guarda también experimentos rechazados.
10. Si falla ABI/IRQ/bancos/FDC, reduce caso y cambia una causa cada vez. Tras
    dos intentos distintos sin avance, conserva reproducción mínima, logs e
    hipótesis para revisión técnica. No desactives pruebas, límites o audio.
    Sin entorno requerido registra bloqueo; sólo continúa trabajo independiente
    habilitado. No solicites permiso para pasos reversibles ya autorizados.
11. Para H0–H5 o hardware, prepara primero artefacto concreto, hashes, controles,
    instrucciones y formulario. No inventes partidas/opiniones/resultados.
    T18 puede esperar mientras se mide O03–O14; producción requiere H2/T20.
    O16 permite preparar emulación; sólo T34 habilita hardware_verified.
12. Actualiza STATUS.json: substep, evidence, remaining, blocker y outcome en
    experimentos O. Done exige todos los criterios; rejected puede cerrar un
    experimento ejecutado, pero su código no se activa. Ejecuta el comprobador
    documental tras editar dependencias/estado. No alteres el grafo para saltar
    un fallo.

Al terminar informa: tarea/subpaso, archivos cambiados, comandos realmente
usados, casos pass/fail/blocked, cifras medidas con entorno, decisión sobre
variante, limitaciones y próximo paso exacto. No presentes metas de FPS como
prestaciones verificadas.
```
