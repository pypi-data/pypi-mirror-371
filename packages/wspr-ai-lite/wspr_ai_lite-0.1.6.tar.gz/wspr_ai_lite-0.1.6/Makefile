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
help:
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
