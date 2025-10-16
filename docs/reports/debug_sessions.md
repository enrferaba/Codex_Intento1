# Registro de sesiones de depuración

Este archivo resume los avances documentados al ejecutar `python scripts/debug_suite.py`
y `feriactl debug report`. Sirve como referencia rápida de qué se ha instrumentado
hasta el momento y cómo interpretar los registros persistidos.

## Sesión actual

- Se amplió la instantánea para capturar `working_directory`, `git_branch`,
  `git_commit`, el indicador `git_dirty` y ahora también `python_path`, lo que
  permite reproducir el estado exacto del repositorio y de los imports durante
  la depuración.
- `scripts/debug_suite.py` admite `--output` y `--append`, y ahora también
  `--command`/`--full` para ejecutar comprobaciones adicionales (incluyendo
  `python -m feriactl.main debug report` bajo `FERIA_DEBUG=1`).
- Las pruebas unitarias cubren el flujo de escritura, la ejecución de comandos y
  la propagación de códigos de salida, garantizando que la bitácora no se
  corrompa al ejecutar sesiones consecutivas.
- `docs/reports/debug_progress.md` incorpora las instrucciones actualizadas para
  mantener el diario histórico y detalla la sección `command_results` del
  informe JSON.
- El registro JSONL conserva tanto ejecuciones exitosas como fallidas (`status`
  = `ok`/`error`), útil para auditar problemas reproducidos durante sesiones de
  depuración.

> Ejecuta `python scripts/debug_suite.py --json --output docs/reports/debug_sessions.jsonl --append`
> para añadir la próxima instantánea cruda asociada a esta entrada.
