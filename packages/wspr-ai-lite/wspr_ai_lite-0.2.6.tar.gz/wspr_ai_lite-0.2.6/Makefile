# ===================================================================
# Makefile for wspr-ai-lite
# -------------------------------------------------------------------
# Provides common developer shortcuts:
#   - Environment setup (venv, dependencies)
#   - Running the app
#   - Ingesting WSPR data
#   - Testing
#   - Cleaning and resetting the project
#   - Docs build/deploy (MkDocs)
#   - Pre-commit & documentation checks
#
# Usage:
#   make <target>
# Examples:
#   make setup-dev   # Create venv + install dev deps + install pre-commit hooks
#   make run         # Launch Streamlit UI
#   make ingest      # Ingest a sample month
#   make test        # Run pytest
#   make docs-serve  # Serve MkDocs locally
#   make docs-deploy # Deploy MkDocs to gh-pages
#   make reset       # Clean EVERYTHING and rebuild fresh
# ===================================================================

PKG_NAME      ?= wspr-ai-lite

PY      := python3
VENV    := .venv
ACT     := . $(VENV)/bin/activate
PIP     := $(PY) -m pip

# Resolve version once at make invocation
VERSION := $(shell $(PY) scripts/get_version.py)

# smoke-test variables
SMOKE_VENV    ?= .smoke-venv
SMOKE_TMP     ?= .smoke-tmp
SMOKE_DB      ?= $(SMOKE_TMP)/wspr.duckdb
SMOKE_PY      := $(SMOKE_VENV)/bin/python
SMOKE_PIP     := $(SMOKE_VENV)/bin/pip
SMOKE_CLI     := $(SMOKE_VENV)/bin/wspr-ai-lite
SMOKE_MONTH		?= 2014-07

# -------------------------------------------------------------------
# Colors
# -------------------------------------------------------------------
C_R     := '\033[01;31m'   # red
C_G     := '\033[01;32m'   # green
C_Y     := '\033[01;33m'   # yellow
C_C     := '\033[01;36m'   # cyan
C_NC    := '\033[01;37m'   # no color


.PHONY: help setup-dev venv install install-dev run ingest test lint-docs precommit-install clean distclean reset docs-serve docs-deploy ui

help:
	@echo ''
	@echo 'Available Make Targets'
	@echo '-------------------------------------------------------------------------------'
	@grep -E '^[a-zA-Z0-9_.-]+:.*?##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build PyPi Pyjon Package
	@$(ACT); python -m build

publish-test: ## Pulublish Package to PyPi Test Repository
	@$(ACT); python -m pip install --upgrade build twine
	@$(ACT); python -m build
	@$(ACT); python -m twine upload --repository testpypi dist/*

publish: ## Pulublish Package to PyPi Production Repository
	@$(ACT); python -m pip install --upgrade build twine
	@$(ACT); python -m build
	@$(ACT); python -m twine upload dist/*

setup-dev: venv ## Create venv, install dev+docs deps, install pre-commit hooks
	@$(ACT); $(PIP) install --upgrade pip
	@$(ACT); $(PIP) install -r requirements.txt
	@$(ACT); $(PIP) install -r requirements-dev.txt
	@$(ACT); $(PIP) install -r requirements-docs.txt
	@$(ACT); pre-commit install
	@echo ''
	@echo "Dev environment ready (venv, runtime+dev+docs deps, pre-commit hooks)."
	@echo "To use venv, type: source .venv/bin/activate"
	@echo ''

# setup-dev: venv ## Create venv, install dev+docs deps, install pre-commit hooks
# 	@$(ACT); $(PIP) install --upgrade pip
# 	@$(ACT); $(PIP) install -r requirements-dev.txt
# 	@$(ACT); if [ -f requirements-docs.txt ]; then \
# 		echo "[setup-dev] Installing docs deps from requirements-docs.txt"; \
# 		$(PIP) install -r requirements-docs.txt; \
# 	else \
# 		echo "[setup-dev] requirements-docs.txt not found (skipping docs deps)"; \
# 	fi
# 	@$(ACT); pre-commit install
# 	@echo "Dev environment ready (venv, dev+docs deps, pre-commit hooks)."

venv: ## Create Python virtual environment (.venv)
	@test -d $(VENV) || ($(PY) -m venv $(VENV) && echo "Created $(VENV)")

install: ## Install runtime dependencies (requirements.txt)
	@$(ACT); $(PIP) install --upgrade pip
	@$(ACT); $(PIP) install -r requirements.txt

install-dev: ## Install dev dependencies (requirements-dev.txt)
	@$(ACT); $(PIP) install --upgrade pip
	@$(ACT); $(PIP) install -r requirements-dev.txt

ingest: ## Ingest a sample month (2014-07)
	@$(ACT); $(PY) pipelines/ingest.py --from 2014-07 --to 2014-07

run: ## Run Streamlit UI
	@DB?=data/wspr.duckdb; \
	echo "[ui] DB=$${DB}"; \
	wspr-ai-lite ui --db "$${DB}" --port 8501

test: ##  Run pytest
	@$(ACT); PYTHONPATH=. pytest -q

lint-docs: ## Docstring checks: coverage (interrogate) + style (pydocstyle)
	@$(ACT); interrogate -i -v -m -p -r app pipelines tests | sed 's/^/interrogate: /'
	@$(ACT); pydocstyle app pipelines tests || true

precommit-install: ## Install git pre-commit hooks
	@$(ACT); pre-commit install

clean: ## Clean temporary files, caches, local DBs, and MkDocs site/
	@find . -name "__pycache__" -type d -prune -exec rm -rf {} \; || true
	@rm -rf .pytest_cache .cache .cache_* || true
	@rm -f .cache_history.json || true
	@rm -f data/*.duckdb data/*.duckdb-wal || true
	@rm -rf htmlcov .coverage site || true
	@echo "Clean complete."

distclean: clean ## More thorough clean: includes venv, packaging artifacts, temp dirs
	@rm -rf $(VENV) || true
	@rm -rf .streamlit || true
	@rm -rf *.tar.gz *.zip || true
	@rm -rf tmp temp || true
	@rm -rf .smoke-tmp || true
	@rm -rf dist/ || true
	@echo "Dist-clean complete (venv, temp files, archives removed)."

reset: distclean ## Full reset: distclean + recreate venv + install deps + ingest sample
	@$(PY) -m venv $(VENV)
	@$(ACT); $(PIP) install --upgrade pip
	@$(ACT); $(PIP) install -r requirements.txt
	@$(ACT); $(PY) pipelines/ingest.py --from 2014-07 --to 2014-07
	@echo "Reset complete. Run: make run"

docs-serve: ## Serve docs locally with MkDocs (auto-reloads on changes)
	@VERSION=$$($(PY) -c "import tomllib, pathlib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['version'])"); \
	echo "WSPR_AI_LITE_VERSION=$$VERSION"; \
	PYTHONPATH=docs/_ext WSPR_AI_LITE_VERSION="$$VERSION" mkdocs serve

# docs-serve: ## Serve docs locally with MkDocs (auto-reloads on changes)
# 	@$(PIP) install -r requirements-docs.txt
# 	@WSPR_AI_LITE_VERSION=$(shell $(PYTHON) -c "import wspr_ai_lite; print(wspr_ai_lite.__version__)") \
# 		mkdocs serve

# docs-deploy: ## Deplot docs to hh-pages
# 	@$(ACT); mkdocs gh-deploy --force

# =============================================================================
# Smoke tests (automated)
#   End-to-end validation from a clean wheel install:
#     1) build wheel
#     2) create isolated venv
#     3) install built wheel
#     4) ingest one month into a temp DuckDB
#     5) assert rowcount > 0
#     6) verify UI app is packaged and Streamlit importable
# =============================================================================

.PHONY: smoke-test smoke-clean smoke-build smoke-install smoke-ingest smoke-verify smoke-ui-check

smoke-test: smoke-clean smoke-build smoke-install smoke-ingest smoke-verify smoke-ui-check ## Full end-to-end smoke test

smoke-build: ## Build wheel+sdist for smoke test
	@python -m pip install --disable-pip-version-check --upgrade pip build >/dev/null
	@python -m build
	@ls -1 dist/$(subst -,_,$(PKG_NAME))* 1>/dev/null
	@echo "[smoke] build: OK"

smoke-install: ## Create isolated smoke venv and install the built wheel
	@rm -rf $(SMOKE_VENV) $(SMOKE_TMP) && mkdir -p $(SMOKE_TMP)
	@python -m venv $(SMOKE_VENV)
	@$(SMOKE_PIP) install --upgrade pip >/dev/null
	@$(SMOKE_PIP) install dist/$(subst -,_,$(PKG_NAME))*whl >/dev/null
	@$(SMOKE_CLI) --version || true
	@echo "[smoke] install: OK"

smoke-ingest: ## Ingest a single month into a temporary DuckDB
	@mkdir -p $(SMOKE_TMP)
	@$(SMOKE_CLI) ingest --from $(SMOKE_MONTH) --to $(SMOKE_MONTH) --db $(SMOKE_DB)
	@echo "[smoke] ingest: OK"

smoke-verify: ## Verify the DuckDB contains rows
	@$(SMOKE_PY) -c "import duckdb, os, sys; db=os.environ.get('DB','$(SMOKE_DB)'); con=duckdb.connect(db, read_only=True); cnt=con.execute('SELECT COUNT(*) FROM spots').fetchone()[0]; print(f'[smoke] rows: {cnt}'); sys.exit(0 if cnt>0 else 2)"
	@echo "[smoke] verify: OK"

smoke-ui-check: ## Check UI presence and streamlit availability
	@$(SMOKE_PY) -c "import importlib, pathlib, wspr_ai_lite; p=pathlib.Path(wspr_ai_lite.__file__).with_name('wspr_ai_lite.py'); assert p.exists(), f'wspr_ai_lite.py missing at {p}'; importlib.import_module('streamlit'); print('[smoke] ui-check: app present & streamlit import OK')"
	@echo "[smoke] ui-check: OK"

smoke-clean: ## Remove smoke-test artifacts (venv + tmp DB)
	@rm -rf $(SMOKE_VENV) $(SMOKE_TMP)
	@echo "[smoke] clean: OK"

# Convenience: deeper clean that also removes smoke artifacts
.PHONY: dist-clean-all
dist-clean-all: dist-clean ## Deep clean + remove smoke artifacts
	@rm -rf .smoke-venv .smoke-tmp
	@echo "🧼 dist-clean-all: removed smoke artifacts."

.PHONY: smoke-test-pypi
smoke-test-pypi: smoke-clean ## Install from PyPI and run verify+ui-check
	@python -m venv $(SMOKE_VENV)
	@$(SMOKE_PIP) install --upgrade pip >/dev/null
	@$(SMOKE_PIP) install "wspr-ai-lite==$(VERSION)"
	@mkdir -p $(SMOKE_TMP)
	@$(SMOKE_CLI) ingest --from $(SMOKE_MONTH) --to $(SMOKE_MONTH) --db $(SMOKE_DB)
	@$(SMOKE_PY) -c "import duckdb,sys; con=duckdb.connect('$(SMOKE_DB)', read_only=True); cnt=con.execute('SELECT COUNT(*) FROM spots').fetchone()[0]; print(f'[smoke] rows: {cnt}'); sys.exit(0 if cnt>0 else 2)"
	@$(SMOKE_PY) -c "import importlib, pathlib, wspr_ai_lite; p=pathlib.Path(wspr_ai_lite.__file__).with_name('wspr_app.py'); assert p.exists(); importlib.import_module('streamlit'); print('[smoke] ui-check: app present & streamlit import OK')"
	@echo "[smoke] PyPI smoke: OK"
