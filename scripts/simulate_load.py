"""Herramienta de simulación de carga para FERIA Precision Codex."""

from __future__ import annotations

import argparse
import itertools
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Mapping, MutableSequence

from core.logging import setup as setup_logging
from orchestrator import (
    AdmissionController,
    GpuGovernor,
    GpuMetrics,
    GovernorConfig,
    QueueManager,
)


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SimulationResult:
    enqueued: Mapping[str, int]
    rejected: Mapping[str, int]
    total_requests: int
    duration_seconds: float
    governor_decision: object | None = None

    def summary(self) -> str:
        base = (
            "total=%s enqueued=%s rejected=%s duration=%ss"
            % (self.total_requests, dict(self.enqueued), dict(self.rejected), self.duration_seconds)
        )
        if self.governor_decision:
            decision = self.governor_decision
            base += (
                " governor={concurrency_scale:.2f}/{micro_batch}mb/{max_new_tokens}tok"
                .format(
                    concurrency_scale=getattr(decision, "concurrency_scale", 1.0),
                    micro_batch=getattr(decision, "micro_batch", 0),
                    max_new_tokens=getattr(decision, "max_new_tokens", 0),
                )
            )
        return base


def parse_mix(mix: str) -> Dict[str, int]:
    if not mix:
        raise ValueError("mix cannot be empty")
    weights: Dict[str, int] = {}
    for chunk in mix.split(","):
        if "=" not in chunk:
            raise ValueError(f"Invalid mix fragment '{chunk}'")
        name, raw = chunk.split("=", 1)
        name = name.strip()
        if not name:
            raise ValueError("Queue name cannot be empty")
        weight = int(float(raw.strip()))
        if weight <= 0:
            raise ValueError("Weight must be positive")
        weights[name] = weight
    return weights


def _expand_mix(weights: Mapping[str, int]) -> Iterable[str]:
    sequence: list[str] = []
    for name, weight in weights.items():
        sequence.extend([name] * weight)
    if not sequence:
        raise ValueError("Weights must contain at least one queue")
    return itertools.cycle(sequence)


def create_default_controller() -> AdmissionController:
    config = [
        {
            "tenant": "default",
            "fast": {"rate": 30, "burst": 60, "max_inflight": 50},
            "batch": {"rate": 10, "burst": 20, "max_inflight": 200},
            "eval": {"rate": 2, "burst": 4, "max_inflight": 20},
        }
    ]
    return AdmissionController.from_dict(config)


def run_simulation(
    *,
    qps: int,
    duration: float,
    mix: Mapping[str, int],
    controller: AdmissionController,
    manager: QueueManager,
    tenant: str = "default",
    sleep: Callable[[float], None] | None = None,
    governor: GpuGovernor | None = None,
    metrics_factory: Callable[[dict[str, int], dict[str, int], MutableSequence[float], int, float], GpuMetrics]
    | None = None,
) -> SimulationResult:
    if qps <= 0:
        raise ValueError("qps must be greater than zero")
    if duration <= 0:
        raise ValueError("duration must be greater than zero")
    interval = 1.0 / qps
    total_requests = int(round(duration * qps))
    request_mix = _expand_mix(mix)
    stats_enqueued: Dict[str, int] = defaultdict(int)
    stats_rejected: Dict[str, int] = defaultdict(int)
    backlog_history: MutableSequence[float] = []
    now = 0.0
    for _ in range(total_requests):
        queue = next(request_mix)
        decision = controller.allow(tenant, queue, now=now)
        if decision.allowed:
            manager.enqueue(queue, {"queue": queue}, now=now)
            controller.release(tenant, queue)
            manager.dequeue(queue)
            stats_enqueued[queue] += 1
        else:
            stats_rejected[queue] += 1
        backlog = sum(snapshot.depth for snapshot in manager.stats())
        backlog_history.append(backlog)
        now += interval
        if sleep:
            sleep(interval)
    decision = None
    if governor:
        factory = metrics_factory or default_metrics_factory
        metrics = factory(stats_enqueued, stats_rejected, backlog_history, qps, duration)
        decision = governor.update(metrics)
    return SimulationResult(stats_enqueued, stats_rejected, total_requests, duration, decision)


def default_metrics_factory(
    enqueued: Mapping[str, int],
    rejected: Mapping[str, int],
    backlog_history: MutableSequence[float],
    qps: int,
    duration: float,
) -> GpuMetrics:
    total_enqueued = sum(enqueued.values())
    total_requests = total_enqueued + sum(rejected.values())
    utilisation = min(1.0, total_enqueued / max(total_requests, 1))
    backlog_peak = max(backlog_history or [0.0])
    backlog_last = backlog_history[-1] if backlog_history else 0.0
    backlog_target = max(1.0, qps)
    memory_utilisation = min(0.99, 0.55 + 0.01 * backlog_peak)
    temperature = min(95.0, 58.0 + 0.4 * backlog_last)
    concurrency = max(1.0, total_enqueued / max(duration, 1e-6))
    return GpuMetrics(
        utilisation=utilisation,
        memory_utilisation=memory_utilisation,
        temperature=temperature,
        backlog=backlog_peak,
        backlog_target=backlog_target,
        concurrency=concurrency,
        micro_batch=4,
        max_new_tokens=1024,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Simula carga sintética para rutas FERIA")
    parser.add_argument("--qps", type=int, default=10)
    parser.add_argument("--mix", type=str, default="fast=80,batch=20")
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--tenant", type=str, default="default")
    parser.add_argument(
        "--sleep",
        action="store_true",
        help="realiza pausas reales para emular el reloj",
    )
    parser.add_argument(
        "--with-governor",
        action="store_true",
        help="calcula la decisión del GPU governor tras la simulación",
    )
    parser.add_argument(
        "--target-util",
        type=float,
        default=0.8,
        help="utilización objetivo para el governor",
    )
    args = parser.parse_args()

    setup_logging()
    mix = parse_mix(args.mix)
    controller = create_default_controller()
    manager = QueueManager(list(mix.keys()))
    logger.debug(
        "Iniciando simulación: qps=%s duration=%s mix=%s tenant=%s",
        args.qps,
        args.duration,
        args.mix,
        args.tenant,
    )
    governor = GpuGovernor(GovernorConfig(target_util=args.target_util)) if args.with_governor else None
    result = run_simulation(
        qps=args.qps,
        duration=args.duration,
        mix=mix,
        controller=controller,
        manager=manager,
        tenant=args.tenant,
        sleep=(lambda interval: __import__("time").sleep(interval)) if args.sleep else None,
        governor=governor,
    )
    logger.info("Resultado de la simulación: %s", result.summary())
    print(result.summary())


if __name__ == "__main__":
    main()
