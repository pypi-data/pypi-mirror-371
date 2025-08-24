# 📚 WSPR AI Lite Documentation

Welcome to the docs for **wspr-ai-lite** — a lightweight WSPR analytics dashboard built with **DuckDB** and **Streamlit**.

## 🚀 Quick Links
- **User Setup & Usage** → See [README](README.md)
- **Developer Setup** → See [DEV_SETUP](dev_setup.md)
- **Makefile Guide** → See [MAKEFILE](makefile.md)
- **Testing** → See [TESTING](testing.md)
- **Troubleshooting** → See [TROUBLESHOOTING](troubleshooting.md)
- **Change Log** → See [CHANGELOG](CHANGELOG.md)

## ✨ About
Explore **Weak Signal Propagation Reporter (WSPR)** data with an easy, local dashboard:

- 📊 SNR distributions & monthly spot trends
- 👂 Top reporters, most-heard TX stations
- 🌍 Geographic spread & distance/DX analysis
- 🔄 QSO-like reciprocal reports
- ⏱ Hourly activity heatmaps & yearly unique counts

Works on **Windows, Linux, macOS** — no heavy server required.

## 🛠 Build & Serve

Install docs tooling:

```bash
pip install mkdocs mkdocs-material mkdocs-material-extensions
```

Serve locally:

```bash
mkdocs serve
```

Deploy to GitHub Pages:

```bash
mkdocs gh-deploy --force
```
