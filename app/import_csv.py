# app/import_csv.py
"""
Smart CSV → SQLite/Postgres loader
----------------------------------
USAGE examples
    # simplest: auto-detect encoding, append rows
    python -m app.import_csv data/areaRealEstateAnalysis.csv \
           --table real_estate_mock

    # same, but replace the table each time
    python -m app.import_csv data/new_dump.csv \
           --table sales_raw --mode replace

    # try utf-16, but fall back to latin-1 if it fails
    python -m app.import_csv data/weird.csv \
           --table messy --encoding utf-16 --fallback latin-1

CLI options
    --table      (str)   target table name (required)
    --mode       (str)   append | replace  (default append)
    --encoding   (str)   preferred encoding (default utf-8)
    --fallback   (str)   second-try encoding if the first fails
    --clean              strip col-names, drop dup rows, coerce dtypes
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from app.settings import DB_URL  # Replace with your actual database URL

# ── helpers ───────────────────────────────────────────────────────────────────
def read_csv_smart(path: Path, enc_primary: str, enc_fallback: str | None):
    """Try primary encoding; if it fails, fall back and warn."""
    try:
        return pd.read_csv(path, encoding=enc_primary)
    except UnicodeDecodeError as e:
        if not enc_fallback:
            raise
        print(f"[warn] {e}\n[warn] retrying with --fallback={enc_fallback}")
        return pd.read_csv(path, encoding=enc_fallback)

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Light, opinionated clean-up: snake-case cols, drop dup rows, trim."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
                  .str.replace(r"[^\w]", "", regex=True)
    )
    df = df.drop_duplicates().convert_dtypes()
    return df

# ── main ─────────────────────────────────────────────────────────────────────
def main(args):
    df = read_csv_smart(args.csv_path, args.encoding, args.fallback)
    if args.clean:
        df = clean_df(df)

    engine = create_engine(DB_URL, future=True)
    mode = "replace" if args.mode == "replace" else "append"

    print(
        f"Inserting {len(df):,} rows into '{args.table}' "
        f"({mode}, db={engine.url.database}) …"
    )
    try:
        df.to_sql(args.table, engine, if_exists=mode, index=False)
    except SQLAlchemyError as e:
        print("[error]", e)
        sys.exit(1)

    print("✓ done")

# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("csv_path", type=Path, help="Path to CSV file")
    p.add_argument("--table", required=True, help="DB table name")
    p.add_argument("--mode", choices=["append", "replace"], default="append")
    p.add_argument("--encoding", default="utf-8", help="Primary encoding")
    p.add_argument("--fallback", default="latin-1", help="Fallback encoding")
    p.add_argument("--clean", action="store_true", help="Run basic data cleanup")
    main(p.parse_args())