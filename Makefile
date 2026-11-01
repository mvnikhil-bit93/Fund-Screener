UV ?= uv
export UV_CACHE_DIR ?= $(CURDIR)/.cache/uv
RUN = $(UV) run --frozen --offline --no-sync

.PHONY: setup check lockcheck lint format typecheck boundaries allowlist test golden

setup:
	$(UV) sync --frozen --all-packages

check: lockcheck lint typecheck boundaries allowlist test

lockcheck:
	$(UV) lock --check --offline

lint:
	$(RUN) ruff check .
	$(RUN) ruff format --check .

format:
	$(RUN) ruff format .

typecheck:
	$(RUN) mypy packages/ledger/src packages/ingest/src packages/engines/src packages/access/src scripts

boundaries:
	$(RUN) lint-imports --no-cache
	$(RUN) python scripts/check_engine_imports.py

allowlist:
	$(RUN) python scripts/check_allowlist.py

test:
	$(RUN) python -m pytest

golden:
	$(RUN) python -m pytest tests/golden
