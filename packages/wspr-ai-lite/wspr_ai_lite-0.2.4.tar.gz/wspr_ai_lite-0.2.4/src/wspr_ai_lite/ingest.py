from __future__ import annotations

"""Ingest utilities for wspr-ai-lite (packaged version).

This module is self-contained so the PyPI-installed CLI works without relying
on the repo-local `pipelines/ingest.py`.

Functions provided:
- month_range(start, end): iterate (year, month) inclusive for YYYY-MM inputs
- archive_url(year, month): WSPRNet monthly CSV.GZ URL
- download_month(year, month, cache_dir): returns raw bytes (cached)
- band_from_freq_mhz(freq_mhz): map float MHz → WSPR band label
- ingest_month(con, year, month, cache_dir): parse & insert into DuckDB
"""

from datetime import datetime
from pathlib import Path
from typing import Generator, Tuple

import gzip
import io

import duckdb
import pandas as pd
import requests


# ----------------------------
# Helpers & core functionality
# ----------------------------

def month_range(start: str, end: str) -> Generator[Tuple[int, int], None, None]:
    """Yield (year, month) pairs inclusive between YYYY-MM strings."""
    sy, sm = (int(start[0:4]), int(start[5:7]))
    ey, em = (int(end[0:4]), int(end[5:7]))
    y, m = sy, sm
    while (y < ey) or (y == ey and m <= em):
        yield y, m
        m += 1
        if m > 12:
            y += 1
            m = 1


def archive_url(year: int, month: int) -> str:
    """Return the wsprnet.org monthly archive URL for a given year-month."""
    return f"https://wsprnet.org/archive/wsprspots-{year:04d}-{month:02d}.csv.gz"


def _cache_path(cache_dir: Path, year: int, month: int) -> Path:
    """Make the download cache directory if it doe not exist."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"wsprspots-{year:04d}-{month:02d}.csv.gz"


def download_month(year: int, month: int, cache_dir: str | Path = ".cache") -> bytes:
    """Download a monthly CSV.GZ into cache and return raw bytes (from cache if present)."""
    cache_dir = Path(cache_dir)
    path = _cache_path(cache_dir, year, month)
    if path.exists():
        return path.read_bytes()
    url = archive_url(year, month)
    print(f"GET {url}")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    return r.content


def band_from_freq_mhz(freq_mhz: float) -> str:
    """Map a frequency in MHz to a WSPR band label.

    Uses common center/range approximations for WSPR segments.
    """
    f = float(freq_mhz)
    # Simplified ranges that work well for historical archives.
    bands = [
        (0.136, 0.139, "2200m"),
        (0.472, 0.479, "630m"),
        (1.8,   2.0,   "160m"),
        (3.5,   4.0,   "80m"),
        (5.0,   6.0,   "60m"),
        (7.0,   7.3,   "40m"),
        (10.0,  10.2,  "30m"),
        (14.0,  14.35, "20m"),
        (18.068,18.168,"17m"),
        (21.0,  21.45, "15m"),
        (24.89, 24.99, "12m"),
        (28.0,  29.7,  "10m"),
        (50.0,  54.0,  "6m"),
        (70.0,  71.0,  "4m"),
        (144.0, 148.0, "2m"),
        (220.0, 225.0, "1.25m"),
        (432.0, 438.0, "70cm"),
        (1240.0,1300.0,"23cm"),
    ]
    for lo, hi, label in bands:
        if lo <= f <= hi:
            return label
    return "unknown"


def _parse_month_csv(raw_gz: bytes) -> pd.DataFrame:
    """Parse a wsprspots-YYYY-MM.csv.gz blob into a normalized DataFrame.

    The monthly archives do not include headers. A typical row (15 cols) seen historically:
      0: spot_id
      1: unixtime (seconds)
      2: txcall
      3: tx_grid
      4: snr
      5: freq_mhz
      6: reporter
      7: reporter_grid
      (additional trailing columns may exist; we ignore them)

    We robustly pick the columns by position and ignore extra ones.
    """
    # Decompress
    buf = io.BytesIO(gzip.decompress(raw_gz))
    # Read only the columns we need; tolerate extra cols.
    df = pd.read_csv(
        buf,
        header=None,
        usecols=[1, 2, 3, 4, 5, 6, 7],
        names=["unixtime", "txcall", "tx_grid", "snr", "freq", "reporter", "reporter_grid"],
        dtype={
            "unixtime": "Int64",
            "txcall": "string",
            "tx_grid": "string",
            "snr": "Int64",
            "freq": "float64",
            "reporter": "string",
            "reporter_grid": "string",
        },
        low_memory=False,
    )

    # Timestamp & calendar fields
    ts_aware = pd.to_datetime(df["unixtime"], unit="s", utc=True)
    ts = ts_aware.dt.tz_localize(None)
    out = pd.DataFrame(
        {
            "ts": ts,
            "band": df["freq"].map(band_from_freq_mhz),
            "freq": df["freq"].astype("float64"),
            "snr": df["snr"].astype("Int64"),
            "reporter": df["reporter"].astype("string"),
            "reporter_grid": df["reporter_grid"].astype("string"),
            "txcall": df["txcall"].astype("string"),
            "tx_grid": df["tx_grid"].astype("string"),
            "year": ts.dt.year.astype("int32"),
            "month": ts.dt.month.astype("int16"),
        }
    )
    # Drop obvious null rows (rare, but keeps DB clean)
    out = out.dropna(subset=["ts", "freq", "snr"])
    # SNR can be nullable Int; cast to Python int for DuckDB
    out["snr"] = out["snr"].astype("int32")
    return out


def _ensure_table(con: duckdb.DuckDBPyConnection) -> None:
    """Create the 'spots' table if it does not exist."""
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS spots (
            ts TIMESTAMP,
            band VARCHAR,
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


def ingest_month(
    con: duckdb.DuckDBPyConnection,
    year: int,
    month: int,
    cache_dir: str | Path = ".cache",
) -> int:
    """Download, parse, and insert one month's spots into DuckDB.

    Returns the number of rows inserted.
    """
    raw = download_month(year, month, cache_dir)
    df = _parse_month_csv(raw)
    _ensure_table(con)

    # ensure the data types are what DuckDB expects before insertion
    df = df.astype({
        "ts": "datetime64[ns]",
        "band": "string",
        "freq": "float64",
        "snr": "int32",
        "reporter": "string",
        "reporter_grid": "string",
        "txcall": "string",
        "tx_grid": "string",
        "year": "int32",
        "month": "int16",
    })

    # Insert via DuckDB's dataframe ingestion
    con.register("df", df)  # expose pandas DataFrame as a DuckDB view
    con.execute("INSERT INTO spots SELECT * FROM df")
    con.unregister("df")

    print(f"[OK] {year:04d}-{month:02d} ({len(df):,} rows)")
    return int(len(df))
