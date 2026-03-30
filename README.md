# AI Agent Commit Tracking: Data Quality Analysis

This repository contains the analysis code, data, and report for a short empirical study on the reliability of GitHub Search API `total_count` values when tracking AI coding agent commit activity over time.

## Research Questions

1. How volatile are the collected `total_count` time series, and does volatility differ across agents?
2. Does the `incomplete_results` flag reliably indicate data quality problems, and does filtering on it improve downstream inference?

## Key Findings

- **Volatility scales with query size.** Claude (CV = 0.82) and Copilot (CV = 0.56) are too unstable for raw count interpretation; Codex (CV = 0.19) retains trend-level usefulness.
- **`incomplete_results=True` means different things for different agents.** For Copilot, filtering on `incomplete=False` reverses the inferred trend direction (slope: −22,800 → +11,673/day). For Codex, filtering changes the slope by only −1.2%.
- **The root cause is query scale, not global server load.** True% saturates in staggered order matching each agent's result-set magnitude (Claude first, then Copilot, then Codex), ruling out a shared external event.
- **Two agents are structurally unobserved.** Cursor and Devin show near-zero counts because the collection script uses incorrect search emails, not because of low activity. See `docs/exploratory-commit-identity-audit.md`.

## Repository Structure

```
data/raw/          Raw commit-count CSVs from the collection pipeline
data/processed/    Enriched CSVs with incomplete_results joined by timestamp
docs/              Dataset description and identity audit supplement
figures/           Exported figures referenced in the report
report/            Quarto report source (report-final.qmd) and compiled PDF
src/               Python scripts for data enrichment and figure generation
```

## Scripts

| Script | Description |
|--------|-------------|
| `src/f1_enrich_csv.py` | Joins raw CSVs with `incomplete_results` from JSON snapshots |
| `src/f1_volatility.py` | Descriptive statistics and volatility figures (Fig. 1–3) |
| `src/f1_incomplete_impact.py` | Subgroup analysis and daily ratio panel (Fig. 4, 7) |
| `src/f1_trend_comparison.py` | Dual-regression scatter plots (Fig. 5–6) |

To regenerate figures from the processed data:

```bash
python src/f1_volatility.py
python src/f1_incomplete_impact.py
python src/f1_trend_comparison.py
```

To re-run data enrichment, configure `REPO_DIR` in `src/f1_enrich_csv.py` to point to a local checkout of [ASSERT-KTH/agent-commits](https://github.com/ASSERT-KTH/agent-commits) (which contains the JSON snapshot archive, not included here due to size).

## Report

The compiled PDF is at `report/report-final.pdf`. To re-render from source, install [Quarto](https://quarto.org/) and run from the `report/` directory:

```bash
quarto render report-final.qmd --to pdf
```

## Data Collection

Raw data was collected by [ASSERT-KTH/agent-commits](https://github.com/ASSERT-KTH/agent-commits), which queries the GitHub Search Commits API every 5 minutes for six AI coding agents (Claude, Copilot, Codex, Gemini, Devin, Cursor) using author email identifiers. The collection window covers 2026-03-03 to 2026-03-29 (27 days).
