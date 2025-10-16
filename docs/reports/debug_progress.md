# Diario de depuración

Este archivo sirve como bitácora viva del trabajo de instrumentación y verificación
en FERIA Precision Codex. Mantenerlo dentro del repositorio facilita compartir el
estado actual con cualquier persona que abra el proyecto en modo depuración.

## Instantáneas disponibles

* `core.debug.collect_snapshot()` — genera una instantánea estructurada con la
  configuración de logging, flags de entorno y módulos cargados.
* `scripts/debug_suite.py` — imprime la instantánea anterior y, opcionalmente,
  ejecuta `pytest` para validar el entorno activo.
* `feriactl debug report` — expone la misma información desde la CLI para
  operadores que no tienen acceso directo a Python.

## Flujo sugerido

1. Ejecutar `python scripts/debug_suite.py` para guardar en consola la
   instantánea resumida.
2. Usar `python scripts/debug_suite.py --json > debug_snapshot.json` cuando se
   necesite compartir los detalles exactos con el equipo.
3. Opcionalmente añadir `--output docs/reports/debug_sessions.jsonl --append`
   para mantener un registro histórico de instantáneas directamente en el
   repositorio.
4. Lanzar `feriactl --debug debug report` desde cualquier estación para comprobar
   rápidamente qué flags están activos en los servicios remotos.
5. Alternativamente, ejecutar `make debug-report` para producir el JSON utilizando
   el runtime configurado por `uv`.

## Campos adicionales capturados

La instantánea incluye ahora información de Git para contextualizar la sesión de
depuración:

* `working_directory` — ruta absoluta desde la que se ejecutó el informe.
* `git_branch` y `git_commit` — referencia corta a la rama y el commit activo.
* `git_dirty` — indicador booleano de si hay cambios sin confirmar.

Estos campos aparecen tanto en el JSON como en la salida formateada, lo que
facilita correlacionar la depuración con el estado del repositorio.

## Qué registrar

Documenta aquí los hallazgos relevantes, por ejemplo:

* Cambios en variables de entorno aplicadas en producción.
* Resultados de `pytest` cuando se ejecutan con `--run-tests`.
* Trazas significativas encontradas al revisar los logs DEBUG.

> Actualiza este diario tras cada sesión de depuración relevante para mantener
> la trazabilidad histórica de la plataforma.
