"""Governor PID simplificado."""

from __future__ import annotations

TARGET_UTIL = 0.8
Kp = 0.5


def adjust(utilization: float) -> float:
    error = TARGET_UTIL - utilization
    return max(0.1, min(1.0, 0.5 + Kp * error))
