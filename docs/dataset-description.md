# Dataset Description

## data/raw/

The `data/raw/` directory contains six raw commit-count CSV files, one per tracked agent, collected by the `collect-data.sh` script in [ASSERT-KTH/agent-commits](https://github.com/ASSERT-KTH/agent-commits). Each file has two columns with no header: sample timestamp and the `total_count` returned by the GitHub Search Commits API at that time. These are the direct input to `src/f1_enrich_csv.py`.

## data/processed/

The `data/processed/` directory contains six enriched CSV files produced by `src/f1_enrich_csv.py`. Each file includes:

- `timestamp`: sample time in ISO 8601 format
- `total_count`: commit count returned by the GitHub Search API
- `incomplete`: whether the matched API snapshot reported `incomplete_results` (True / False / empty if no JSON match)

These files are the input to the three analysis scripts and reproduce all figures and statistics in the report without re-running the enrichment step.

## Notes

Two limitations are especially important. First, missing or saturated API responses can make `total_count` unstable, particularly for large result sets. Second, some agent identities are imperfectly captured by the underlying collection design, which means that apparently small counts may reflect query mismatch rather than genuinely low activity. See `docs/exploratory-commit-identity-audit.md` for details.

The JSON snapshot archive (21,000+ files, required to re-run `f1_enrich_csv.py`) is not included in this repository due to size. It is available in the source collection at [ASSERT-KTH/agent-commits](https://github.com/ASSERT-KTH/agent-commits).
