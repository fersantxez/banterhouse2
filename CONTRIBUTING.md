# Colaborar en Banterhouse 2

Empieza por [la primera compilación](docs/development/GETTING_STARTED.md) y [el mapa del código](docs/development/REPOSITORY.md). El objetivo es un CPC 6128 clásico de 128 KiB; no presupongas Plus ni expansiones.

## Un cambio pequeño, una prueba que lo explique

1. Explica qué problema arreglas y qué verá el jugador.
2. Cambia la entrada o el módulo responsable, sin editar a mano un generado si tiene generador.
3. Ejecuta `make test-host` y las pruebas específicas del cambio.
4. Si cambia el juego CPC, construye `make campaign-disk` y pruébalo en emulador.
5. Ejecuta `make public-check` antes de preparar el commit.

En una propuesta de cambio incluye el comportamiento anterior y nuevo, los comandos ejecutados y los límites de la prueba. No prometas rendimiento, compatibilidad física o calidad artística a partir de una compilación correcta.

## Evidencia y limpieza

Guarda capturas y resultados bajo `research/runs/`, con el hash de la build. Cierra los procesos y ventanas creados por tu prueba incluso si falla. No borres evidencia antigua ni termines procesos de otras aplicaciones por nombre.

No incluyas ROM, MIDI privados, claves, sesiones personales ni paquetes de despliegue. Revisa [las atribuciones](THIRD_PARTY.md) antes de incorporar recursos externos.

La documentación se escribe en español y debe separar hechos medidos, hipótesis y planes. Para un bug incluye DSK/hash, emulador/modelo, pasos, resultado esperado y observado; puedes usar la plantilla de incidencia.
