# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-08-24
### Changed
- CLI now displays the program name as `wspr-ai-lite` (instead of `wspr-lite`) in `--version` and help output.
- Updated documentation, usage examples, and CHANGELOG to consistently use `wspr-ai-lite` as the canonical command.
- Retained the `wspr-lite` shim for backward compatibility, which continues to emit a deprecation warning.

## [0.2.0] - 2025-08-24
### Changed
- Default CLI command is now `wspr-ai-lite`.
- Added transitional `wspr-ai-lite` shim with deprecation warning.

### Deprecated
- The `wspr-lite` command will be removed in a future release.


## [0.1.9] - 2025-08-24
### Fixed
- Added missing `import os` in `cli.py` (caused `wspr-ai-lite ui` to crash).
- Ensured module docstring placement is compliant with Python’s `__future__` import rules and pre-commit checks.

### Changed
- `wspr_app.py` is now packaged inside `wspr_ai_lite`, so `wspr-ai-lite ui` works out-of-the-box after `pip install`.
- CLI `ui` subcommand now correctly resolves the installed app path instead of referencing `app/wspr_app.py`.

### Notes
- Users can now launch the dashboard with:
  ```bash
  wspr-ai-lite ui --db ~/wspr-data/wspr.duckdb --port 8501


## [0.1.7] - 2025-08-23
### Fixed
- Fixed `wspr-ai-lite ingest` failures when running from the PyPI package:
- Removed dependency on repo-local `pipelines/` (ingest is now fully self-contained in the package).
- Corrected timestamp handling: UTC → naive UTC for DuckDB.
- Fixed DuckDB insert by using `con.register()` for DataFrame ingestion.
- Added Change log to site documents

### Changed
- Internal refactoring of ingest for better portability and reproducibility across platforms.

## [0.1.6] - 2025-08-23
### Added
- Initial PyPI release of `wspr-ai-lite`.
- CLI: `wspr-ai-lite ingest` for pulling and storing WSPRNet monthly archives into DuckDB.
- CLI: `wspr-ai-lite ui` for launching the Streamlit dashboard.
- Documentation site via MkDocs + Material theme.
- Pre-commit hooks and CI workflows for linting, testing, and publishing.

---

## [0.1.6] - 2025-08-23
### Fixed
- CI/CD release workflow using PyPI Trusted Publishing
- YAML syntax issues in `.github/workflows/release.yml`
- Unified single-source versioning via `__version__` in `src/wspr_ai_lite/__init__.py`

---

## [0.1.5] - 2025-08-22
### Added
- Initial PyPI publishing workflow with GitHub Actions
- Automatic version verification between Git tag and package version

---

## [0.1.0] - 2025-08-20
### Added
- First public release of `wspr-ai-lite`
- Ingest pipeline for WSPR CSV → DuckDB
- Streamlit dashboard for:
  - 📊 SNR distributions & monthly spot trends
  - 👂 Top reporters, most-heard TX stations
  - 🌍 Geographic spread & distance/DX analysis
  - 🔄 QSO-like reciprocal reports
  - ⏱ Hourly activity heatmaps & yearly unique counts
- Full developer docs with MkDocs + Material
- Pre-commit hooks & interrogate for docstring coverage
