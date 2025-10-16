"""Herramienta de simulación de carga para FERIA Precision Codex."""

from __future__ import annotations

import argparse
import time


def simulate(qps: int, duration: float) -> None:
    interval = 1.0 / max(qps, 1)
    end = time.time() + duration
    iterations = 0
    while time.time() < end:
        iterations += 1
        time.sleep(interval)
    print(f"Simulated {iterations} synthetic requests at {qps} QPS for {duration}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simula carga sintética para rutas FERIA")
    parser.add_argument("--qps", type=int, default=10)
    parser.add_argument("--mix", type=str, default="fast=80,batch=20")
    parser.add_argument("--duration", type=float, default=60.0)
    args = parser.parse_args()
    simulate(args.qps, args.duration)


if __name__ == "__main__":
    main()
