"""Admission control con token bucket por tenant y cola."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import monotonic
from typing import Dict, Iterable, Mapping, Tuple


@dataclass(frozen=True)
class Quota:
    """Reglas de rate limit y concurrencia."""

    rate: float
    burst: int
    max_inflight: int

    def __post_init__(self) -> None:
        if self.rate <= 0:
            raise ValueError("rate must be > 0")
        if self.burst <= 0:
            raise ValueError("burst must be > 0")
        if self.max_inflight <= 0:
            raise ValueError("max_inflight must be > 0")


@dataclass
class _BucketState:
    quota: Quota
    tokens: float
    updated_at: float
    inflight: int = 0


class AdmissionDecision(Tuple[bool, str | None]):
    """Tuple tipado para el resultado."""

    __slots__ = ()

    @property
    def allowed(self) -> bool:
        return self[0]

    @property
    def reason(self) -> str | None:
        return self[1]


class AdmissionController:
    """Gestor de cuotas por tenant y cola."""

    def __init__(self, quotas: Mapping[str, Mapping[str, Quota]]) -> None:
        if not quotas:
            raise ValueError("At least one tenant quota is required")
        self._buckets: Dict[str, Dict[str, _BucketState]] = {}
        now = monotonic()
        for tenant, queues in quotas.items():
            if not queues:
                raise ValueError(f"Tenant '{tenant}' must define at least one queue")
            tenant_buckets: Dict[str, _BucketState] = {}
            for queue, quota in queues.items():
                tenant_buckets[queue] = _BucketState(quota=quota, tokens=quota.burst, updated_at=now)
            self._buckets[tenant] = tenant_buckets
        self._lock = Lock()

    @classmethod
    def from_dict(cls, config: Iterable[Mapping[str, object]]) -> "AdmissionController":
        """Construye el controlador a partir de la estructura de YAML."""

        quotas: Dict[str, Dict[str, Quota]] = {}
        for entry in config:
            tenant = str(entry.get("tenant"))
            if not tenant:
                raise ValueError("Missing tenant identifier")
            queues_conf = {k: v for k, v in entry.items() if k != "tenant"}
            queue_quotas: Dict[str, Quota] = {}
            for queue_name, raw in queues_conf.items():
                if not isinstance(raw, Mapping):
                    raise TypeError(f"Quota for {tenant}/{queue_name} must be a mapping")
                quota = Quota(
                    rate=float(raw.get("rate", 0)),
                    burst=int(raw.get("burst", 0)),
                    max_inflight=int(raw.get("max_inflight", 0)),
                )
                queue_quotas[queue_name] = quota
            quotas[tenant] = queue_quotas
        return cls(quotas)

    def allow(self, tenant: str, queue: str, *, weight: int = 1, now: float | None = None) -> AdmissionDecision:
        """Evalúa si se puede admitir otra solicitud."""

        now_monotonic = monotonic() if now is None else now
        with self._lock:
            bucket = self._get_bucket(tenant, queue)
            self._refill(bucket, now_monotonic)
            if bucket.inflight >= bucket.quota.max_inflight:
                return AdmissionDecision((False, "max_inflight"))
            if bucket.tokens < weight:
                return AdmissionDecision((False, "rate_limit"))
            bucket.tokens -= weight
            bucket.inflight += 1
            return AdmissionDecision((True, None))

    def release(self, tenant: str, queue: str, *, weight: int = 1) -> None:
        """Reduce el contador de concurrencia tras completar un trabajo."""

        with self._lock:
            bucket = self._get_bucket(tenant, queue)
            bucket.inflight = max(0, bucket.inflight - weight)

    def snapshot(self) -> Dict[str, Dict[str, dict[str, float]]]:
        """Devuelve estadísticas actuales para observabilidad."""

        with self._lock:
            snapshot: Dict[str, Dict[str, dict[str, float]]] = {}
            for tenant, queues in self._buckets.items():
                tenant_view: Dict[str, dict[str, float]] = {}
                for queue, bucket in queues.items():
                    tenant_view[queue] = {
                        "tokens": bucket.tokens,
                        "max_tokens": bucket.quota.burst,
                        "inflight": float(bucket.inflight),
                        "max_inflight": float(bucket.quota.max_inflight),
                    }
                snapshot[tenant] = tenant_view
            return snapshot

    def _get_bucket(self, tenant: str, queue: str) -> _BucketState:
        try:
            tenant_buckets = self._buckets[tenant]
        except KeyError as exc:  # pragma: no cover - defensa
            raise KeyError(f"Unknown tenant '{tenant}'") from exc
        try:
            return tenant_buckets[queue]
        except KeyError as exc:  # pragma: no cover - defensa
            raise KeyError(f"Unknown queue '{queue}' for tenant '{tenant}'") from exc

    @staticmethod
    def _refill(bucket: _BucketState, now: float) -> None:
        elapsed = max(0.0, now - bucket.updated_at)
        if not elapsed:
            return
        bucket.tokens = min(bucket.quota.burst, bucket.tokens + elapsed * bucket.quota.rate)
        bucket.updated_at = now


__all__ = ["AdmissionController", "Quota", "AdmissionDecision"]
