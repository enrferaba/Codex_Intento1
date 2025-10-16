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
* `python_path` — lista exacta de rutas en `sys.path` para reproducir cómo se
  resolvieron los imports durante la sesión.

Estos campos aparecen tanto en el JSON como en la salida formateada, lo que
facilita correlacionar la depuración con el estado del repositorio.

## Modo completo y captura de comandos

* `scripts/debug_suite.py` acepta `--command` para ejecutar y registrar cualquier
  instrucción adicional. Las salidas (stdout/stderr), códigos de retorno y el
  tiempo de ejecución quedan incrustados en el informe.
* El flag `--full` añade automáticamente dos comprobaciones clave: `python -m
  feriactl.main debug report --json` y `python scripts/dev_debug.py ...`, además
  de habilitar `pytest` al final del flujo.
* El informe JSON añade un bloque `command_results` con el detalle de cada
  comando; el formato de texto imprime una sección `# Resultados de comandos`
  para inspección humana inmediata.
* Si algún comando falla, el script finaliza con código ≠ 0 y emite una alerta en
  stderr (`Al menos un comando finalizó con errores`).

> Mantén estos comandos documentados aquí tras cada sesión para que el equipo
> pueda reproducir paso a paso las comprobaciones ejecutadas.

## Qué registrar

Documenta aquí los hallazgos relevantes, por ejemplo:

* Cambios en variables de entorno aplicadas en producción.
* Resultados de `pytest` cuando se ejecutan con `--run-tests`.
* Trazas significativas encontradas al revisar los logs DEBUG.

> Actualiza este diario tras cada sesión de depuración relevante para mantener
> la trazabilidad histórica de la plataforma.

## Sesión 2025-10-16 — Depuración integral

* Activado el modo `--full` para validar CLI y scripts auxiliares junto al
  reporte principal.
* Registradas las salidas de `feriactl debug report` (vía `python -m
  feriactl.main`) y del wrapper `dev_debug`
  con `FERIA_DEBUG=1`.
* Confirmado que los fallos en comandos fallan la sesión con exit code ≠ 0 y un
  mensaje explícito en stderr.
* Guardada la instantánea completa (con `python_path` y `command_results`) en
  `docs/reports/debug_sessions.jsonl` mediante `--output ... --append`.
* La primera ejecución fallida permanece registrada como evidencia del
  comportamiento ante errores; la posterior repetición exitosa valida las
  comprobaciones con estado `ok`.

## Sesión 2025-10-17 — Governor y Scheduler

* Se implementó el `GpuGovernor` con PID + feed-forward, verificando los casos
  de aumento de escala y protección ante límites térmicos/memoria a través de
  pruebas unitarias dedicadas.
* El `JobScheduler` ahora reparte cargas respetando perfiles MIG, temperatura y
  utilización máximas de GPU.
* `scripts/simulate_load.py` registra la decisión del governor tras cada
  simulación y expone nuevas banderas `--with-governor`/`--target-util` para
  acompañar la instrumentación descrita en el lienzo maestro.
* El histórico JSONL se ha actualizado automáticamente con la nueva ejecución
  completa de la suite de depuración.
