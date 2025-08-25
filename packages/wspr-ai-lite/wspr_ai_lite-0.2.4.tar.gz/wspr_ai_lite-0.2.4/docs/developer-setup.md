# Developer Setup — wspr-ai-lite

This guide documents **developer workflows** for wspr-ai-lite using the new **`src/`** layout and the **`wspr-ai-lite`** CLI entrypoint.

- Works on macOS, Linux, WSL2/Windows
- Uses a local virtualenv
- Makefile targets are “sugar” over the CLI so dev & user paths match

## 1) Prerequisites

- Python **3.11+** (project tests & CI run on 3.11; smoke also covers 3.13)
- `git`, `make`
- (Recommended) `pre-commit` installed: `pip install pre-commit`

## 2) Clone & bootstrap

```bash
git clone git@github.com:KI7MT/wspr-ai-lite.git
cd wspr-ai-lite

# Optional virtualenv
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dev requirements
pip install -r requirements.txt

# Install pre-commit hooks (formatting, YAML check, docstrings, etc.)
pre-commit install

# See available Make targets
make help
```
> Tip: all Make targets have inline ## descriptions and appear in make help automatically.

## 3) Run the UI (dev)

The UI should always be launched via the CLI, not streamlit run (path-independent and matches PyPI behavior).

```bash
# default DB path: data/wspr.duckdb
make run

# or with custom DB file:
make run DB=~/wspr-data/wspr.duckdb
```

This calls:

```bash
wspr-ai-lite ui --db <DB> --port 8501
```

Open http://localhost:8501

## 4) Ingest data (dev)

Use the packaged CLI subcommand:

```bash
# Example: load a single month
wspr-ai-lite ingest --from 2014-07 --to 2014-07 --db data/wspr.duckdb

# Cache dir defaults to .cache/; can be overridden:
wspr-ai-lite ingest --from 2014-07 --to 2014-07 --db data/wspr.duckdb --cache .cache
```

Behavior:
- downloads compressed CSVs to cache
- parses/normalizes into DuckDB
- computes derived columns (band, reporter grid, tx grid, etc.)

## 5) Tests
Run unit tests and style checks:

```bash
make test            # pytest
pre-commit run -a    # run all configured hooks (YAML, whitespace, docstrings, etc.)
```

Common pytest conveniences:
```bash
pytest -q
pytest tests/test_ingest.py::test_parse_month_csv -q
pytest -k "ingest and not io" -q
```

## 6) Smoke tests (local wheel + PyPI)

### 6.1 Source smoke (local wheel)

End-to-end smoke using your working tree:
```bash
make smoke-test
```
What it does:
- builds wheel+sdist
- installs in a temp venv
- ingests a small month
- verifies row count
- checks Streamlit presence

You can also run steps individually:

```bash
make smoke-clean
make smoke-build
make smoke-install
make smoke-ingest
make smoke-verify
make smoke-ui-check
```

### 6.2 PyPI smoke
Validate a tagged PyPI version installs and runs:
```bash
make smoke-test-pypi VERSION=0.2.2
```

This creates a temp venv, installs from PyPI, ingests, verifies, and checks the app file inside the installed package.

## 7) Build & release (manual)

CI/CD handles real PyPI publishing on tags. Use the Release Process doc for the full flow.

Local build:
```bash
python -m build
```
This produces dist/wspr_ai_lite-<ver>-py3-none-any.whl and a matching sdist.

Tag & push to trigger CI publish (trusted publishing must be configured on PyPI):
```bash
git commit -am "release: vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

CI will:
- build the package
- publish to PyPI (if tag)
- run smoke tests (source & PyPI)

## 8) Pre-commit

Run all hooks locally before pushing:

```bash
pre-commit autoupdate
pre-commit run -a
```

Docstring coverage is enforced via interrogate. If the hook fails, add module/function docstrings or adjust thresholds in pyproject.toml (not recommended unless intentional).

## 9) Troubleshooting

Module docstring shows up in UI
- Ensure nothing renders __doc__ (e.g., st.markdown(__doc__)). Use a sidebar help expander instead.

DB cannot be opened / empty UI

- Confirm the DB used by UI matches where you ingested:
```bash
wspr-ai-lite ui --db data/wspr.duckdb
```

Make errors about tabs
- Make requires TABs for command lines under targets. Replace leading spaces wih a TAB.

CI: invalid-publisher (PyPI)
- Verify PyPI Trusted Publisher matches repo/workflow and that the tag pushed is vX.Y.Z.

Streamlit app missing on PyPI smoke
- Ensure the app file is inside the package (we ship wspr_ai_lite.py next to __init__.py).
- The CLI locates it via _app_path(); do not hardcode app/wspr_app.py anywhere.

## 10) Make targets (common)
```bash
# common
help                Show Makefile targets (auto-generated)
run                 Launch the Streamlit dashboard (wspr-ai-lite ui)
test                Run unit tests (pytest)
build               Build wheel+sdist for PyPI

# smoke
smoke-test          Full end-to-end smoke test
smoke-clean         Remove smoke-test artifacts (venv + tmp DB)
smoke-build         Build wheel+sdist for smoke
smoke-install       Create isolated smoke venv and install wheel
smoke-ingest        Ingest a sample month into temp DuckDB
smoke-verify        Verify the DuckDB contains rows
smoke-ui-check      Check UI presence and streamlit availability
smoke-test-pypi     Install VERSION from PyPI and run smoke
```
> See the Makefile for the authoritative list (make help).

## 11) Conventions
- Prefer CLI (wspr-ai-lite) over raw file paths
- Keep Streamlit logic in the packaged module
- Tests should not hit the network unless explicitly marked
- Cache downloads under .cache/ and keep .cache_history.json out of git
