"""PID governor with feed-forward heuristics for GPU scheduling.

The implementation models the behaviour described in the programme playbook:

* keep utilisation close to ``target_util`` using a PID loop with
  anti-windup on the integral term and a derivative term that takes the
  sampling interval into account;
* add a feed-forward term based on queue backlog to anticipate bursts;
* reduce load (and optionally divert traffic) when memory or temperature
  headroom becomes tight;
* return actionable levers for the orchestrator: concurrency scaling,
  micro-batch size, ``max_new_tokens`` and queues that should be paused.

The module is intentionally framework-agnostic so it can be used both in
the orchestrator service and in offline simulations.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf
from time import monotonic


@dataclass(frozen=True)
class GovernorConfig:
    """Configuration knobs for :class:`GpuGovernor`."""

    target_util: float = 0.8
    kp: float = 0.6
    ki: float = 0.25
    kd: float = 0.15
    kf: float = 0.4
    min_scale: float = 0.25
    max_scale: float = 1.75
    integral_limit: float = 2.0
    backlog_normalizer: float = 32.0
    max_temperature: float = 82.0
    max_memory: float = 0.85
    base_micro_batch: int = 1
    max_micro_batch: int = 16
    base_max_new_tokens: int = 2048
    min_max_new_tokens: int = 256
    pause_queues_on_hot: tuple[str, ...] = ("batch", "eval")


@dataclass(frozen=True)
class GpuMetrics:
    """Snapshot of GPU and workload metrics used by the governor."""

    utilisation: float
    memory_utilisation: float
    temperature: float
    backlog: float
    concurrency: float
    backlog_target: float
    micro_batch: int
    max_new_tokens: int


@dataclass(frozen=True)
class GovernorDecision:
    """Outcome of a control step."""

    concurrency_scale: float
    micro_batch: int
    max_new_tokens: int
    divert_to_cpu: bool
    pause_queues: tuple[str, ...]


class GpuGovernor:
    """PID+feed-forward controller for GPU load governance."""

    def __init__(self, config: GovernorConfig | None = None) -> None:
        self._config = config or GovernorConfig()
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = None

    def reset(self) -> None:
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = None

    def update(self, metrics: GpuMetrics, *, now: float | None = None) -> GovernorDecision:
        """Run the control loop and return a :class:`GovernorDecision`."""

        if metrics.backlog_target <= 0:
            raise ValueError("backlog_target must be > 0")

        cfg = self._config
        timestamp = monotonic() if now is None else now
        dt = 0.0 if self._last_time is None else max(1e-6, timestamp - self._last_time)
        error = cfg.target_util - metrics.utilisation
        self._integral = _clamp(
            self._integral + error * dt,
            -cfg.integral_limit,
            cfg.integral_limit,
        )
        derivative = 0.0 if self._last_time is None else (error - self._last_error) / dt
        backlog_term = (metrics.backlog - metrics.backlog_target) / max(
            cfg.backlog_normalizer,
            metrics.backlog_target,
            1.0,
        )
        control = (
            cfg.kp * error
            + cfg.ki * self._integral
            + cfg.kd * derivative
            + cfg.kf * backlog_term
        )
        scale = _clamp(1.0 + control, cfg.min_scale, cfg.max_scale)

        divert = False
        pause_queues: tuple[str, ...] = ()
        if metrics.memory_utilisation >= cfg.max_memory or metrics.temperature >= cfg.max_temperature:
            # Clamp hard to avoid OOM/thermal trips and signal the orchestrator.
            scale = cfg.min_scale
            divert = True
            pause_queues = cfg.pause_queues_on_hot

        micro_batch = _clamp_int(
            int(round(metrics.micro_batch * scale)),
            cfg.base_micro_batch,
            cfg.max_micro_batch,
        )
        max_tokens = _clamp_int(
            int(round(metrics.max_new_tokens * scale)),
            cfg.min_max_new_tokens,
            cfg.base_max_new_tokens,
        )

        self._last_time = timestamp
        self._last_error = error

        return GovernorDecision(
            concurrency_scale=scale,
            micro_batch=micro_batch,
            max_new_tokens=max_tokens,
            divert_to_cpu=divert,
            pause_queues=pause_queues,
        )


def _clamp(value: float, lower: float | None, upper: float | None) -> float:
    lower = -inf if lower is None else lower
    upper = inf if upper is None else upper
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def _clamp_int(value: int, lower: int, upper: int) -> int:
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


__all__ = [
    "GovernorConfig",
    "GpuGovernor",
    "GpuMetrics",
    "GovernorDecision",
]
