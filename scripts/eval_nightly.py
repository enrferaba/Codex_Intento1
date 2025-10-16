"""Runner simplificado del laboratorio de precisión."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def generate_report(path: Path) -> None:
    now = datetime.utcnow().isoformat()
    content = f"# Nightly Eval\n\n- timestamp: {now}\n- status: placeholder\n"
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta la evaluación nocturna placeholder")
    parser.add_argument("--report", default="docs/reports/eval-nightly.md")
    args = parser.parse_args()
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    generate_report(report_path)
    print(f"Reporte generado en {report_path}")


if __name__ == "__main__":
    main()
