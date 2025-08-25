# 📚 WSPR AI Lite Documentation

Current version: {{ config.extra.version }} | Build time: {{ build_time() }}

Welcome to the docs for **wspr-ai-lite** — a lightweight WSPR analytics dashboard built with **DuckDB** and **Streamlit**.

# WSPR-AI-Lite Documentation

Welcome to the documentation for **WSPR-AI-Lite** — a lightweight tool for exploring WSPRNet data with **DuckDB** and **Streamlit**.

## Quick Links

- [User Setup](user-setup.md) — Installation & usage guide for end users
- [Developer Setup](developer-setup.md) — Dev environment, testing & contributions
- [Process Release](process-release.md) — Release workflow & PyPI publishing
- [Testing](testing.md) — Unit tests, smoke tests, CI details
- [Troubleshooting](troubleshooting.md) — Common issues & fixes
- [Code of Conduct](https://github.com/KI7MT/wspr-ai-lite/blob/main/CODE_OF_CONDUCT.md)
- [Security Policy](https://github.com/KI7MT/wspr-ai-lite/blob/main/SECURITY.md)

📘 Tip: The navigation menu on the left provides the same structure.

## ✨ About
Explore **Weak Signal Propagation Reporter (WSPR)** data with an easy, local dashboard:

- 📊 SNR distributions & monthly spot trends
- 👂 Top reporters, most-heard TX stations
- 🌍 Geographic spread & distance/DX analysis
- 🔄 QSO-like reciprocal reports
- ⏱ Hourly activity heatmaps & yearly unique counts

Works on **Windows, Linux, macOS** — no heavy server required.

## Build & Serve

Install docs tooling:

```bash
pip install mkdocs mkdocs-material mkdocs-material-extensions
```

Serve locally:

```bash
# if no version is stipulated, the version will fall back to the last --tagged version
mkdocs serve
```

Set a specific Version when bulding
```bash
WSPR_AI_LITE_VERSION=$(python -c "import wspr_ai_lite as m; print(getattr(m,'__version__','dev'))") \
mkdocs serve
```

Deploy to GitHub Pages:

```bash
mkdocs gh-deploy --force
```
