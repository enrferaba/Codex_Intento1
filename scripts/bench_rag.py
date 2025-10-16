"""Benchmark sintético para RAG."""

from __future__ import annotations

import random


def run_benchmark(samples: int = 10) -> float:
    return sum(random.random() for _ in range(samples)) / samples


def main() -> None:
    score = run_benchmark()
    print(f"nDCG@5 placeholder: {score:.2f}")


if __name__ == "__main__":
    main()
