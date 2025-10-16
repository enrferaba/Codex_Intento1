"""Configura ``sys.path`` para los paquetes locales del monorepo."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

for relative in [
    "apps/feriactl/src",
    "packages/core/src",
    "packages/agent/src",
    "packages/policy/src",
    "packages/eval/src",
    "packages/observability/src",
    "packages/metrics-client/src",
    "packages/sdk/src",
    "services/api-gateway/src",
    "services/model-gateway/src",
    "services/orchestrator/src",
    "services/retrieval/src",
]:
    path = ROOT / relative
    sys.path.append(str(path))
