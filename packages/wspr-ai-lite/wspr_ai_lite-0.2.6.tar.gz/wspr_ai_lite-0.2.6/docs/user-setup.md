# User Setup & Usage

This page mirrors the core usage instructions from the project README so it renders in the MkDocs site.

## Quickstart

1. **Create a virtual environment (optional but recommended)**
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ingest a sample month (e.g., July 2014)**
   ```bash
   python pipelines/ingest.py --from 2014-07 --to 2014-07
   ```

4. **Run the Streamlit UI**
   ```bash
   streamlit run app/wspr_app.py
   ```
   Open http://localhost:8501 in your browser.

## Notes

- Data is stored locally in `data/wspr.duckdb`.
- The ingest script caches downloads and can clean caches with `--clean-cache`.
- See the Makefile for shortcuts:
  ```bash
  make setup-dev   # create venv + install deps
  make ingest      # ingest sample month
  make run         # run Streamlit UI
  make test        # run pytest suite
  ```

For more details, refer to the repository README on GitHub.
