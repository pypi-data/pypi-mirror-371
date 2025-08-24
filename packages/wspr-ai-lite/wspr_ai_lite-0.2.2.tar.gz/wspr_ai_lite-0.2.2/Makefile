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

PY      := python3
PIP     := pip
VENV    := .venv
ACT     := . $(VENV)/bin/activate

.PHONY: help setup-dev venv install install-dev run ingest test lint-docs precommit-install clean distclean reset docs-serve docs-deploy

# -------------------------------------------------------------------
# Show available commands
# -------------------------------------------------------------------
help: ## Show this help
	@grep -E '^[a-zA-Z0-9_.-]+:.*?##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo "Available make targets:"
	@echo "  setup-dev      Create venv, install dev deps, install pre-commit hooks"
	@echo "  venv           Create Python virtual environment (.venv)"
	@echo "  install        Install runtime dependencies (requirements.txt)"
	@echo "  install-dev    Install dev dependencies (requirements-dev.txt)"
	@echo "  run            Run Streamlit UI"
	@echo "  ingest         Ingest a sample month (2014-07)"
	@echo "  test           Run pytest"
	@echo "  lint-docs      Docstring coverage/style checks (interrogate/pydocstyle)"
	@echo "  precommit-install Install git pre-commit hooks"
	@echo "  clean          Remove caches, __pycache__, test artifacts, local DB, site/"
	@echo "  distclean      clean + remove venv, temp, packaging artifacts"
	@echo "  reset          distclean + recreate venv + install + sample ingest"
	@echo "  docs-serve     Serve MkDocs site locally"
	@echo "  docs-deploy    Deploy MkDocs site to gh-pages"
	@echo "  build          Build PyPi Pyjon Package"
	@echo "  publish-test   Pulublish Package to PyPi Test Repository"
	@echo "  publish				Pulublish Package to PyPi Production Repository"

# -------------------------------------------------------------------
# Development to PyPI
# -------------------------------------------------------------------
build:
	@$(ACT); python -m build

publish-test:
	@$(ACT); python -m pip install --upgrade build twine
	@$(ACT); python -m build
	@$(ACT); python -m twine upload --repository testpypi dist/*

publish:
	@$(ACT); python -m pip install --upgrade build twine
	@$(ACT); python -m build
	@$(ACT); python -m twine upload dist/*

# -------------------------------------------------------------------
# Development setup: create venv, install dev requirements, install hooks
# -------------------------------------------------------------------
setup-dev: venv
	@$(ACT); $(PIP) install --upgrade pip
	@$(ACT); $(PIP) install -r requirements-dev.txt
	@$(ACT); pre-commit install
	@echo "Dev environment ready (venv, deps, pre-commit hooks)."

# -------------------------------------------------------------------
# Create Python virtual environment if missing
# -------------------------------------------------------------------
venv:
	@test -d $(VENV) || ($(PY) -m venv $(VENV) && echo "Created $(VENV)")

# -------------------------------------------------------------------
# Install only runtime dependencies (for end users)
# -------------------------------------------------------------------
install:
	@$(ACT); $(PIP) install --upgrade pip
	@$(ACT); $(PIP) install -r requirements.txt

# -------------------------------------------------------------------
# Install development dependencies (linters, tests, hooks)
# -------------------------------------------------------------------
install-dev:
	@$(ACT); $(PIP) install --upgrade pip
	@$(ACT); $(PIP) install -r requirements-dev.txt

# -------------------------------------------------------------------
# Run Streamlit dashboard
# -------------------------------------------------------------------
run:
	@$(ACT); streamlit run app/wspr_app.py

# -------------------------------------------------------------------
# Ingest a sample month of WSPR data (2014-07 by default)
# -------------------------------------------------------------------
ingest:
	@$(ACT); $(PY) pipelines/ingest.py --from 2014-07 --to 2014-07

# -------------------------------------------------------------------
# Run the test suite (pytest, with PYTHONPATH set for discovery)
# -------------------------------------------------------------------
test:
	@$(ACT); PYTHONPATH=. pytest -q

# -------------------------------------------------------------------
# Docstring checks: coverage (interrogate) + style (pydocstyle)
# -------------------------------------------------------------------
lint-docs:
	@$(ACT); interrogate -i -v -m -p -r app pipelines tests | sed 's/^/interrogate: /'
	@$(ACT); pydocstyle app pipelines tests || true

# -------------------------------------------------------------------
# Install git pre-commit hooks
# -------------------------------------------------------------------
precommit-install:
	@$(ACT); pre-commit install

# -------------------------------------------------------------------
# Clean temporary files, caches, local DBs, and MkDocs site/
# -------------------------------------------------------------------
clean:
	@find . -name "__pycache__" -type d -prune -exec rm -rf {} \; || true
	@rm -rf .pytest_cache .cache .cache_* || true
	@rm -f .cache_history.json || true
	@rm -f data/*.duckdb data/*.duckdb-wal || true
	@rm -rf htmlcov .coverage site || true
	@echo "Clean complete."

# -------------------------------------------------------------------
# More thorough clean: includes venv, packaging artifacts, temp dirs
# -------------------------------------------------------------------
distclean: clean
	@rm -rf $(VENV) || true
	@rm -rf .streamlit || true
	@rm -rf *.tar.gz *.zip || true
	@rm -rf tmp temp || true
	@echo "Dist-clean complete (venv, temp files, archives removed)."

# -------------------------------------------------------------------
# Full reset: distclean + recreate venv + install deps + ingest sample
# -------------------------------------------------------------------
reset: distclean
	@$(PY) -m venv $(VENV)
	@$(ACT); $(PIP) install --upgrade pip
	@$(ACT); $(PIP) install -r requirements.txt
	@$(ACT); $(PY) pipelines/ingest.py --from 2014-07 --to 2014-07
	@echo "Reset complete. Run: make run"

# -------------------------------------------------------------------
# Docs tasks (MkDocs)
# -------------------------------------------------------------------
docs-serve:
	@$(ACT); mkdocs serve

docs-deploy:
	@$(ACT); mkdocs gh-deploy --force
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

SMOKE_VENV    ?= .smoke-venv
SMOKE_TMP     ?= .smoke-tmp
SMOKE_DB      ?= $(SMOKE_TMP)/wspr.duckdb

SMOKE_PY      := $(SMOKE_VENV)/bin/python
SMOKE_PIP     := $(SMOKE_VENV)/bin/pip
SMOKE_CLI     := $(SMOKE_VENV)/bin/wspr-ai-lite
SMOKE_MONTH		?= 2014-07

PKG_NAME      ?= wspr-ai-lite

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
	@$(SMOKE_PY) -c "import duckdb,sys; con=duckdb.connect('$(SMOKE_DB)', read_only=True); cnt=con.execute('SELECT COUNT(*) FROM spots').fetchone()[0]; print(f'[smoke] rows: {cnt}'); sys.exit(0 if cnt>0 else 2)"
	@echo "[smoke] verify: OK"

smoke-ui-check: ## Check UI presence and streamlit availability
	@$(SMOKE_PY) -c "import importlib, pathlib, wspr_ai_lite; p=pathlib.Path(wspr_ai_lite.__file__).with_name('wspr_app.py'); assert p.exists(), f'wspr_app.py missing at {p}'; importlib.import_module('streamlit'); print('[smoke] ui-check: app present & streamlit import OK')"
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
