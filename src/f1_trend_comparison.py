from __future__ import annotations

"""
f1_trend_comparison.py

Trend comparison: full data vs incomplete=False subgroup.

Generates scatter plots with dual regression lines to quantify how filtering
on incomplete=False changes the inferred trend for Codex and Copilot.

Output:
  figures/f1_fig5_codex-incomplete-scatter.png
  figures/f1_fig6_copilot-incomplete-scatter.png
  Regression slope/R^2 summary printed to stdout
"""

import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats

# --- constants -----------------------------------------------------------

ROOT = pathlib.Path(__file__).resolve().parents[1]
INTERMEDIATE = ROOT / "data" / "processed"
OUTPUT = ROOT / "figures"

DPI = 300


# --- helpers -------------------------------------------------------------

def load_enriched(agent: str) -> pd.DataFrame:
    """Load enriched CSV, parse types, keep only rows with incomplete info."""
    path = INTERMEDIATE / f"f1_enriched_{agent}.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["total_count"] = pd.to_numeric(df["total_count"], errors="coerce")
    df["incomplete"] = df["incomplete"].map(
        {True: True, False: False, "True": True, "False": False}
    )
    df_valid = df.dropna(subset=["incomplete", "total_count"]).copy()
    df_valid["incomplete"] = df_valid["incomplete"].astype(bool)
    return df_valid


def fit_regression(df: pd.DataFrame, mask: pd.Series | None = None) -> dict:
    """
    Fit linear regression on total_count vs time (seconds from first point).
    mask: boolean Series to select subset; None means use full df.
    Returns dict with slope_per_day, intercept, r_squared, x_range, y_range.
    """
    sub = df.loc[mask] if mask is not None else df
    t0 = df["timestamp"].min()
    x = (sub["timestamp"] - t0).dt.total_seconds().values
    y = sub["total_count"].values
    slope, intercept, r, _, _ = stats.linregress(x, y)
    slope_per_day = slope * 86400
    r_squared = r ** 2
    # Predict at the time range of the subset (for plotting)
    x_min, x_max = x.min(), x.max()
    y_start = slope * x_min + intercept
    y_end = slope * x_max + intercept
    t_start = t0 + pd.Timedelta(seconds=float(x_min))
    t_end = t0 + pd.Timedelta(seconds=float(x_max))
    return {
        "slope_per_day": slope_per_day,
        "r_squared": r_squared,
        "t_start": t_start,
        "t_end": t_end,
        "y_start": y_start,
        "y_end": y_end,
    }


# --- plot functions -------------------------------------------------------

def plot_scatter_dual_regression(
    df: pd.DataFrame,
    agent_label: str,
    fig_path: pathlib.Path,
    false_note: str | None = None,
    legend_loc: str = "upper left",
    pre_cutoff: str | None = None,
) -> tuple[dict, dict]:
    """
    Time-series scatter colored by incomplete (True=orange, False=green).
    Two regression lines:
      - Black dashed: False-only (spans False group time range)
      - Red dashed:   Full data  (spans full time range)
    Optional blue dashed line: all-data regression restricted to pre-cutoff period.
    Returns (false_reg, full_reg) regression dicts.
    """
    fig, ax = plt.subplots(figsize=(13, 4))

    true_mask = df["incomplete"]
    false_mask = ~df["incomplete"]

    ax.scatter(
        df.loc[true_mask, "timestamp"].values,
        df.loc[true_mask, "total_count"].values,
        s=3, c="#d95f02", alpha=0.6,
        label=f"incomplete=True (n={true_mask.sum():,})",
        zorder=2,
    )
    ax.scatter(
        df.loc[false_mask, "timestamp"].values,
        df.loc[false_mask, "total_count"].values,
        s=3, c="#1b9e77", alpha=0.6,
        label=f"incomplete=False (n={false_mask.sum():,})",
        zorder=2,
    )

    # False-only regression
    false_reg = fit_regression(df, false_mask)
    ax.plot(
        [false_reg["t_start"], false_reg["t_end"]],
        [false_reg["y_start"], false_reg["y_end"]],
        c="black", linewidth=1.5, linestyle="--",
        label=(
            f"False-only fit: slope={false_reg['slope_per_day']:+.1f}/day, "
            f"R^2={false_reg['r_squared']:.3f}"
        ),
        zorder=3,
    )

    # Full-data regression
    full_reg = fit_regression(df)
    ax.plot(
        [full_reg["t_start"], full_reg["t_end"]],
        [full_reg["y_start"], full_reg["y_end"]],
        c="#cc0000", linewidth=1.5, linestyle="--",
        label=(
            f"Full-data fit: slope={full_reg['slope_per_day']:+.1f}/day, "
            f"R^2={full_reg['r_squared']:.3f}"
        ),
        zorder=3,
    )

    # Pre-cutoff all-data regression drawn over same span as False-only line
    if pre_cutoff is not None:
        cutoff_ts = pd.Timestamp(pre_cutoff, tz="UTC")
        pre_mask = df["timestamp"] < cutoff_ts
        pre_sub = df.loc[pre_mask]
        if len(pre_sub) >= 2:
            t0 = df["timestamp"].min()
            x_pre = (pre_sub["timestamp"] - t0).dt.total_seconds().values
            y_pre = pre_sub["total_count"].values
            from scipy import stats as _stats
            slope, intercept, r, _, _ = _stats.linregress(x_pre, y_pre)
            slope_per_day = slope * 86400
            r_sq = r ** 2
            # Draw over same time range as False-only line
            x_start = (false_reg["t_start"] - t0).total_seconds()
            x_end = (false_reg["t_end"] - t0).total_seconds()
            y_start = slope * x_start + intercept
            y_end = slope * x_end + intercept
            ax.plot(
                [false_reg["t_start"], false_reg["t_end"]],
                [y_start, y_end],
                c="#1f78b4", linewidth=1.5, linestyle="--",
                label=(
                    f"Pre-{pre_cutoff[:5]} all-data fit: "
                    f"slope={slope_per_day:+.1f}/day, R^2={r_sq:.3f}"
                ),
                zorder=3,
            )

    title = f"{agent_label}: total_count Over Time by incomplete_results"
    if false_note:
        title += f"\n({false_note})"
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Date")
    ax.set_ylabel("total_count")
    ax.legend(loc=legend_loc, markerscale=3, fontsize=8)
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(fig_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {fig_path.name}")
    return false_reg, full_reg


def print_regression_summary(results: dict) -> None:
    """Print regression slope and R^2 comparison table."""
    print("\n=== Regression Summary: Full vs False-only ===")
    print(
        f"{'Agent':<10} {'Full slope/day':>16} {'Full R^2':>9} "
        f"{'False slope/day':>17} {'False R^2':>10} {'Notes'}"
    )
    print("-" * 85)
    for agent, (false_reg, full_reg, note) in results.items():
        print(
            f"{agent:<10} "
            f"{full_reg['slope_per_day']:>+16.1f} "
            f"{full_reg['r_squared']:>9.3f} "
            f"{false_reg['slope_per_day']:>+17.1f} "
            f"{false_reg['r_squared']:>10.3f} "
            f"  {note}"
        )


# --- main ----------------------------------------------------------------

def main() -> None:
    codex = load_enriched("codex")
    copilot = load_enriched("copilot")

    # fig5: Codex scatter with dual regression lines
    codex_false_reg, codex_full_reg = plot_scatter_dual_regression(
        codex,
        agent_label="Codex",
        fig_path=OUTPUT / "f1_fig5_codex-incomplete-scatter.png",
        false_note=None,
    )

    # fig6: Copilot scatter with dual regression lines
    # False group covers 03-04 to 03-11 only; pre_cutoff adds an early all-data line
    copilot_false_reg, copilot_full_reg = plot_scatter_dual_regression(
        copilot,
        agent_label="Copilot",
        fig_path=OUTPUT / "f1_fig6_copilot-incomplete-scatter.png",
        false_note="False group covers 03-04~03-11 only; regression lines span different time ranges",
        legend_loc="lower left",
        pre_cutoff="2026-03-11",
    )

    # Regression summary table
    results = {
        "Codex": (
            codex_false_reg,
            codex_full_reg,
            "False covers full period",
        ),
        "Copilot": (
            copilot_false_reg,
            copilot_full_reg,
            "False covers 03-04~03-11 only (temporal confound)",
        ),
    }
    print_regression_summary(results)
    print("\nDone.")


if __name__ == "__main__":
    main()
