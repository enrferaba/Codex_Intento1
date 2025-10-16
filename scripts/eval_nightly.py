"""Runner simplificado del laboratorio de precisión."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path

from core.logging import setup as setup_logging


logger = logging.getLogger(__name__)


def generate_report(path: Path) -> None:
    now = datetime.utcnow().isoformat()
    content = f"# Nightly Eval\n\n- timestamp: {now}\n- status: placeholder\n"
    path.write_text(content, encoding="utf-8")
    logger.debug("Reporte escrito en %s", path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta la evaluación nocturna placeholder")
    parser.add_argument("--report", default="docs/reports/eval-nightly.md")
    args = parser.parse_args()
    setup_logging()
    logger.info("Generando reporte nightly en %s", args.report)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    generate_report(report_path)
    logger.info("Reporte nightly generado correctamente")
    print(f"Reporte generado en {report_path}")


if __name__ == "__main__":
    main()
