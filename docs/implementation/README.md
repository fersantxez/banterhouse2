# Planes y tareas

Esta carpeta guarda las tareas, decisiones y resultados de las distintas etapas del desarrollo. Para compilar el juego, sigue [estas instrucciones](../development/GETTING_STARTED.md).

| Etapa | Plan | Registro de tareas |
|---|---|---|
| Implementación T y optimización O | [Implementación](../IMPLEMENTATION_PLAN.md), [optimización](OPTIMIZATION_PLAN.md) | [STATUS.json](STATUS.json) |
| Reparación inicial E | [Entrega](DELIVERY_REPAIR_PLAN.md) | [DELIVERY_STATUS.json](DELIVERY_STATUS.json) |
| Reparación de física F | [Física](PHYSICS_REPAIR_PLAN.md) | [PHYSICS_STATUS.json](PHYSICS_STATUS.json) |
| Revalidación N | [Revalidación](AUTONOMOUS_REPAIR_PLAN.md) | [AUTONOMOUS_STATUS.json](AUTONOMOUS_STATUS.json) |

Los registros conservan también fallos y versiones rechazadas. La entrega publicada corresponde a N00–N10 y está descrita en el [informe de entrega](../DELIVERY_REPORT.md). Las pruebas web pendientes figuran en [Estado](../STATUS.md).

Los requisitos de cada tarea están en [CONTRACTS](CONTRACTS.md), [TASKS](TASKS.md), [TESTS](TESTS.md), [OPTIMIZATION_TASKS](OPTIMIZATION_TASKS.md) y [OPTIMIZATION_TESTS](OPTIMIZATION_TESTS.md). [AUTONOMOUS_EXECUTOR](AUTONOMOUS_EXECUTOR.md) y [EXECUTOR_PROMPT](EXECUTOR_PROMPT.md) contienen las instrucciones para ejecutarlas con un agente.

Las capturas y registros de `research/runs/` se guardan fuera del repositorio público. Para volver a comprobar esos resultados hay que recuperar los archivos o repetir las pruebas. Los tests del ordenador no aprueban las revisiones de arte, las pruebas con jugadores ni las pruebas en hardware.
