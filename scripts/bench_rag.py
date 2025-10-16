"""Benchmark sintético para RAG."""

from __future__ import annotations

import logging
import random

from core.logging import setup as setup_logging


logger = logging.getLogger(__name__)


def run_benchmark(samples: int = 10) -> float:
    logger.debug("Iniciando benchmark de RAG con %s muestras", samples)
    result = sum(random.random() for _ in range(samples)) / samples
    logger.debug("Resultado provisional del benchmark: %.4f", result)
    return result


def main() -> None:
    setup_logging()
    logger.info("Ejecutando benchmark sintético de RAG")
    score = run_benchmark()
    logger.info("nDCG@5 placeholder: %.2f", score)
    print(f"nDCG@5 placeholder: {score:.2f}")


if __name__ == "__main__":
    main()
