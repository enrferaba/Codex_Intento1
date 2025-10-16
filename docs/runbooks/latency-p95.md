<!-- cspell:disable -->
# Runbook: Latencia /query P95 alta

1. Revisa `feriactl health --verbose` para confirmar profundidad de colas.
2. Inspecciona dashboards de GPU y router.
3. Ajusta `micro_batch` y `max_new_tokens` según headroom.
4. Activa `kill-switch` para colas batch/eval si es necesario.
5. Verifica recuperación < 10 minutos y documenta en postmortem.
