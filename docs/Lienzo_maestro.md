# Lienzo maestro — FERIA Precision Codex

> **Nota:** Este documento contiene las instrucciones completas del programa. **No borrar.**

# Lienzo maestro — FERIA Precision Codex (metas, tareas y criterios de éxito)

> Guía global orientada a ejecución. **Repo‑first** y operable en monorepo. Estructurada por **metas** (qué), **tareas** (cómo) y **criterios de éxito** (cómo demostrarlo). Horizonte 4–6 meses con entregables quincenales.

---

## 0) Visión, alcance y métricas globales

**Problema**

* Entender y operar repos grandes con IA (búsqueda semántica, Q&A con citas), ejecutar tareas seguras (sandbox) y mejorar precisión/fiabilidad con evaluación continua.

**Usuarios objetivo**

* Devs, SRE, Data/ML, equipos de soporte.

**Métricas North Star**

* [/query] **P95** ≤ 1.5 s; **P50** ≤ 400 ms.
* **Precision@Coverage** ≥ 92% a 70–80% cobertura.
* **ECE** < 7% (calibración de confianza).
* **Éxito agente** ≥ 95%; **violaciones de política** = 0.
* **Utilización GPU target** 80% (mem < 85%).
* **MTTR debug** −25–40% vs baseline.

**Principios**

* Local‑first, trazabilidad total, seguridad por defecto (no red en sandbox), reproducibilidad (snapshots firmados), rutas de modelos adaptativas (coste/latencia/precisión).

---

## 1) Pilares y metas por dominio

### 1.1 Control Plane & Gobernanza de GPU

**Meta**: orquestar tareas, cumplir SLOs y mantener GPU ≈80% sin saturación.

**Tareas**

* Orchestrator + Scheduler (APScheduler) con colas: fast, realtime, batch, eval, indexing.
* Admission Controller (token‑bucket/quotas) y Circuit Breaker por SLA.
* GPU Governor 2.0: NVML/DCGM, PID + feed‑forward por backlog; actuadores: concurrency, micro‑batch, max_new_tokens, desvío a CPU/pequeño, pausa batch/eval.
* Priority Queues + Dynamic Batcher + GPU Job Scheduler por GPU/MIG.

**Éxito**

* P95 en objetivo 24 h (carga sintética+real).
* Util GPU 75–85% sin OOM; throttles < 3% en fast.
* `feriactl` pausa/escala/rehidrata sin downtime sensible. Evidencias: panel Grafana, logs de throttle, informe `simulate`.

---

### 1.2 Model Plane: ruteo, lanes y seguridad

**Meta**: maximizar precisión/coste con rutas **draft → verify → expert**, A/B y ensamblados opcionales.

**Tareas**

* Router con heurística de **dificultad** (stack depth, traza, tipo de consulta).
* Lanes: speculative (mini/CPU), verify (med/GPU), expert (grande/GPU). Canary 10–20% con Judge (P95, nDCG, ECE, coste) para promoción/rollback.
* Guardrails: plantillas con citación obligatoria, anti‑inyección, PII/PHI scrubbing, validación JSON Schema.
* Self‑consistency n=3 en tareas críticas.

**Éxito**

* Coste medio ↓ ≥ 30% vs solo modelo grande con nDCG@5 ±2%.
* Rollback automático ante degradación. Evidencias: reportes A/B, curvas Prec@Cov, logs de router/safety.

---

### 1.3 Data Plane: RAG++, ingesta y freshness

**Meta**: recuperación precisa y compacta con grafo de símbolos y actualización incremental.

**Tareas**

* Pipeline de ingesta: parsers/AST, chunking 300±, dedup (minhash), Embedding Cache.
* FAISS por shards + Graph Hop (callers/callees) + Reranker CPU (MiniLM).
* Prompt Builder con citas estrictas y presupuesto de tokens.
* Freshness Watcher (git + debounce) y purge selectivo.

**Éxito**

* nDCG@5 ≥ target en 3 repos.
* Latencia RAG P95 ≤ 300 ms a 80k chunks.
* Reindex < 2 min tras merge. Evidencias: benchmarks, trazas de citas (path:línea), tiempos de reindex.

---

### 1.4 Agente & Sandbox

**Meta**: ejecutar tareas reproducibles, sin red y con evidencia verificable.

**Tareas**

* Sandbox no‑net, allowlist, timeouts, CPU/RAM caps, COW.
* Agente planificador + recetas permitidas (venv, pip, pytest, ruff, mypy, bandit).
* Artefactos: coverage, logs, diffs; firma y almacenamiento.

**Éxito**

* ≥ 95% éxito en 10 recetas estándar; 0 violaciones. Evidencias: reportes MD por `run_id`, artefactos y logs firmados.

---

### 1.5 Observabilidad y calidad

**Meta**: visibilidad total de M/L/T, alertas útiles y anomalías baratas.

**Tareas**

* Prometheus exporters (servicios, router, governor) + logs JSON (Loki) + trazas del mesh.
* Anomaly Detect (EWMA/Z‑score) en util, depth, error‑rate → alertas.
* Dashboards: GPU util/mem/temp, P50/95 por cola, admit/throttle, costo/request.

**Éxito**

* Alertas con precisión > 80%. Dos postmortems con línea de tiempo por `run_id`.

---

### 1.6 Evaluación, calibración, A/B y drift

**Meta**: evaluación continua por slices y decisiones guiadas por datos.

**Tareas**

* Eval Registry versionado; métricas nDCG@5, MRR, ECE, Prec@Cov, coste/latencia.
* Ablations: baseline → +rerank → +RAG → +self‑consistency → +calibración/abstención → +graph‑hop.
* A/B online canary 10–20% con Judge automático.
* Drift monitor: distribución de consultas, éxito@cobertura; acciones de reindex/recalibrar.

**Éxito**

* Mejora neta ≥ objetivo del eval preacordado. Nightly estable con reportes firmados.

---

### 1.7 Seguridad, compliance y auditoría

**Meta**: seguridad por defecto y evidencia de cumplimiento.

**Tareas**

* Policies YAML: sandbox, routing, quotas; RBAC; secretos vía KMS/HSM.
* SBOM CycloneDX; escáneres (bandit/trivy); logs firmados y retención.
* Model card/versioning; DLP para PII/PHI.

**Éxito**

* 0 hallazgos críticos; SBOM en CI; accesos revisados.

---

### 1.8 CI/CD, DR y resiliencia

**Meta**: entregas seguras, recuperables en < 10 min y resiliencia probada.

**Tareas**

* CI con lint/tests/bench; CD blue‑green + canary.
* Snapshots firmados (DB+FAISS+artifacts) y restore verificado.
* Chaos drills: latencia, caída, OOM; runbooks y game‑days.

**Éxito**

* Restore < 10 min; canary/rollback operativos. Evidencias: registro de drills, tiempos.

---

### 1.9 DX & CLI

**Meta**: operar con una mano y reducir fricción dev.

**Tareas**

* `feriactl`: status/health, scale/drain, queues, ingest, snapshot, eval, canary, simulate, kill‑switch.
* Plantillas de PR, issues, RFCs; convenciones de ramas y etiquetado.

**Éxito**

* Operaciones comunes < 3 comandos; onboarding dev < 1 día. Evidencias: manual CLI y vídeo corto.

---

## 2) Roadmap por fases (DoD)

**Fase 0 — Fundaciones (1–2)**

* Monorepo, CI base, `settings.toml`, `models.toml`, policies.
* FastAPI `/health` + RQ + FAISS vacío + exporters. **DoD**: build verde; panel latencias; `feriactl status` ok.

**Fase 1 — MVP Pro (3–8)**

* Ingesta + FAISS + reranker; Prompt Builder con citas.
* Router small/med/large; sandbox no‑net; primeros paneles.
* Eval inicial (nDCG/ECE/Prec@Cov) y snapshot. **DoD**: nDCG@5 target en 2 repos; P95 ≤ 1.8 s; éxito agente ≥ 90%.

**Fase 2 — Hardening (9–14)**

* Admission/quota; GPU governor; dynamic batching; A/B + Judge.
* Calibración + abstención; semantic cache; snapshots firmados. **DoD**: P95 ≤ 1.5 s estable; util 75–85%; ECE < 7%; Prec@Cov ≥ 92%.

**Fase 3 — Escala & Resiliencia (15–22)**

* Drift + freshness; HIL; chaos drills; restore < 10 min. **DoD**: 2 game‑days; MTTR −30%; DR probado.

**Fase 4 — Enterprise polish (23–26+)**

* Multitenant ligero; presupuesto tokens/€; gCO2e; CLI completo. **DoD**: presupuesto 30 d; onboarding < 1 d; auditoría limpia.

---

## 3) Tablero de métricas y umbrales

* **SLO /query**: P95 ≤ 1.5 s, error‑rate < 0.5%; **fast.depth** ≤ 50.
* **GPU**: util 80%±5, mem < 85%, temp bajo umbral.
* **Calidad**: nDCG@5 ≥ target; ECE < 7%; Prec@Cov ≥ 92% a 70–80% cobertura.
* **Agente**: éxito ≥ 95%, violaciones 0; artefactos 100% adjuntos.
* **Evaluación**: nightly OK; reportes versionados.

---

## 4) Checklists de verificación por pilar

**Control plane**

* [ ] Governor aplica acciones y registra decisiones.
* [ ] Circuit breaker retorna 429 con Retry‑After.
* [ ] Batcher mantiene P95 y no crea picos de VRAM.

**Model plane**

* [ ] Ruteo dinámico por dificultad, con logs y tasas de acierto.
* [ ] A/B con Judge y rollback automático.
* [ ] Guardrails activos y medidos.

**Data plane**

* [ ] Dedup/minhash funcionando; embedding cache con hit‑rate.
* [ ] Graph hop aporta +nDCG medible.
* [ ] Freshness reindexa < 2 min tras merge relevante.

**Agente**

* [ ] 10 recetas pasan en sandbox; tiempo y logs firmados.

**Obs/Calidad**

* [ ] Dashboards clave; 3 alertas útiles; 2 postmortems.

**Seg/Compliance**

* [ ] SBOM generado; 0 críticos; DLP probado.

**CI/CD/DR**

* [ ] Canary y rollback; restore < 10 min; chaos drills.

**DX/CLI**

* [ ] Operación diaria < 3 pasos; manual listo.

---

## 5) Evidencias mínimas por entrega

* Reporte MD con métricas y capturas de paneles.
* Artefactos: modelos/configs, calibradores, snapshots.
* Logs firmados con `run_id` correlable.
* Scripts reproducibles: `nightly_eval`, `simulate`, `snapshot/restore`.

---

## 6) Riesgos y mitigaciones (resumen)

* **VRAM**: KV paginada, democión a modelo pequeño.
* **Picos**: batcher + quotas + kill‑switch.
* **Drift**: monitor + refresco evalset e índices.
* **Seguridad**: deny por defecto en sandbox; secretos KMS/HSM.
* **Coste**: router coste‑aware + presupuesto tokens/€ por tenant.

---

## 7) Glosario operativo

* **Precision@Coverage**: precisión condicionada a responder según umbral de confianza.
* **ECE**: error de calibración esperado.
* **Runbook**: guía paso a paso para incidentes.

---

## Apéndice A — Mandos rápidos `feriactl`

```
feriactl status | health --verbose | queues list --stats
feriactl workers scale agent=2 indexing=4 eval=1
feriactl ingest <repo>
feriactl snapshot create | restore <id>
feriactl eval run --set vX | report show --last
feriactl canary start --model <id> --traffic 10
feriactl simulate --qps 30 --mix fast=80,batch=20 --dur 10m
feriactl kill-switch on | off
```

---

# 8) Desarrollo detallado por pilar (mega‑guía)

> Formato **Meta → Diseño → Implementación → Pruebas → Entregables**.

## 8.1 Control Plane y Gobernanza de GPU

**Diseño**

* Colas: `fast`, `realtime`, `batch`, `eval`, `indexing` con cuotas por tenant y rate‑limit.
* Admission Controller: token bucket por `tenant:cola:modelo` (`rate`, `burst`, `max_inflight`). `429` + `Retry‑After` en rechazo.
* Circuit Breaker: abre si `P95>SLA` durante `T` y `depth>threshold`; backoff exponencial.
* GPU Governor 2.0: PID + feed‑forward; actuadores: `concurrency`, `micro_batch`, `max_new_tokens`, desviación a CPU/pequeño, pausa `batch/eval`.
* Scheduler aware de GPU/MIG/NUMA. Hints del governor para reparto.

**Implementación**

* PID: `e=target−medida`; `Δconcurrency=Kp·e+Ki∫e+Kd·de/dt+Kf·backlog_norm`.
* `micro_batch = clamp(mb_min, mb_max, f(memory_headroom))`.
* Reducir `max_new_tokens` si `mem>85%` o `temp>Θ`.
* Backpressure: si `fast.depth>50` o `wait_p95>500ms`, reducir `admit_rate` y activar `Retry‑After`.
* Auto‑escalado por `depth` y `p95`; drain con graceful shutdown.

**Pruebas**

* `simulate --qps {10..60} --mix fast=80,batch=20 --dur 15m` y medir P95, throttles, util, mem, depth.
* Chaos: inyección de latencia/errores para CB.

**Entregables**

* `configs/policies/tenants.quotas.yaml` y `configs/features.flags.yaml`.
* Panel Grafana: GPU util/mem/temp, queue depth, admit/throttle, P50/95.

---

## 8.2 Model Plane: ruteo, lanes, A/B y seguridad

**Diseño**

* Scoring de dificultad `D` (RAG: `0.4*len_ctx + 0.4*k + 0.2*entropy`; Debug: `0.4*depth + 0.3*files + 0.3*len_trace`).
* Lanes: draft (CPU mini) → verify (GPU med) → expert (GPU large) con fallback y escalado por confianza.
* A/B 10–20% con Judge (P95, nDCG@5, ECE, coste).
* Guardrails: prompt hygiene, citación obligatoria, anti‑inyección, JSON Schema, PII/PHI scrubber.

**Implementación**

```toml
# models.toml
[defaults]
small="phi-3.5-mini"
medium="llama3.1:8b-instruct"
large="qwen2.5-coder:14b"

[routing]
KeyError="small"
ValueError="small"
TypeError="medium"
DeepStack="large"
```

* Router: `D<3 → small`, `3≤D<6 → medium`, `D≥6 → large`. Escalar si `confidence<τ`. Bifurcar si `A/B`.

**Pruebas**

* Suite de prompts sintéticos + reales; medir coste y nDCG.
* Canary 48 h; rollback si {P95↑, nDCG↓, ECE↑} cruzan umbrales.

**Entregables**

* Reporte A/B `docs/reports/ab_vX.md` y recomendación.

---

## 8.3 Data Plane: ingesta, RAG++, freshness

**Implementación (pseudocódigo)**

```python
for file in repo:
  doc = parse(file)
  chunks = chunk(doc, size=300, overlap=50)
  for c in chunks:
    if is_duplicate(c):
      continue
    emb = embed_cache.get_or_compute(hash(c))
    faiss.add(emb, metadata={"path": path(file), "line_span": span(c)})
```

**Pruebas**: nDCG@5 y MRR por repo; P95 RAG; reindex parcial < 2 min.

**Entregables**: Bench RAG, cobertura de citas, métricas exportadas.

---

## 8.4 Agente & Sandbox

**Recetas (YAML)**

```yaml
name: unit-tests
steps:
  - run: python -m venv .venv
  - run: .venv/bin/pip install -r requirements.txt
  - run: .venv/bin/pytest -q --maxfail=1 --disable-warnings --cov
artifacts:
  - path: .coverage
  - path: tests/pytest.log
policies: unit_tests
```

**Pruebas**: 10 recetas estándar; 0 violaciones; artefactos presentes.

---

## 8.5 Observabilidad

**Métricas, logs, trazas** y alertas EWMA/Z. Dashboards GPU, P50/95 por cola, admit/throttle, coste/request.

---

## 8.6 Evaluación y calibración

**ECE** con temperature scaling o isotonic; curvas Prec@Cov; nightly eval reproducible.

---

## 8.7 Seguridad y cumplimiento

RBAC; KMS/HSM; DLP PII/PHI; SBOM; escáneres; logs firmados; retención.

---

## 8.8 CI/CD, DR y resiliencia

Gates de calidad; blue‑green + canary; snapshots firmados; restore validado.

---

## 9) Plan por sprints (detalle sugerido)

S1 Fundaciones; S2 Ingesta/FAISS; S3 Reranker/Prompt Builder; S4 Router+guardrails; S5 Sandbox+agente; S6 Governor+batcher+CB; S7 A/B+Judge+calibración; S8 Freshness+drift+HIL; S9 DR+snapshots+chaos; S10 Multitenant+coste/carbón+DX.

---

## 10) Criterios de aceptación globales

Rendimiento, calidad, confiabilidad, operabilidad, resiliencia, auditoría según SLOs descritos.

---

## 11) Riesgos detallados y mitigación

VRAM, picos, drift, inyección, PII, dependencia de modelos, coste variable, corrupción de índice, restore fallido. Mitigaciones alineadas (KV paginada, quotas+CB, drift monitor, DLP, canary, snapshots firmados).

---

## 12) Apéndices (plantillas)

### 12.1 `sandbox.policy.yaml`

```yaml
network: disabled
cpu_quota: "1.0"
memory_limit: "2GiB"
timeout_sec: 90
workdir_mode: copy-on-write
allowlist: ["python","pip","pytest","coverage","ruff","mypy","bandit","ls","cat"]
denylist:   ["rm","curl","wget"]
```

### 12.2 `routing.policy.toml`

```toml
[defaults]
small="phi-3.5-mini"
medium="llama3.1:8b-instruct"
large="qwen2.5-coder:14b"

[rules]
low_diff = "small"
mid_diff = "medium"
high_diff = "large"
```

### 12.3 `features.flags.yaml`

```yaml
use_speculative: true
use_self_consistency: false
use_semantic_cache: true
kill_switch_enabled: true
```

### 12.4 `tenants.quotas.yaml`

```yaml
- tenant: default
  fast:   { rate: 30, burst: 60, max_inflight: 50 }
  batch:  { rate: 10, burst: 20, max_inflight: 200 }
  eval:   { rate: 2,  burst: 4,  max_inflight: 20 }
```

### 12.5 Prompt templates (resumen)

* RAG QA: cita por archivo/línea; formato fijo; abstención si baja confianza.
* Debug: resume traza, causa y plan reproducible; comandos limitados a allowlist.

### 12.6 Métricas Prometheus (mínimas)

`router_requests_total{route,model}`, `router_latency_seconds_bucket{route}`, `gpu_utilization{gpu}`, `gpu_memory_bytes{gpu}`, `gpu_temperature_celsius{gpu}`, `queue_depth{queue}`, `admit_total{queue}`, `throttle_total{queue}`, `rag_ndcg5`, `rag_latency_seconds`, `eval_ece`, `prec_at_cov`.

### 12.7 Reglas de alerta sugeridas

* `P95_query > 1.5s for 5m` → WARN; `>2.5s for 5m` → CRIT.
* `gpu_util > 0.9 for 5m` o `gpu_mem > 0.85 for 2m` → CRIT + kill‑switch.
* `fast_queue_depth > 50 for 2m` → WARN; `>100 for 2m` → CRIT.

---

## 13) Playbooks operativos (runbooks)

### 13.1 Pico de latencia /query (P95 > SLA)

**Diagnóstico**: `feriactl health --verbose`; panel GPU/util/mem/depth/admit/throttle; `queues list --stats`.

**Acciones**: subir `micro_batch` hasta headroom; si mem>80% bajar `max_new_tokens` 20%; aumentar `gpu-worker` si hay GPU ociosa; activar `use_semantic_cache`; reducir `top_k` 20→12; cortar `batch/eval` con CB.

**Verificación**: P95 normaliza en 5–10 min; throttles<3%.

### 13.2 OOM o VRAM > 85%

Democión a modelo small en fast; reducir `max_new_tokens` y `micro_batch`; purgar KV‑GPU fría; mover KV→CPU; pausar eval. Prevención: límite de tokens y cálculo de batch por memoria.

### 13.3 Drift de datos

Reindex incremental; refrescar evalset; recalibrar ECE.

### 13.4 Violaciones de sandbox

Bloqueo + reporte; revisar receta; ampliar allowlist si legítimo.

### 13.5 Degradación por canary

`feriactl canary rollback`; incidencia + reportes.

---

## 14) APIs (contratos)

**Gateway `/v1`**

* `GET /v1/health` → `{ status, uptime, version }`
* `POST /v1/query` → `{query, top_k?, tenant?}` ⇒ `{answer, citations:[{path,line_start,line_end}], confidence}`
* `POST /v1/ingest` → `{repo_url|path, branch?, include?, exclude?}` ⇒ `{job_id}`
* `POST /v1/agent/run` → `{task, recipe, inputs, tenant?}` ⇒ `{run_id,status}`
* `GET /v1/eval/report?id=...` → `{metrics, artifacts}`

**Control plane**

* `POST /v1/admin/scale` → `{workers:{agent:2,indexing:4,eval:1}}`
* `POST /v1/admin/kill-switch` → `{enabled:true|false}`
* `GET  /v1/admin/queues` → stats por cola
* `POST /v1/admin/snapshot` → `{label}` ⇒ `{snapshot_id}`

---

## 15) Event Bus (esquemas)

`debug.new`, `eval.done`, `gpu.hot`, `index.updated`, `canary.alert` con campos estandarizados (`run_id`, `tenant`, métricas, `ts`).

---

## 16) Datos y modelos (esquemas)

**Chunks** `{id, repo, path, lang, symbol?, hash, text, start_line, end_line, created_at}`.
**Embeddings** `{chunk_id, model, dim, vec, created_at}`.
**Edges** `{from_symbol, to_symbol, type, file, lines}`.
**Citations** `{answer_id, chunk_id, path, lines, score}`.
**Runs** `{run_id, route, model, tokens_in/out, cost_est, latency_ms, success, created_at}`.

---

## 17) Algoritmos clave

**Dynamic batching**

```python
B = []
T_deadline = now + SLA_batcher  # ej., 40 ms
while now < T_deadline and headroom_ok():
  req = queue.peek()
  if tokens(B)+tokens(req) <= max_tokens_by_headroom():
     B.append(queue.pop())
  else:
     break
serve(B)
```

**KV‑cache paginada**

```python
if kv_gpu_usage() > high_watermark:
    evict = lru_tail_until(low_watermark)
    move_to_cpu(evict)
```

**Scoring de dificultad**

```python
score = 0.4*depth + 0.4*unique_files + 0.2*(trace_len/500)
route = 'small' if score<3 else 'medium' if score<6 else 'large'
```

---

## 18) Seguridad y privacidad

Amenazas: inyección de prompt, exfiltración por herramientas, PII/PHI, abuso de sandbox.
Controles: DLP, validación JSON, no‑net, allowlist, logging firmado, RBAC.
Pruebas: corpus de inyecciones, pentest, auditoría trimestral.

---

## 19) Métricas (catálogo)

Router: `router_requests_total`, `router_confidence_bucket`. GPU: `gpu_utilization`, `gpu_memory_bytes`, `gpu_temperature_celsius`. Colas: `queue_depth`, `admit_total`, `throttle_total`. RAG: `rag_ndcg5`, `rag_mrr`, `rag_latency_seconds`. Eval: `eval_ece`, `precision_at_coverage`. Coste: `cost_tokens_total{tenant}`, `cost_eur_estimate{tenant}`.

---

## 20) Dashboards (Grafana)

**Overview**: /query P50/95, error, depth, throttles.
**GPU**: util/mem/temp, KV hits, batch size efectivo.
**Calidad**: nDCG@5, MRR, ECE, Prec@Cov vs cobertura.
**Coste/Carbono**: tokens/s, €/req, gCO2e estimado.

---

## 21) Calidad: evaluación y calibración

ECE con reliability diagram; Prec@Cov por barrido de umbral; ablations con tabla coste/latencia.

---

## 22) CI/CD: calidad antes de prod

Pre‑commit (ruff/black/mypy/bandit), tests unit/int/e2e, bench sintético. Blue‑green; canary 10–20%; Judge obligatorio; rollback automático. Gates: falla si P95↑>20% o nDCG↓>3% o ECE↑>2%.

---

## 23) Disaster Recovery y snapshots

Snapshot diario y por release; retención 30 d; firma y hash. Restore < 10 min con verificación de integridad. Runbook `snapshot restore <id>`.

---

## 24) Costes y carbono

`€ ≈ (tokens_in+tokens_out)*precio + infra/h`. `gCO2e ≈ kWh × factor_red`. Presupuesto por tenant; kill‑switch de coste.

---

## 25) SDK de plugins (extensiones)

Contrato `tool.json` (`name`, `inputs schema`, `outputs schema`, `allowed_commands`). Seguridad: validación de schema; límites CPU/mem/tiempo; sin red.

---

## 26) Sizing (guía)

* 80k chunks → FAISS IVF CPU P95 < 120 ms.
* 1×GPU 24 GB → modelo mediano 2 workers con KV paginada; fast 25–40 req/s con speculative.
* MIG 10/24 + 8/24 → verify en 10/24, expert en 8/24; reranker/FAISS a CPU.

---

## 27) Onboarding dev y DX

`make bootstrap`; `docker compose up -f compose.dev.yml`; `feriactl ingest <repo>`; `nightly_eval` local.

---

## 28) Formato de logs

```json
{
  "ts":"2025-10-16T13:22:05Z",
  "svc":"router",
  "run_id":"r-abc123",
  "tenant":"default",
  "route":"verify",
  "model":"llama3.1-8b",
  "qlen":12,
  "admit":true,
  "throttle":false,
  "lat_ms":812,
  "confidence":0.78
}
```

---

## 29) OKRs trimestrales sugeridos

KR1 P95 ≤ 1.4 s con 100k chunks; KR2 coste/request −25% con nDCG±1%; KR3 MTTR −35%; KR4 0 incidentes de sandbox.

---

## 30) Demos “ready”

**A** RAG++ con citas y panel de latencias. **B** Router adaptativo + A/B con rollback live. **C** Agente debug corrigiendo fallo en sandbox con evidencia. **D** DR restore < 10 min cronometrado.

---

## 31) Definition of Awesome

Explicabilidad por consulta (“por qué esta cita/este modelo”); botón “reproducir respuesta” desde logs; presupuesto dinámico de tokens por tenant.

---

## 32) Catálogo de servicios y módulos

Servicios: `api-gateway`, `orchestrator`, `model-gateway`, `gpu-worker`, `cpu-worker`, `ingestor`, `retrieval`, `debug-agent`, `sandbox-runner`, `observability`, `eval-service`, `snapshotter`, `event-bus`.

Paquetes: `core/`, `agent/`, `policy/`, `eval/`, `observabilidad/`.

---

## 33) Estructura de monorepo

```
precision-codex/
  apps/
    feriactl/
  services/
    api-gateway/
    orchestrator/
    model-gateway/
    gpu-worker/
    cpu-worker/
    ingestor/
    retrieval/
    debug-agent/
    sandbox-runner/
    eval-service/
    snapshotter/
    observability/
  packages/
    core/
    agent/
    policy/
    eval/
    observability/
  configs/
    settings.toml
    models.toml
    policies/
      sandbox.policy.yaml
      routing.policy.toml
      tenants.quotas.yaml
      features.flags.yaml
  infra/
    docker/
    k8s/
  storage/
    db/
    vector/
    artifacts/
    logs/
  docs/
    runbooks/
    reports/
    rfcs/
```

---

## 34) Infra: compose y perfiles

Perfiles: `dev` (hot‑reload), `prod` (límites, logging estructurado, healthchecks), `eval` (GPU mínima, menos prioridad).

```yaml
services:
  api-gateway:
    image: api:latest
    deploy:
      resources:
        limits: { cpus: '1.0', memory: 512M }
  gpu-worker:
    image: worker-gpu:latest
    deploy:
      resources:
        reservations:
          devices: [{ capabilities: [gpu] }]
```

---

## 35) Makefile

```
make bootstrap
make dev-up
make ingest REPO=... BRANCH=...
make eval-nightly
make snapshot
make restore ID=...
make simulate QPS=30 MIX="fast=80,batch=20" DUR=10m
```

---

## 36) CI (Actions)

Jobs: `lint`, `test`, `bench`, `build`, `sbom`, `scan`. Gates: P95↑>20% o nDCG↓>3% o ECE↑>2% falla. Artefactos: reportes MD/CSV, SBOM CycloneDX.

---

## 37) Matrices de pruebas

Unitarias: chunkers, minhash, prompt builder, router. Integración: RAG e2e, lanes, sandbox recetas. E2E: `/query` y `/agent/run` con asserts de citas. No funcionales: carga, resiliencia, DR, seguridad.

---

## 38) Bench methodology

Dataset estratificado; escenarios frío/templado/caliente; KPIs P50/95, coste/request, nDCG@5, ECE, Prec@Cov.

---

## 39) GPU Governor: tuning

Parámetros `Kp, Ki, Kd`; `headroom_mem∈[0.12–0.2]`; `util_target=0.8`. Procedimiento: ajustar `Kd` para evitar oscilación; `Ki` para sesgo; `Kf` para backlog.

---

## 40) Headroom de memoria

```
headroom = 1 - max(vram_used/vram_total, kv_gpu_usage)
max_tokens_by_headroom = floor(headroom * H * factor_model)
```

---

## 41) Partición MIG (recetario)

`10/24` verify; `8/24` expert; fast aislado; batch/eval en colas separadas.

---

## 42) Router coste‑aware

`score_total = λ1*lat + λ2*cost + λ3*(1-precision_proxy)`; democión si coste/tenant > presupuesto horario.

---

## 43) Biblioteca de prompts (convenciones)

Bloques: `role`, `context`, `task`, `cites`, `constraints`, `format`. Marcadores `{{ctx}} {{question}}`. Prohibido inventar.

---

## 44) Chunking por lenguaje

Python/TS/Java por símbolo (tree‑sitter), fallback por tamaño. Markdown por encabezados + longitud. `size=300`, `overlap=40–60`.

---

## 45) Grafo (tree‑sitter)

Nodos: funciones, clases, módulos. Aristas: `calls`, `imports`, `inherits`. Index `{from,to,type,file,lines}`.

---

## 46) Cache semántica: clave/invalidación

Clave: `hash(query_norm+ctx_fingerprint+flags)`; invalidar si cambia fingerprint de contexto o flags críticos.

---

## 47) Verificación de citas

Chequear entailment de snippet citado vs afirmación; marcar inconsistencia.

---

## 48) Políticas de sandbox (paquetes)

`unit_tests`, `linting`, `build`, `docs` con allowlist específicos.

---

## 49) Eventos extendidos

`audit.access`, `budget.breach`, `drill.result` con payloads mínimos y `ts`.

---

## 50) Retención y privacidad

Logs 30–90 d; artefactos 180 d; snapshots 30 d rolling + LTS por release. PII/PHI enmascarado, cifrado, acceso auditado.

---

## 51) RBAC

Roles: `admin`, `analyst`, `user` con permisos definidos.

---

## 52) Gestión de secretos

KMS/HSM; rotación 90 d; doble control para claves maestras.

---

## 53) DR (RTO/RPO)

RTO < 10 min; RPO ≤ 24 h; ejercicio mensual de conmutación.

---

## 54) Estrategias de despliegue

Blue/green; canary 10–20% con Judge; feature flags por archivo.

---

## 55) Quality Gates (CI/CD)

Bloquear merge si SLOs empeoran; SBOM y escaneos limpios obligatorios.

---

## 56) SLOs y presupuestos de error

Mes con 1% de tiempo fuera de SLO; alertas burn‑rate 2%/1h y 5%/6h.

---

## 57) A/B Judge: fórmula

```
win = (ΔnDCG>=-0.01) && (ΔP95<=+0.2s) && (ΔECE<=+0.02) && (ΔCost<=+10%)
```

---

## 58) Cobertura (definiciones)

Coverage = fracción de queries con respuesta; Precision@Coverage = precisión condicionada; variar umbral.

---

## 59) PromQL (ejemplos)

```
query_p95 = histogram_quantile(0.95, sum(rate(router_latency_seconds_bucket[5m])) by (le))
queue_depth = sum(queue_depth) by (queue)
gpu_hot = avg_over_time(gpu_utilization[5m]) > 0.9
```

---

## 60) Chaos scenarios

Model-gateway restart storm; FAISS ×5 latencia; GPU OOM; CB mal configurado; pérdida temporal de disco de snapshots.

---

## 61) Runbook: FAISS corrupto

1. `snapshot restore <id>` 2. Verifica integridad 3. Reconstituir graph-hop y recalcular fingerprints 4. Aislar queries a cache mientras se reindexa.

---

## 62) Runbook: pico de costes

Panel coste/token por tenant → modo coste-aware (demote) → freeze eval/batch → alertar owners.

---

## 63) Readiness de soporte

Manual, FAQ, paneles, playbooks, guardias.

---

## 64) Portabilidad y vendor-neutral

Abstracciones para servir modelos (local/externo) y vector stores intercambiables.

---

## 65) Lecturas recomendadas

RAG (Lewis et al.), Calibración (Guo et al.), Serving LLMs eficientemente (paged KV).

---

## 66) Rate-limit y fairness

Token-bucket ponderado por tenant; leaky-bucket para suavizado.

---

## 67) Quotas por tenant

Tabla `{tenant, cola, rate, burst, max_inflight, budget_tokens_h}` y políticas de degradación.

---

## 68) Grooming y priorización

WSJF para backlog; etiquetas `P0/P1/P2`.

---

## 69) Reglas de revisión y CODEOWNERS

2 aprobaciones para `services/`; 1 para `packages/`.

---

## 70) Versionado

SemVer para servicios; `eval_vX` para suites; versionado de prompts.

---

## 71) Incidentes (IR)

Severidades S1–S3; responsables; comunicación y RCA en 48 h.

---

## 72) Ética y limitaciones

No sustituir juicio humano; abstención antes que invención; privacidad primero.

---

## 73) Reporte de entrega (plantilla)

Resumen ejecutivo, hitos, métricas, costes, riesgos, próximos pasos.

---

## 74) OKR semanal (plantilla)

Objetivos, logros, métricas, bloqueos, plan siguiente.

---

## 75) Cierre de sprint (retro)

Qué salió bien, qué no, acciones, responsables, due dates.

---

## 76) Teoría de colas & dimensionamiento

Modelo M/M/c para `fast`; `ρ=λ/(c·μ)<0.8`; Erlang-C para `W_q`; ajustar `c` hasta `W_q≤200ms` y `P95_total≤1.5s`.

---

## 77) Governor 2.0 robusto

PID con anti-windup y derivada filtrada; feed-forward por backlog; saturación de `u` mapeado a concurrencia; supervisión térmica.

---

## 78) WFQ simplificado (fairness entre colas)

Pesos `w_fast=5, w_realtime=4, w_batch=1, w_eval=1`; strict priority a `fast` si `depth_fast>50`.

---

## 79) Forecast de cola

EWMA (`α=0.3`) y Holt-Winters; precalentar modelos; subir `c` con 30–60 s de antelación.

---

## 80) Política de abstención

Seleccionar `τ` por slice para maximizar Prec@Cov a 70–80% de cobertura.

---

## 81) Rerankers (catálogo)

`MiniLM-L6` vs `bge-reranker-base`; política CPU salvo P95 permita; `k'` 5–8.

---

## 82) Embeddings (elección y costes)

Memoria ≈ `N·d·4 bytes`; N=80k, d=768 → ~235 MB; evaluar d=384 si memoria ajustada.

---

## 83) FAISS (índices y parámetros)

IVF con `nlist∈{256,512,1024}` y `nprobe∈{4,8,16}`; HNSW si queries dinámicas; PQ para memoria.

---

## 84) Prompt Builder & presupuesto

Reservar 40% respuesta; ordenar citas por score y diversidad; eliminar redundancias (Jaccard > 0.8).

---

## 85) Cache semántica (expulsión)

LRU con TTL_fast 15–30 min, TTL_batch 4–8 h; guardar solo si `confidence≥τ_slice`.

---

## 86) Multitenancy (fair-share)

Degradar a modelo pequeño si excede presupuesto en ventana deslizante.

---

## 87) Telemetría y muestreo

Muestreo adaptativo de trazas cuando QPS alto; jamás muestreos en `error`.

---

## 88) News: roles & RACI

RACI por área (Owner, Approver, Consulted, Informed) para despliegues, DR, eval, seguridad.

---

## 89) Taxonomía de errores

Códigos y causas: `E-RAG-NOCITE`, `E-KV-OOM`, `E-GPU-HOT`, `E-CB-OPEN`, acciones sugeridas por código.

---

## 90) Esquema de telemetría unificado

`ts, svc, run_id, tenant, route, model, qlen, admit, throttle, lat_ms, confidence, cost_est, gpu{util,mem,temp}`.

---

## 91) Intents classifier & fallback

Clasificador ligero (CPU) para intents; fallback a ruta segura si incertidumbre alta.

---

## 92) PII masking en logs

Hash/scrub de PII; campos sensibles con `redact:true`.

---

## 93) Testing de seguridad

Fuzzing de entradas; pruebas de prompt-injection; sandbox egress tests.

---

## 94) Entailment offline (CPU)

Verificador ligero para citas, pre-computa contradicción/soporte.

---

## 95) Datos sintéticos para eval

Generación controlada por plantillas; etiquetado semiautomático; revisión humana por muestras.

---

## 96) Confianza → UX

Mapeo de `confidence` → mensajes: responder/abstenerse/pedir más contexto; badges de citas.

---

## 97) Migración de índices

Scripts de dump/restore; compatibilidad de versiones; verificación post-migración.

---

## 98) Compatibilidad CUDA/Drivers

Matriz soportada; pruebas de humo por combinación; fallback a CPU si incompatibilidad.

---

## 99) Parámetros por modelo/hardware

Tabla de `max_batch_tokens`, `mb_min/max`, `max_new_tokens`, `kv_gpu_hwm` por modelo.

---

## 100) Guardrails de salida

Longitud, estilo, formato JSON; denegar si violación.

---

## 101) Plantilla de runbook (genérico)

Síntomas → Diagnóstico → Acciones → Verificación → RCA → Prevención.

---

## 102) Checklist de demo externa

Datos no sensibles; citas válidas; kill-switch listo; plan B sin GPU.

---

## 103) Apéndice legal (OSS)

Lista de licencias, obligaciones de atribución y políticas de uso.

---

## 104) Personas & casos de uso

Dev, SRE, Soporte, Data/ML: historias de usuario y criterios de aceptación por rol.

---

## 105) CLI: contratos y ejemplos

`feriactl queues list --json` salida estructurada; `feriactl eval run --set vX --json`.

---

## 106) SDKs (TS/Python)

Funciones `query()`, `ingest()`, `agentRun()` con ejemplos; manejo de `Retry-After`.

---

## 107) Admin UI (wireframes)

Secciones: SLOs, Colas, GPU, Coste, Eventos; acciones rápidas (pause batch, start canary, snapshot).

---

## 108) Accesibilidad e i18n

Textos localizables; contraste AA; atajos teclado; RTL soportado.

---

## 109) Data residency

Marcar datasets por región; políticas de ruteo y snapshots por residencia.

---

## 110) Modo air-gapped

Sin llamadas externas; imágenes locales; documentación offline.

---

## 111) SSO/OIDC

Scopes por rol; mapeo de grupos → RBAC; expiración de sesiones.

---

## 112) Tagging & lineage

Etiquetas por dataset/índice/modelo; eventos tipo OpenLineage.

---

## 113) Curvas QPS→P95 (plantilla)

Cómo producirlas con `simulate` y exportar a CSV/PNG.

---

## 114) DR multi-región

Anycast/GeoLB; failover A↔B; objetivos de `restore<10min` y `healthchecks` activos.

---

## 115) Presupuestos por tenant (YAML)

```yaml
- tenant: acme
  budget:
    tokens_hour: 5_000_000
    eur_month: 2000
  policy:
    on_overage: demote_small | throttle | deny
```

---

## 116) Rotación de claves (playbook)

Generar nuevas; doble escritura; rotar clientes; revocar viejas; verificar acceso.

---

## 117) Versionado de prompts

`prompts/` con SemVer; diffs y changelog; pruebas A/B ligadas a versión.

---

## 118) Librería de prompts (5 base)

RAG-QA, Debug, Design-Doc, Code-Fix, Explainer con bloques y ejemplos de parámetros.

---

## 119) Código de errores (tabla)

`E-RAG-NOCITE`, `E-RAG-MISS`, `E-KV-OOM`, `E-GPU-HOT`, `E-CB-OPEN`, `E-QUOTA-REJ`.

---

## 120) Esquema de telemetría (JSON Schema)

Campos obligatorios y tipos; validación en ingestión de logs.

---

## 121) Sampling & masking

Reglas de muestreo adaptativo; mascar PII por patrón/regex y DLP.

---

## 122) Seguridad: fuzz/LLM-attacks

Corpus de prompts maliciosos; asserts de no-exfiltración; CI gate.

---

## 123) Verificador de citas CPU

Modelo ligero de entailment; batch en background con prioridad baja.

---

## 124) Datos sintéticos: políticas

Separación clara; marcado en eval; nunca mezclar con productivos.

---

## 125) UX de confianza

Umbral visual; razón de abstención; CTA para aportar más contexto.

---

## 126) Migración de índices: scripts

`faiss-export`, `faiss-import`, validación de cardinalidad y recall.

---

## 127) Compatibilidad de drivers

Tabla CUDA/NVIDIA y versiones probadas; ruta de rollback.

---

## 128) Parámetros por modelo

Defaults por modelo/cola: `max_new_tokens`, `top_k`, `temperature`, `mb_max`.

---

## 129) Guardrails de salida

Schemas por tipo de respuesta; validación y truncado seguro.

---

## 130) RACI del proyecto (tabla)

Owner/Approver/Consulted/Informed por stream (Data, Serving, Eval, SRE, Security).

---

## 131) Checklist pre-release

SLOs verdes, eval A/B, SBOM limpio, DR validado, runbooks al día.

---

## 132) Licencias OSS

Listado y obligaciones; fichero NOTICE generado en CI.

---

## 133) Personas: historias de usuario (ejemplos)

Dev: “como dev quiero responder dudas de código con citas en <2 s para…” Criterios: nDCG@5≥X, citas válidas.

---

## 134) CLI ejemplos de salida

`feriactl queues list --json` y `jq` para inspección rápida; códigos de salida estandarizados.

---

## 135) SDKs: ejemplos

TS y Python con manejo de `Retry-After`, timeouts y reintentos full-jitter.

---

## 136) Admin UI: flujos

Pausar batch, lanzar canary, snapshot/restore, ver Judge, ver panel de costes.

---

## 137) i18n

Archivos `.po`/`.json` para textos; locales `es`, `en`.

---

## 138) Residency

Mapeo dataset→región; ruteo con política de residencia; snapshots por región.

---

## 139) Air-gapped

Registros locales; mirror de contenedores; documentación offline.

---

## 140) SSO/OIDC

Scopes: `query`, `admin`, `eval`; expiración y refresh tokens.

---

## 141) Lineage

Eventos `run→job→dataset` estilo OpenLineage; correlación con `run_id`.

---

## 142) QPS→P95 curvas

Procedimiento y scripts; umbrales de saturación y recomendaciones de `c`.

---

## 143) DR multi-región: pruebas

Failover controlado con tráfico sintético; verificación de SLOs post-switch.

---

## 144) Budgets por tenant (política)

Demote, throttle o deny con ventanas móviles; alertas proactivas.

---

## 145) Rotación de claves

Plan de 5 pasos y checklist; verificación de clientes y revocación.

---

## 146) Versionado de prompts: changelog

`CHANGELOG.md` por prompt; vincular a métricas de eval.

---

## 147) Prompts base detallados

Incluye variables, formato y ejemplos de salida.

---

## 148) Error codes (detallado)

Mapa código→HTTP→acción del cliente.

---

## 149) Telemetría: schema

JSON Schema validable; contrato estable para pipelines.

---

## 150) Masking DLP

Campos, patrones, ejemplos de redacción y pruebas unitarias.

---

## 151) Seguridad: fuzz CI

Job `fuzz` obligatorio en CI para rutas clave.

---

## 152) Entailment: backlog

Procesado batch en ventanas de baja carga; marcar inconsistencias para revisión.

---

## 153) Sintéticos: orquestación

Generación separada; etiquetado; reporte de cobertura de casos.

---

## 154) UX confianza

Componentes UI de confianza y motivos de abstención.

---

## 155) Scripts de migración

CLI para `faiss→faiss`, control de versiones y checksum.

---

## 156) CUDA matrix

Tabla probada y política de actualización.

---

## 157) Param presets por hardware

Preset por `A100 40G`, `L40S 48G`, `3090 24G`.

---

## 158) Salida segura (JSON)

Validador estricto; truncado por límites; logs si invalidación.

---

## 159) RACI (detalle)

Anexo con responsabilidades por hito.

---

## 160) Cierre

Checklist final de adopción: SLOs 30 d, nightly verde 14 d, DR ×2, seguridad sin críticos, manual + vídeo 5 min.

---

> **Nota repo-first**: todo lo anterior es plug-and-play en monorepo. Ajusta rutas bajo `configs/`, servicios en `services/`, y usa `feriactl` como interfaz única de operación. Los bloques de YAML/TOML/JSON son copypasteables sin dependencias externas.
