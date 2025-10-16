"""Scheduler placeholder."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def start() -> None:
    scheduler.start()
    print("Orchestrator scheduler started")


if __name__ == "__main__":
    start()
