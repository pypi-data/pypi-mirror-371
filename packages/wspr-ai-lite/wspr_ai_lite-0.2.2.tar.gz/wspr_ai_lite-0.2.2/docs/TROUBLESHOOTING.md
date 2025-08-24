# Troubleshooting

## "Database not found" in Streamlit
Run ingest first:
```bash
python pipelines/ingest.py --from 2014-07 --to 2014-07
```

## Ingest is slow or re-downloads
- Use the `--cache-dir` (default `.cache`). Files are reused if present.
- Clean all cached locations you ever used:
```bash
python pipelines/ingest.py --clean-cache
```

## No data appears for a year/band
- You may not have ingested that year/month or that band had no activity.
- Try a different year/band pair that you know has data.

## Distance shows "No valid grid pairs"
- Some rows lack `tx_grid` or `reporter_grid` — distance can't be computed.
- Ingest more months or check another band/year.

## Windows + Python
Prefer WSL or ensure you have a proper Python environment (not MS Store).
