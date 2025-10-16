<!-- cspell:disable -->
# Runbook: OOM / VRAM alta

1. Identifica workers con `feriactl status` y métricas `gpu_memory_bytes`.
2. Reduce `max_new_tokens` y `micro_batch` en el governor.
3. Evacúa workloads no críticos (`batch`, `eval`).
4. Limpia KV-cache con el comando `feriactl simulate --kill-cache` (pendiente de implementación).
5. Documenta incidente y ajusta umbrales preventivos.
