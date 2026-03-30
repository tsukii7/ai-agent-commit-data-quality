from __future__ import annotations

"""
f1_incomplete_impact.py

Impact of incomplete_results on data quality.

Analyses:
  1. True/False proportion summary per agent (printed)
  2. Box plot: True vs False total_count distribution for Copilot and Codex (fig4)
     Claude excluded: False group has only 5 samples, insufficient for comparison
  3. CV comparison: full vs False-only subset (printed for Copilot/Codex; descriptive for Claude)
  4. Daily incomplete=True ratio panel with sample-count overlay (fig7)
"""

import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- constants -----------------------------------------------------------

ROOT = pathlib.Path(__file__).resolve().parents[1]
INTERMEDIATE = ROOT / "data" / "processed"
OUTPUT = ROOT / "figures"

# Ordered by total_count magnitude (descending)
AGENTS = ["claude", "copilot", "codex"]
AGENT_LABELS = {"claude": "Claude", "copilot": "Copilot", "codex": "Codex"}

DPI = 300


# --- helpers -------------------------------------------------------------

def load_enriched(agent: str) -> pd.DataFrame:
    """Load enriched CSV, parse types, drop rows without incomplete info."""
    path = INTERMEDIATE / f"f1_enriched_{agent}.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["total_count"] = pd.to_numeric(df["total_count"], errors="coerce")
    # incomplete column: pandas may read 'True'/'False' as bool or string
    # Normalize to boolean, preserving NaN for empty cells
    df["incomplete"] = df["incomplete"].map(
        {True: True, False: False, "True": True, "False": False}
    )
    # Keep only rows with incomplete info
    df_valid = df.dropna(subset=["incomplete", "total_count"]).copy()
    df_valid["incomplete"] = df_valid["incomplete"].astype(bool)
    return df_valid


# --- analysis functions --------------------------------------------------

def print_summary(data: dict[str, pd.DataFrame]) -> None:
    """Print True/False counts and proportions."""
    print("\n=== incomplete=True/False Summary ===")
    print(f"{'Agent':<10} {'True':>8} {'False':>8} {'True%':>8}")
    print("-" * 38)
    for agent in AGENTS:
        df = data[agent]
        n_true = int(df["incomplete"].sum())
        n_false = int((~df["incomplete"]).sum())
        pct = n_true / (n_true + n_false) * 100
        print(f"{AGENT_LABELS[agent]:<10} {n_true:>8,} {n_false:>8,} {pct:>7.1f}%")


def compute_cv_comparison(data: dict[str, pd.DataFrame]) -> None:
    """Print CV comparison: full vs False-only for Copilot/Codex; descriptive for Claude."""
    print("\n=== CV Comparison ===")

    # Claude: descriptive only (n=5 in False group)
    claude_false = data["claude"].loc[~data["claude"]["incomplete"], "total_count"]
    print(f"\nClaude (False group, n={len(claude_false)}):")
    if len(claude_false) > 0:
        print(f"  Mean:  {claude_false.mean():,.0f}")
        print(f"  Min:   {claude_false.min():,.0f}")
        print(f"  Max:   {claude_false.max():,.0f}")
        print(f"  Range: {claude_false.max() - claude_false.min():,.0f}")
        print("  -> Sample too small for meaningful CV")

    # Copilot & Codex
    print(f"\n{'Agent':<10} {'Full CV':>10} {'False CV':>10} {'Reduction':>10}")
    print("-" * 44)
    for agent in ["copilot", "codex"]:
        df = data[agent]
        tc = df["total_count"]
        tc_false = df.loc[~df["incomplete"], "total_count"]
        cv_full = tc.std() / tc.mean() if tc.mean() != 0 else float("nan")
        cv_false = tc_false.std() / tc_false.mean() if tc_false.mean() != 0 else float("nan")
        reduction = (cv_full - cv_false) / cv_full * 100 if cv_full != 0 else float("nan")
        print(f"{AGENT_LABELS[agent]:<10} {cv_full:>10.4f} {cv_false:>10.4f} {reduction:>9.1f}%")


def plot_boxplot(data: dict[str, pd.DataFrame]) -> None:
    """Fig4: 1x2 box plot, True vs False total_count for Copilot & Codex only.
    Claude excluded: False group has only 5 samples, box plot misleading."""
    boxplot_agents = ["copilot", "codex"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    for i, agent in enumerate(boxplot_agents):
        ax = axes[i]
        df = data[agent]
        true_vals = df.loc[df["incomplete"], "total_count"]
        false_vals = df.loc[~df["incomplete"], "total_count"]

        bp = ax.boxplot(
            [true_vals, false_vals],
            labels=["True", "False"],
            widths=0.5,
            patch_artist=True,
            medianprops={"color": "black", "linewidth": 1.5},
        )
        bp["boxes"][0].set_facecolor("#ff9999")
        bp["boxes"][1].set_facecolor("#99ccff")

        n_true = len(true_vals)
        n_false = len(false_vals)
        ax.set_xlabel("incomplete_results")
        ax.set_ylabel("total_count")
        ax.set_title(f"{AGENT_LABELS[agent]}\nn(True)={n_true:,}, n(False)={n_false:,}")
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Copilot & Codex: total_count Distribution by incomplete_results",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(OUTPUT / "f1_fig4_incomplete-boxplot.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"\nSaved: f1_fig4_incomplete-boxplot.png")


def plot_daily_ratio(data: dict[str, pd.DataFrame]) -> None:
    """Fig7: daily incomplete=True ratio — 3x1 panel, one agent per row."""
    colors = {"claude": "#e41a1c", "copilot": "#377eb8", "codex": "#4daf4a"}
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    for i, agent in enumerate(AGENTS):
        ax1 = axes[i]
        ax2 = ax1.twinx()

        df = data[agent].copy()
        df["date"] = df["timestamp"].dt.date
        daily = df.groupby("date").agg(
            n_true=("incomplete", "sum"),
            n_total=("incomplete", "count"),
        )
        daily["ratio"] = daily["n_true"] / daily["n_total"]
        dates = pd.to_datetime(daily.index).values

        ax1.plot(dates, daily["ratio"].values, color=colors[agent],
                 linewidth=1.2, label="True ratio")
        ax2.bar(dates, daily["n_total"].values, color=colors[agent],
                alpha=0.15, width=0.8, label="Sample count")

        ax1.set_ylim(-0.05, 1.05)
        ax1.set_ylabel("True Ratio")
        ax2.set_ylabel("n")
        ax1.set_title(AGENT_LABELS[agent], loc="left", fontsize=11, fontweight="bold")
        ax1.grid(alpha=0.3)

        # Legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="center right",
                   fontsize=7)

    axes[-1].set_xlabel("Date")
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    axes[-1].xaxis.set_major_locator(mdates.DayLocator(interval=3))
    fig.autofmt_xdate()

    fig.suptitle("Daily incomplete=True Ratio with Sample Count", fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(OUTPUT / "f1_fig7_daily-incomplete-ratio.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: f1_fig7_daily-incomplete-ratio.png")


# --- main ----------------------------------------------------------------

def main() -> None:
    data = {agent: load_enriched(agent) for agent in AGENTS}
    print_summary(data)
    compute_cv_comparison(data)
    plot_boxplot(data)
    # fig5 and fig6 (scatter with regression lines) are generated by f1_trend_comparison.py
    plot_daily_ratio(data)
    print("\nDone.")


if __name__ == "__main__":
    main()
