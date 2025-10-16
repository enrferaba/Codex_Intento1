from time import monotonic

import pytest

from orchestrator.admission import AdmissionController, Quota


@pytest.fixture
def controller() -> AdmissionController:
    return AdmissionController(
        {
            "default": {
                "fast": Quota(rate=10, burst=5, max_inflight=2),
                "batch": Quota(rate=1, burst=1, max_inflight=1),
            }
        }
    )


def test_allow_and_release_cycle(controller: AdmissionController) -> None:
    decision = controller.allow("default", "fast")
    assert decision.allowed
    controller.release("default", "fast")
    decision_after_release = controller.allow("default", "fast")
    assert decision_after_release.allowed


def test_respects_max_inflight(controller: AdmissionController) -> None:
    assert controller.allow("default", "fast").allowed
    assert controller.allow("default", "fast").allowed
    decision = controller.allow("default", "fast")
    assert not decision.allowed
    assert decision.reason == "max_inflight"


def test_rate_limit_enforced(controller: AdmissionController) -> None:
    assert controller.allow("default", "batch").allowed
    controller.release("default", "batch")
    decision = controller.allow("default", "batch", now=monotonic())
    assert not decision.allowed
    assert decision.reason == "rate_limit"


def test_refill_allows_after_time(controller: AdmissionController) -> None:
    now = monotonic()
    assert controller.allow("default", "batch", now=now).allowed
    controller.release("default", "batch")
    later = now + 2
    decision = controller.allow("default", "batch", now=later)
    assert decision.allowed


def test_snapshot_returns_tokens(controller: AdmissionController) -> None:
    snapshot = controller.snapshot()
    assert "default" in snapshot
    assert "fast" in snapshot["default"]
    fast_view = snapshot["default"]["fast"]
    assert fast_view["tokens"] <= fast_view["max_tokens"]
