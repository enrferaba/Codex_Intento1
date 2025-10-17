PYTHON ?= python3
POETRY ?= poetry
UV ?= uv

.PHONY: bootstrap pre-commit dev-up dev-down lint test debug-test debug-report build-images ingest eval-nightly snapshot restore simulate clean

bootstrap:
	$(UV) venv --python $(PYTHON)
	$(UV) pip install -r requirements-dev.txt || true
	pre-commit install

pre-commit:
	pre-commit run --all-files

lint:
	$(UV) run ruff check .
	$(UV) run mypy apps packages services

test:
	$(UV) run pytest

debug-test:
	FERIA_DEBUG=1 $(UV) run pytest -vv

debug-report:
	$(UV) run python scripts/debug_suite.py --json

dev-up:
	docker compose --profile dev up -d

dev-down:
	docker compose --profile dev down

build-images:
	docker compose build

ingest:
	$(UV) run apps/feriactl -m feriactl.ingest $(REPO)

eval-nightly:
	$(UV) run scripts/eval_nightly.py

snapshot:
	$(UV) run scripts/snapshot_create.py $(label)

restore:
	$(UV) run scripts/snapshot_restore.py $(id)

simulate:
	$(UV) run scripts/simulate_load.py --qps $(QPS) --mix $(MIX) --duration $(DUR)

clean:
	rm -rf .uv .ruff_cache .mypy_cache __pycache__
