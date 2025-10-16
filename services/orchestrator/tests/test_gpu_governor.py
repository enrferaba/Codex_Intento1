from __future__ import annotations

import math

import pytest

from orchestrator import (
    GpuGovernor,
    GpuMetrics,
    GovernorConfig,
)


def test_governor_increases_scale_when_util_low_and_backlog_high() -> None:
    governor = GpuGovernor(GovernorConfig(target_util=0.8))
    metrics = GpuMetrics(
        utilisation=0.4,
        memory_utilisation=0.4,
        temperature=60.0,
        backlog=80,
        backlog_target=40,
        concurrency=8,
        micro_batch=2,
        max_new_tokens=1024,
    )
    decision = governor.update(metrics, now=0.0)
    assert decision.concurrency_scale > 1.0
    assert decision.micro_batch >= metrics.micro_batch
    assert decision.max_new_tokens >= metrics.max_new_tokens


def test_governor_limits_scale_when_hot() -> None:
    cfg = GovernorConfig(min_scale=0.3, pause_queues_on_hot=("batch",))
    governor = GpuGovernor(cfg)
    metrics = GpuMetrics(
        utilisation=0.7,
        memory_utilisation=0.9,
        temperature=90.0,
        backlog=10,
        backlog_target=20,
        concurrency=4,
        micro_batch=4,
        max_new_tokens=2048,
    )
    decision = governor.update(metrics, now=1.0)
    assert math.isclose(decision.concurrency_scale, cfg.min_scale)
    assert decision.divert_to_cpu is True
    assert decision.pause_queues == cfg.pause_queues_on_hot


def test_governor_integral_clamped() -> None:
    cfg = GovernorConfig(integral_limit=0.1)
    governor = GpuGovernor(cfg)
    metrics = GpuMetrics(
        utilisation=0.0,
        memory_utilisation=0.1,
        temperature=50.0,
        backlog=10,
        backlog_target=10,
        concurrency=2,
        micro_batch=1,
        max_new_tokens=512,
    )
    # Run several updates with large error to saturate the integral term.
    for step in range(1, 6):
        governor.update(metrics, now=float(step))
    decision = governor.update(metrics, now=10.0)
    assert decision.concurrency_scale <= cfg.max_scale


def test_governor_requires_positive_backlog_target() -> None:
    governor = GpuGovernor()
    metrics = GpuMetrics(
        utilisation=0.5,
        memory_utilisation=0.2,
        temperature=55.0,
        backlog=0,
        backlog_target=0,
        concurrency=1,
        micro_batch=1,
        max_new_tokens=512,
    )
    with pytest.raises(ValueError):
        governor.update(metrics)
