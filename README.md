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
- `docs/Lienzo_maestro.md` conserva el lienzo maestro con las instrucciones completas del programa (**no borrar**).

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

1. **Estado**: `feriactl status` y `feriactl health --verbose` inspeccionan servicios y SLOs (se apoyan en `/v1/health`).
2. **Ingesta**: `feriactl ingest <repo>` lanza pipelines de indexado semántico llamando a `/v1/ingest` con los ficheros relevantes.
3. **Evaluación**: `feriactl eval run --set vX` ejecuta el laboratorio nocturno y genera reportes en `docs/reports/`.
4. **Snapshots**: `feriactl snapshot create` produce artefactos firmados listos para restauración (`storage/snapshots/`).
5. **Depuración**: `feriactl debug report` publica la instantánea en `/v1/debug` junto con artefactos; `python scripts/debug_suite.py --json` sigue disponible para auditoría local.
6. **Simulación de carga**: `python scripts/simulate_load.py --with-governor --target-util 0.8` emula ráfagas por cola, aplica el `GpuGovernor` PID y reporta la escala de concurrencia, micro-batches y límites de tokens recomendados.

### Ejemplo reproducible end-to-end

1. Arranca el API gateway en local: `python -m api_gateway.main` desde `services/api-gateway`.
2. Desde la raíz del repo ejecuta `feriactl ingest .` para indexar archivos de texto/Markdown del propio proyecto.
3. Lanza `curl -s http://localhost:8000/v1/query -X POST -H "content-type: application/json" -d '{"query": "Qué es FERIA"}' | jq` para ver la respuesta con citas.
4. Genera un reporte de depuración: `feriactl debug report --json` y revisa la carpeta indicada en la respuesta.

### Métricas clave

- `rag_ndcg5`, `rag_latency_seconds` (Prometheus).
- `precision_at_coverage`, `eval_ece` (Eval service).
- `gpu_utilization`, `gpu_memory_bytes` y decisiones de `GpuGovernor` (exporters + simulador).

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

## 5. Bitácoras y depuración reproducible

La plataforma incorpora utilidades para capturar el estado completo del entorno y facilitar auditorías posteriores:

1. Ejecuta `python scripts/debug_suite.py --json --full --output docs/reports/debug_sessions.jsonl --append` para generar un snapshot estructurado que incluye variables de entorno relevantes, configuración activa de logging, `sys.path` y el estado del repositorio (rama, commit y *dirty flag*).
2. Consulta el histórico acumulado en `docs/reports/debug_sessions.md` y `docs/reports/debug_progress.md` para entender qué verificaciones se han realizado y cuáles quedan pendientes.
3. Desde la CLI, `feriactl debug report --full` produce la misma información y permite compartirla con el equipo de SRE o soporte.
4. Añade notas manuales sobre incidencias o hallazgos en `docs/reports/debug_progress.md` para mantener el contexto operativo.

> Consejo: incluye la salida más reciente de `scripts/debug_suite.py` como artefacto en tus PRs cuando afecten a infraestructura, flujos de despliegue o tooling local. Así el revisor puede reproducir el entorno exacto y validar los cambios sin ambigüedades.

Para más contexto estratégico, revisa el documento “Lienzo maestro — FERIA Precision Codex” que inspiró este scaffolding y coordina cada sprint con los criterios de aceptación definidos allí.
