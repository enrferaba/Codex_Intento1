# Runbook: Drift de consultas/datos

1. Observa alertas `drift` y analiza histogramas de intents.
2. Lanza `feriactl eval run --set drift-sanity` para comparar métricas.
3. Reindexa repos afectados (`feriactl ingest <repo>`).
4. Recalibra umbrales de abstención con `scripts/eval_nightly.py --calibrate`.
5. Actualiza reportes en `docs/reports/` y comunica a interesados.
