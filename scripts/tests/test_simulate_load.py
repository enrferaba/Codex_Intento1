import math

import pytest

from orchestrator import (
    AdmissionController,
    GpuGovernor,
    GpuMetrics,
    GovernorConfig,
    QueueManager,
)
from scripts import simulate_load


def test_parse_mix_valid() -> None:
    assert simulate_load.parse_mix("fast=80,batch=20") == {"fast": 80, "batch": 20}


def test_parse_mix_invalid() -> None:
    with pytest.raises(ValueError):
        simulate_load.parse_mix("fast80")


def test_run_simulation_counts() -> None:
    controller = AdmissionController.from_dict(
        [
            {
                "tenant": "default",
                "fast": {"rate": 100, "burst": 100, "max_inflight": 5},
            }
        ]
    )
    manager = QueueManager(["fast"])
    result = simulate_load.run_simulation(
        qps=10,
        duration=1.0,
        mix={"fast": 1},
        controller=controller,
        manager=manager,
        sleep=None,
    )
    assert result.total_requests == 10
    assert result.enqueued["fast"] == 10
    assert result.summary().startswith("total=10")


def test_run_simulation_respects_qps() -> None:
    controller = AdmissionController.from_dict(
        [
            {
                "tenant": "default",
                "fast": {"rate": 1, "burst": 1, "max_inflight": 1},
            }
        ]
    )
    manager = QueueManager(["fast"])
    result = simulate_load.run_simulation(
        qps=1,
        duration=1.0,
        mix={"fast": 1},
        controller=controller,
        manager=manager,
        sleep=None,
    )
    assert math.isclose(result.duration_seconds, 1.0)
    assert result.enqueued["fast"] <= result.total_requests


def test_run_simulation_with_governor_uses_metrics_factory() -> None:
    controller = AdmissionController.from_dict(
        [
            {
                "tenant": "default",
                "fast": {"rate": 100, "burst": 100, "max_inflight": 5},
            }
        ]
    )
    manager = QueueManager(["fast"])
    governor = GpuGovernor(GovernorConfig(target_util=0.9))

    def factory(enqueued, rejected, backlog_history, qps, duration):
        assert enqueued["fast"] > 0
        assert backlog_history
        return GpuMetrics(
            utilisation=0.5,
            memory_utilisation=0.4,
            temperature=60.0,
            backlog=1.0,
            backlog_target=1.0,
            concurrency=1.0,
            micro_batch=2,
            max_new_tokens=512,
        )

    result = simulate_load.run_simulation(
        qps=5,
        duration=1.0,
        mix={"fast": 1},
        controller=controller,
        manager=manager,
        sleep=None,
        governor=governor,
        metrics_factory=factory,
    )
    assert result.governor_decision is not None
