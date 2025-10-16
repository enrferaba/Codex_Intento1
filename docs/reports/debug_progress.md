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
3. Lanzar `feriactl --debug debug report` desde cualquier estación para comprobar
   rápidamente qué flags están activos en los servicios remotos.
4. Alternativamente, ejecutar `make debug-report` para producir el JSON utilizando
   el runtime configurado por `uv`.

## Qué registrar

Documenta aquí los hallazgos relevantes, por ejemplo:

* Cambios en variables de entorno aplicadas en producción.
* Resultados de `pytest` cuando se ejecutan con `--run-tests`.
* Trazas significativas encontradas al revisar los logs DEBUG.

> Actualiza este diario tras cada sesión de depuración relevante para mantener
> la trazabilidad histórica de la plataforma.
