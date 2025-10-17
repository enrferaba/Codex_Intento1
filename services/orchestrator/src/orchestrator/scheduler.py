"""Scheduler placeholder."""

from __future__ import annotations

from importlib import import_module
from typing import Protocol, runtime_checkable


@runtime_checkable
class SupportsStart(Protocol):
    def start(self) -> None:
        ...


def _create_scheduler() -> SupportsStart:
    module = import_module("apscheduler.schedulers.background")
    background_scheduler = getattr(module, "BackgroundScheduler")
    scheduler_instance = background_scheduler()
    assert isinstance(scheduler_instance, SupportsStart)
    return scheduler_instance


scheduler = _create_scheduler()


def start() -> None:
    scheduler.start()
    print("Orchestrator scheduler started")


if __name__ == "__main__":
    start()
