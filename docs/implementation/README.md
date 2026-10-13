# Planes y seguimiento de implementación

[Guía de lectura](../README.md) · [Estado actual](../STATUS.md)

Esta carpeta conserva contratos y registros de varias etapas. No está pensada como tutorial de primera compilación: para eso está [Del código a un disquete](../development/GETTING_STARTED.md).

| Etapa | Plan | Estado |
|---|---|---|
| Implementación T y optimización O | [Plan principal](../IMPLEMENTATION_PLAN.md), [optimización](OPTIMIZATION_PLAN.md) | [STATUS.json](STATUS.json) |
| Reparación inicial E | [Plan de entrega](DELIVERY_REPAIR_PLAN.md) | [DELIVERY_STATUS.json](DELIVERY_STATUS.json) |
| Reparación de física F | [Plan de física](PHYSICS_REPAIR_PLAN.md) | [PHYSICS_STATUS.json](PHYSICS_STATUS.json) |
| Revalidación autónoma N | [Plan autónomo](AUTONOMOUS_REPAIR_PLAN.md) | [AUTONOMOUS_STATUS.json](AUTONOMOUS_STATUS.json) |

Los registros antiguos pueden describir una build rechazada o un experimento que ya no es la entrega actual. La revalidación N00–N10 y el [informe de entrega](../DELIVERY_REPORT.md) describen el prototipo de referencia. La prueba web posterior sigue pendiente según [Estado](../STATUS.md).

[CONTRACTS](CONTRACTS.md), [TASKS](TASKS.md), [TESTS](TESTS.md), [OPTIMIZATION_TASKS](OPTIMIZATION_TASKS.md) y [OPTIMIZATION_TESTS](OPTIMIZATION_TESTS.md) detallan los contratos. Los ejecutores automatizados tienen instrucciones en [AUTONOMOUS_EXECUTOR](AUTONOMOUS_EXECUTOR.md) y [EXECUTOR_PROMPT](EXECUTOR_PROMPT.md).

Las rutas a `research/runs/` identifican evidencia del archivo local, excluido del repositorio. Los estados PASS históricos no pueden volverse a verificar desde un clon que carece de esas capturas. No marques una revisión artística, humana o de hardware como aprobada porque pasen tests host.
