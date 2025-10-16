# FERIA Precision Codex — Monorepo Scaffold

Este repositorio contiene la estructura inicial y los artefactos mínimos para poner en marcha **FERIA Precision Codex**, el copiloto de desarrollo con RAG, agente seguro y laboratorio de precisión descrito en el *Lienzo maestro*.

La guía se organiza en tres bloques prácticos:

1. **Preparar el entorno**: configuración del workspace Python, dependencias comunes y herramientas de calidad.
2. **Desplegar la plataforma**: servicios, paquetes y scripts que conforman el plano de datos, modelo, control y observabilidad.
3. **Operar y evaluar**: cómo ejecutar `feriactl`, lanzar ingestas, correr el laboratorio de precisión y validar SLOs.

Cada bloque hace referencia a los runbooks, políticas y scripts almacenados en este monorepo. Las rutas coinciden con la estructura recomendada en el documento del plan de ejecución.

## 1. Preparar el entorno

1. Clona el repositorio y copia `.env.sample` a `.env`, ajustando credenciales locales.
2. Instala las dependencias de tooling ejecutando `make bootstrap` (usa `uv` como backend ligero por defecto).
3. Habilita `pre-commit` con `pre-commit install` para garantizar formato y seguridad antes de cada commit.
4. Levanta el entorno de desarrollo con `docker compose up --profile dev` cuando necesites servicios auxiliares (FAISS, Postgres, MinIO opcional).

Documentación complementaria:

- `docs/rfcs/` almacena decisiones de arquitectura (ADRs).
- `docs/runbooks/` ofrece guías operativas para incidentes comunes.
- `docs/api/openapi.yaml` expone el contrato inicial de la API.

## 2. Desplegar la plataforma

La plataforma se divide en **servicios** (FastAPI, orquestador, gateways, workers) y **paquetes reutilizables** (core, agent, eval, observabilidad, SDK). Cada componente incluye un `pyproject.toml`, directorio `src/` y carpeta `tests/`.

1. Construye imágenes base mediante `make build-images` (ver `infra/docker/`).
2. Despliega en Kubernetes aplicando los manifiestos base y overlays (`infra/k8s/base` y `infra/k8s/overlays/`).
3. Configura dashboards y alertas cargando los JSON de Grafana (`infra/grafana/dashboards/`).
4. Publica políticas y cuotas copiando los archivos de `configs/policies/` al `configmap` correspondiente.

Referencias rápidas:

- `services/api-gateway/` implementa los endpoints `/v1/*`.
- `services/orchestrator/` controla colas, gobernanza de GPU y admission control.
- `services/model-gateway/` resuelve enrutamiento entre modelos, canaries y guardrails.
- `services/retrieval/` y `packages/core/` contienen la lógica de RAG.
- `services/sandbox-runner/` ejecuta recetas en entornos aislados.

## 3. Operar y evaluar

La CLI `feriactl` actúa como panel de control local-first.

1. **Estado**: `feriactl status` y `feriactl health --verbose` inspeccionan servicios y SLOs.
2. **Ingesta**: `feriactl ingest <repo>` lanza pipelines de indexado semántico.
3. **Evaluación**: `feriactl eval run --set vX` ejecuta el laboratorio nocturno y genera reportes en `docs/reports/`.
4. **Snapshots**: `feriactl snapshot create` produce artefactos firmados listos para restauración (`storage/snapshots/`).
5. **Depuración**: `feriactl debug report` o `python scripts/debug_suite.py --json` generan instantáneas con flags de entorno,
   nivel de logging efectivo y estado general del entorno de ejecución.

### Métricas clave

- `rag_ndcg5`, `rag_latency_seconds` (Prometheus).
- `precision_at_coverage`, `eval_ece` (Eval service).
- `gpu_utilization`, `gpu_memory_bytes` (governor + exporters).

### Runbooks destacados

| Runbook | Propósito |
| --- | --- |
| `docs/runbooks/latency-p95.md` | Reducir picos de latencia `/query` |
| `docs/runbooks/gpu-oom.md` | Responder a OOM/VRAM > 85% |
| `docs/runbooks/drift.md` | Gestionar drift de consultas y datos |
| `docs/runbooks/restore-dr.md` | Restaurar la plataforma desde snapshots |

## 4. Próximos pasos

- Completar la implementación funcional de cada servicio siguiendo las plantillas dentro de `src/`.
- Añadir suites de pruebas unitarias e integraciones completas en los directorios `tests/`.
- Automatizar despliegues con los workflows de GitHub Actions definidos en `.github/workflows/`.
- Documentar cambios relevantes en `docs/reports/` y mantener actualizado el changelog de prompts y modelos.

Para más contexto estratégico, revisa el documento “Lienzo maestro — FERIA Precision Codex” que inspiró este scaffolding y coordina cada sprint con los criterios de aceptación definidos allí.
