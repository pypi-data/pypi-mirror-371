# 📡 wspr-ai-lite

**Lightweight WSPR analytics rendering tool employing DuckDB + Streamlit**

Designed to be portable, and lightweight, `wspr-ai-lite` can be run on RasperyPI's or Enterprise Servers.
The portability of Python makes it OS agnostic. The only limiting factor is disk space. The more archives you elect to add, the larger the diskspace footprint becomes. In future releases, we provide resource utilization stats for CPU, RAM an storage.

## Resources

[![Made with Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-FF4B4B)](https://streamlit.io/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB-blue)](https://duckdb.org/)
[![Docs](https://img.shields.io/badge/docs-github_pages-blue)](https://KI7MT.github.io/wspr-ai-lite/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Workflows and Packaging Status
![GH tag](https://img.shields.io/github/v/tag/KI7MT/wspr-ai-lite?sort=semver)
[![GH release](https://img.shields.io/github/v/release/KI7MT/wspr-ai-lite)](https://github.com/KI7MT/wspr-ai-lite/releases)
[![CI](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/ci.yml/badge.svg)](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/ci.yml)
[![pre-commit](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/pre-commit.yml)
[![PyPI version](https://img.shields.io/pypi/v/wspr-ai-lite.svg)](https://pypi.org/project/wspr-ai-lite/)
[![Python versions](https://img.shields.io/pypi/pyversions/wspr-ai-lite.svg)](https://pypi.org/project/wspr-ai-lite/)
[![Publish](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/release.yml/badge.svg)](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/release.yml)
[![smoke](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/smoke.yml/badge.svg)](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/smoke.yml)

## Get Help
- **Report a bug** → [New Bug Report](https://github.com/KI7MT/wspr-ai-lite/issues/new?template=bug_report.yml)
- **Request a feature** → [New Feature Request](https://github.com/KI7MT/wspr-ai-lite/issues/new?template=feature_request.yml)
- **Ask a question / share ideas** → [GitHub Discussions](https://github.com/KI7MT/wspr-ai-lite/discussions)
- **Read the docs** → https://ki7mt.github.io/wspr-ai-lite/

## What Can You Do With It

Explore **Weak Signal Propagation Reporter (WSPR)** data with an easy, local dashboard:

- 📊 SNR distributions & monthly spot trends
- 👂 Top reporters, most-heard TX stations
- 🌍 Geographic spread & distance/DX analysis
- 🔄 QSO-like reciprocal reports
- ⏱ Hourly activity heatmaps & yearly unique counts
- 🚀 Works on **Windows, Linux, macOS** — no heavy server required.

## ✨ Key Features
- Local DuckDB storage with efficient ingest + caching
- Streamlit UI for interactive exploration
- Distance/DX analysis with Maidenhead grid conversion
- QSO-like reciprocal finder with configurable time window

### Fast Performance
- Columnar Storage: DuckDB is a columnar database, which allows for better data compression and faster query execution.
- Vectorization: proceses data in batches. optimized CPU usage, significantly faster than traditional OLTP databases.

### Ease of Use
- Simple Installation: DuckDB can be installed with just a few lines of code, and on any platform.
- In-Process Operation: It runs within as a host application, eliminating network latency and simplifying data access.

## Quickstart (Recommended: PyPI)

### 1. Install from PyPI
```bash
# optional but recommended: create a virtualenv first
python3 -m venv .venv && source .venv/bin/activate
pip install wspr-ai-lite
```

### 2. Ingest Data
Fetch WSPRNet monthly archives and load them into DuckDB:

```bash
# adjust the range as needed, but be reasonable!
wspr-ai-lite ingest --from 2014-07 --to 2014-07 --db data/wspr.duckdb
```
- Downloads compressed monthly CSVs (caches locally in .cache/)
- Normalizes into data/wspr.duckdb
- Adds extra fields (band, reporter grid, tx grid)

### 3. Launch the Dashboard
```bash
wspr-ai-lite ui --db data/wspr.duckdb --port 8501
```
Open http://localhost:8501 in your browser 🎉

👉 For developers who want to hack on the code directly, see [Developer Setup](https://ki7mt.github.io/wspr-ai-lite/DEV_SETUP/).


## Example Visualizations
- SNR Distribution by Count
- Monthly Spot Counts
- Top Reporting Stations
- Most Heard TX Stations
- Geographic Spread (Unique Grids)
- Distance Distribution + Longest DX
- Best DX per Band
- Activity by Hour × Month
- TX/RX Balance and QSO Success Rate

## Development

For contributors and developers:
- docs/dev-setup.md --> Development setup guide
- docs/testing.md --> Testing instructions (pytest + Makefile)
- docs/troubleshooting.md --> Common issues & fixes

```bash
make setup-dev   # create venv and install deps
make ingest      # run ingest pipeline
make run         # launch Streamlit UI
make test        # run pytest suite
```

### Testing
Run unit tests for ingest and utilities:

### Makefile Usage

There is an extensive list of Makefile targets that simplify operations. See `make help` for a full list of available targets.

```bash
make help

# sample output

Available Make Targets
-------------------------------------------------------------------------------
build                Build PyPi Pyjon Package
clean                Clean temporary files, caches, local DBs, and MkDocs site/
dist-clean-all       Deep clean + remove smoke artifacts
distclean            More thorough clean: includes venv, packaging artifacts, temp dirs
docs-deploy          Deplot docs to hh-pages
docs-serve           Docs tasks (MkDocs)
ingest               Ingest a sample month (2014-07)
install-dev          Install dev dependencies (requirements-dev.txt)
install              Install runtime dependencies (requirements.txt)
lint-docs            Docstring checks: coverage (interrogate) + style (pydocstyle)
precommit-install    Install git pre-commit hooks
publish-test         Pulublish Package to PyPi Test Repository
publish              Pulublish Package to PyPi Production Repository
reset                Full reset: distclean + recreate venv + install deps + ingest sample
run                  Run Streamlit UI
setup-dev            Create venv, install dev deps, install pre-commit hooks
smoke-build          Build wheel+sdist for smoke test
smoke-clean          Remove smoke-test artifacts (venv + tmp DB)
smoke-ingest         Ingest a single month into a temporary DuckDB
smoke-install        Create isolated smoke venv and install the built wheel
smoke-test-pypi      Install from PyPI and run verify+ui-check
smoke-test           Full end-to-end smoke test
smoke-ui-check       Check UI presence and streamlit availability
smoke-verify         Verify the DuckDB contains rows
test                  Run pytest
venv                 Create Python virtual environment (.venv)
```

## Acknowledgements
- WSPRNet community for providing global weak-signal data
- Joe Taylor, K1JT, and the WSJT-X Development Team
- Contributors to DuckDB and Streamlit
- Amateur radio operators worldwide who share spots and keep the network alive

## Contributing
Pull requests are welcome!
If you have feature ideas (e.g., new metrics, visualizations, or AI integrations), open an issue first to discuss.

## Roadmap
- **Phase 1**: wspr-ai-lite (this project)
  - Lightweight, local-only DuckDB + Streamlit dashboard
- **Phase 2**: wspr-ai-analytics ( modernize [wspr-analytics](https://github.com/KI7MT/wspr-analytics) project )
  - Full analytics suite with ClickHouse, Grafana, AI Agents, and MCP integration
  - Designed for heavier infrastructure and richer analysis

## Code of Conduct
Please review [Code of Conduct](https://github.com/KI7MT/wspr-ai-lite/blob/main/CODE_OF_CONDUCT.md) decliration.

## Security
Please review our [Security Policy](https://github.com/KI7MT/wspr-ai-lite/blob/main/SECURITY.md).

## 📜 License
This project is licensed under the MIT License. Open and free for amateur radio and research use.
