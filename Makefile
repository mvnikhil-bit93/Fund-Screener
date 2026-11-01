UV ?= uv
export UV_CACHE_DIR ?= $(CURDIR)/.cache/uv
export FI_TEST_ADMIN_DSN ?= postgresql://postgres@127.0.0.1:55432/postgres
RUN = $(UV) run --frozen --offline --no-sync

.PHONY: setup check lockcheck lint format typecheck boundaries allowlist test golden integration db-start db-stop db-status db-migrate

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
	$(RUN) python -m pytest --ignore=tests/integration

golden:
	$(RUN) python -m pytest tests/golden

integration:
	$(RUN) python -m pytest -m integration tests/integration

db-start:
	$(RUN) python scripts/local_postgres.py start

db-stop:
	$(RUN) python scripts/local_postgres.py stop

db-status:
	$(RUN) python scripts/local_postgres.py status

db-migrate:
	$(RUN) python scripts/local_postgres.py migrate
