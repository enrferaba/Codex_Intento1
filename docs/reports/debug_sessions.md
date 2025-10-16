# Registro de sesiones de depuración

Este archivo resume los avances documentados al ejecutar `python scripts/debug_suite.py`
y `feriactl debug report`. Sirve como referencia rápida de qué se ha instrumentado
hasta el momento y cómo interpretar los registros persistidos.

## Sesión actual

- Se amplió la instantánea para capturar `working_directory`, `git_branch`,
  `git_commit` y el indicador `git_dirty`, lo que permite reproducir el estado
  exacto del repositorio durante la depuración.
- `scripts/debug_suite.py` ahora acepta `--output` y `--append`, habilitando un
  historial JSONL dentro del repositorio sin pasos manuales adicionales.
- Las pruebas unitarias cubren el flujo de escritura y la acumulación en disco,
  garantizando que la bitácora no se corrompa al ejecutar sesiones consecutivas.
- `docs/reports/debug_progress.md` incorpora las instrucciones para mantener el
  diario histórico y los nuevos campos recogidos.

> Ejecuta `python scripts/debug_suite.py --json --output docs/reports/debug_sessions.jsonl --append`
> para añadir la próxima instantánea cruda asociada a esta entrada.
