# 📘 Makefile Guide — wspr-ai-lite

The `Makefile` provides common shortcuts for developers and users of **wspr-ai-lite**.
It helps set up the environment, run the app, ingest data, clean up, and reset the project.

Instead of typing long commands, you can run:

```bash
make <target>
```

Example:
```bash
make setup-dev
make run
```

---

## 🔧 Targets Overview

### `help`
Prints a list of all available targets.

---

### `setup-dev`
Creates a fresh Python virtual environment (`.venv`) and installs all dependencies from `requirements.txt`.

Use this the first time you clone the repo, or after running `make distclean`.

```bash
make setup-dev
```

---

### `venv`
Creates the virtual environment (`.venv`) only, without installing packages.

```bash
make venv
```

---

### `install`
Installs dependencies into an existing `.venv`.
Useful if you updated `requirements.txt`.

```bash
make install
```

---

### `run`
Runs the **Streamlit dashboard**.

```bash
make run
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

### `ingest`
Ingests WSPRNet data into DuckDB.
By default, it pulls July 2014 as a test dataset:

```bash
make ingest
```

This fetches monthly archives (or uses the cache), parses them, and writes to `data/wspr.duckdb`.

---

### `test`
Runs the test suite using `pytest`.
The `PYTHONPATH` is set automatically so `pipelines/` is found.

```bash
make test
```

---

### `clean`
Removes temporary files, caches, test outputs, and local DuckDB databases:

- `__pycache__/`
- `.pytest_cache/`
- `.cache/`, `.cache_history.json`
- `data/*.duckdb` (local DB)
- Coverage reports

```bash
make clean
```

---

### `distclean`
Runs `clean` plus removes **all development artifacts**:

- `.venv/`
- `.streamlit/`
- Temporary archives (`*.tar.gz`, `*.zip`)
- `tmp/`, `temp/`

```bash
make distclean
```

Use this before pushing to GitHub or when you want a completely clean repo.

---

### `reset`
Performs a full **rebuild from scratch**:

1. Runs `distclean`
2. Creates `.venv`
3. Installs dependencies
4. Ingests a sample dataset (2014-07)

```bash
make reset
```

Afterwards, you can launch the app immediately:

```bash
make run
```

---

## 🧑‍💻 Common Workflows

- **First-time setup**
  ```bash
  make setup-dev
  make ingest
  make run
  ```

- **Run tests before pushing**
  ```bash
  make test
  ```

- **Clean your repo before committing/pushing**
  ```bash
  make distclean
  ```

- **Start completely fresh (new venv + sample data)**
  ```bash
  make reset
  ```

---

This Makefile is designed to make development **repeatable, reliable, and fast**.
