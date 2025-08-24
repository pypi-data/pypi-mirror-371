from __future__ import annotations

"""Console entrypoint for wspr-ai-lite.

Provides two subcommands:

- `ingest`: Download monthly WSPRNet archives and insert into DuckDB.
- `ui`:     Launch the Streamlit dashboard that reads from the DuckDB file.

Usage examples:
    wspr-ai-lite ingest --from 2014-07 --to 2014-07 --db ~/wspr-data/wspr.duckdb
    WSPR_DB_PATH=~/wspr-data/wspr.duckdb wspr-ai-lite ui --port 8501
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import duckdb

from . import __version__
from .ingest import ingest_month, month_range


def _app_path() -> Path:
    """
    Resolve the Streamlit app path.

    Order:
    1) Packaged location (installed wheel): alongside this cli.py in wspr_ai_lite/.
    2) Dev fallback (repo checkout): ../../app/wspr_app.py relative to this file.
    """
    # 1) packaged: wspr_ai_lite/wspr_app.py (same folder as cli.py)
    packaged = Path(__file__).with_name("wspr_app.py")
    if packaged.exists():
        return packaged

    # 2) dev fallback: repo-root/app/wspr_app.py
    repo_fallback = Path(__file__).resolve().parents[2] / "app" / "wspr_app.py"
    return repo_fallback

def deprecated_entrypoint() -> None:
    """Temporary shim for the old `wspr-ai-lite` command name.

    Prints a deprecation warning and then calls main().
    """
    print(
        "WARNING: The `wspr-ai-lite` command conflicts with the official WSPR suite.\n"
        "Please use the new command: `wspr-ai-lite`.\n",
        flush=True,
    )
    main()

def main() -> None:
    """Dispatch subcommands: `ingest` and `ui`."""
    parser = argparse.ArgumentParser(prog="wspr-ai-lite", description="WSPR AI Lite Utilities")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest", help="Ingest one or more months into DuckDB")
    p_ing.add_argument("--from", dest="start", required=True, help="YYYY-MM")
    p_ing.add_argument("--to", dest="end", required=True, help="YYYY-MM")
    p_ing.add_argument("--db", default="data/wspr.duckdb", help="DuckDB path (default: data/wspr.duckdb)")
    p_ing.add_argument("--cache", default=".cache", help="Download cache dir (default: .cache)")

    p_ui = sub.add_parser("ui", help="Run Streamlit UI")
    p_ui.add_argument("--db", default="data/wspr.duckdb", help="DuckDB path (default: data/wspr.duckdb)")
    p_ui.add_argument("--port", type=int, default=8501, help="Streamlit port (default: 8501)")

    args = parser.parse_args()

    if args.cmd == "ingest":
        Path(args.db).parent.mkdir(parents=True, exist_ok=True)
        con = duckdb.connect(args.db)
        total = 0
        for y, m in month_range(args.start, args.end):
            total += ingest_month(con, y, m, args.cache)
        print(f"[OK] inserted rows: {total}")
        return

    if args.cmd == "ui":
        app_path = _app_path()
        if not app_path.exists():
            print(
                f"ERROR: Cannot find Streamlit app at {app_path}\n"
                "This likely means the package app file was not included in the install.",
                file=sys.stderr,
            )
            sys.exit(1)

        env = os.environ.copy()
        if args.db:
            env["WSPR_DB_PATH"] = args.db

        try:
            code = subprocess.call(
                [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(args.port)],
                env=env,
            )
        except ModuleNotFoundError:
            print(
                "ERROR: Streamlit is not installed in this environment.\n"
                "Install it with:\n\n    pip install streamlit\n",
                file=sys.stderr,
            )
            sys.exit(1)

        sys.exit(code)


if __name__ == "__main__":
    main()
