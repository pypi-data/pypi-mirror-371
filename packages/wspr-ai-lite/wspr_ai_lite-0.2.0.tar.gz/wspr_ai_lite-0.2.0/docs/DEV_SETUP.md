# Developer Setup

## Prereqs
- Python 3.10+
- macOS / Linux / Windows (WSL recommended on Windows)

## Create a venv
```bash
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
```

## Install dependencies
```bash
pip install -r requirements.txt
```

## Run tests
```bash
pytest -q
# or
make test
```

## Lint/Format (optional)
This project keeps it simple — use your editor's formatter. You can add `ruff`/`black` later if you like.
