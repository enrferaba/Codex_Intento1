<!-- cspell:disable -->
# Runbook: Restaurar desde snapshot

1. Selecciona snapshot con `feriactl snapshot list`.
2. Ejecuta `feriactl snapshot restore <id>` y verifica hashes.
3. Restaura índices FAISS con `scripts/snapshot_restore.py`.
4. Ejecuta smoke tests `make test` y `feriactl health`.
5. Documenta tiempo total y métricas en `docs/reports/drills.md`.
