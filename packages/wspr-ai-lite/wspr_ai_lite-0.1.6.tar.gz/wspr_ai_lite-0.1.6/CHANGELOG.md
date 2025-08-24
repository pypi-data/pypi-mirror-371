# Changelog

All notable changes to **wspr-ai-lite** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.1] - 2025-08-23
### Fixed
- Corrected placement of `from __future__ import annotations` to avoid CI syntax errors.
- Improved docstring coverage and aligned with pre-commit hooks.
- Documentation cleanup in `pyproject.toml` and developer setup.

### Added
- Initial packaging skeleton under `src/wspr_ai_lite/`.
- Trusted Publisher setup for PyPI automated releases via GitHub Actions.

---

## [0.1.0] - 2025-08-23
### Added
- Initial release of **wspr-ai-lite**.
- DuckDB ingest pipeline (`pipelines/ingest.py`).
- Streamlit dashboard (`app/wspr_app.py`).
- Pre-commit hooks, docstring coverage, and CI with pytest.
- MkDocs documentation site (GitHub Pages).
