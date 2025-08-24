from __future__ import annotations

"""Console entrypoint for wspr-ai-lite."""

import argparse
import subprocess
import sys
from pathlib import Path

from . import __version__
from .ingest import ingest_month, month_range
import duckdb

def main() -> None:
    """Dispatch subcommands: ingest and ui."""
    p = argparse.ArgumentParser(prog="wspr-lite", description="WSPR AI Lite utilities")
    p.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest", help="Ingest one or more months into DuckDB")
    p_ing.add_argument("--from", dest="start", required=True, help="YYYY-MM")
    p_ing.add_argument("--to", dest="end", required=True, help="YYYY-MM")
    p_ing.add_argument("--db", default="data/wspr.duckdb", help="DuckDB path (default: data/wspr.duckdb)")
    p_ing.add_argument("--cache", default=".cache", help="Download cache dir (default: .cache)")

    p_ui = sub.add_parser("ui", help="Run Streamlit UI")
    p_ui.add_argument("--db", default="data/wspr.duckdb", help="DuckDB path (default: data/wspr.duckdb)")
    p_ui.add_argument("--port", type=int, default=8501, help="Streamlit port (default: 8501)")

    args = p.parse_args()

    if args.cmd == "ingest":
        Path(args.db).parent.mkdir(parents=True, exist_ok=True)
        con = duckdb.connect(args.db)
        total = 0
        for y, m in month_range(args.start, args.end):
            total += ingest_month(con, y, m, args.cache)
        print(f"[OK] inserted rows: {total}")
        return

    if args.cmd == "ui":
        # Just delegate to Streamlit but pass DB path through env
        env = dict(**os.environ, WSPR_DB_PATH=args.db)
        code = subprocess.call(
            [sys.executable, "-m", "streamlit", "run", "app/wspr_app.py", "--server.port", str(args.port)],
            env=env,
        )
        sys.exit(code)

if __name__ == "__main__":
    main()
