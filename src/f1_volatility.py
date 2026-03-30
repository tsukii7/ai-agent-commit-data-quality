"""
f1_volatility.py

Volatility analysis of total_count time series.

Reads enriched CSVs and computes:
  1. Descriptive statistics per agent (mean, std, min, max, CV)
  2. Time series plot of total_count for Claude, Copilot, Codex
  3. Rolling standard deviation (window=60 samples ≈ 5 hours) per agent

Output:
  figures/f1_fig1_total-count-over-time.png
  figures/f1_fig2_rolling-std.png
  figures/f1_fig3_cv-comparison.png
  Descriptive stats printed to stdout
"""

from __future__ import annotations

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

INTERMEDIATE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ordered by total_count magnitude (descending)
AGENTS = ["claude", "copilot", "codex", "gemini", "devin", "cursor"]

ROLLING_WINDOW = 60  # 60 samples × 5 min = ~5 hours


def load_agent(name: str) -> pd.DataFrame:
    path = os.path.join(INTERMEDIATE_DIR, f"f1_enriched_{name}.csv")
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df["agent"] = name
    return df


def descriptive_stats(dfs: dict[str, pd.DataFrame]):
    print("\n=== Descriptive Statistics ===\n")
    print(f"{'Agent':<10} {'Valid':>7} {'Total':>7} {'Mean':>14} {'Std':>14} {'Min':>12} {'Max':>14} {'CV':>8}")
    print("-" * 95)
    for name in AGENTS:
        df = dfs[name]
        s = df["total_count"].dropna()
        mean = s.mean()
        std = s.std()
        cv = std / mean if mean > 0 else float("nan")
        print(f"{name:<10} {len(s):>7} {len(df):>7} {mean:>14,.0f} {std:>14,.0f} {s.min():>12,} {s.max():>14,} {cv:>8.4f}")


def plot_total_count(dfs: dict[str, pd.DataFrame]):
    # Only plot Claude, Copilot, Codex — the three agents with meaningful data.
    # Cursor (always 0), Devin (12-13), Gemini (58-107) are excluded:
    #   - Their near-constant values produce no meaningful time-series pattern
    #   - ~86% of their CSV rows have missing total_count (NaN), making plots
    #     visually degenerate (data compressed into a thin band at y-axis bottom)
    plot_agents = ["claude", "copilot", "codex"]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
    fig.suptitle("Total Commit Count Over Time", fontsize=14)

    for ax, name in zip(axes, plot_agents):
        df = dfs[name]
        ax.plot(df["timestamp"].values, df["total_count"].values, linewidth=0.4, alpha=0.8)
        ax.set_title(name.capitalize(), fontsize=11)
        ax.set_ylabel("total_count")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)

    out_path = os.path.join(OUTPUT_DIR, "f1_fig1_total-count-over-time.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"\nSaved: {out_path}")


def plot_rolling_std(dfs: dict[str, pd.DataFrame]):
    plot_agents = ["claude", "copilot", "codex"]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
    fig.suptitle(f"Rolling Std (window={ROLLING_WINDOW} samples ≈ 5h)", fontsize=14)

    for ax, name in zip(axes, plot_agents):
        df = dfs[name]
        rolling = df["total_count"].rolling(window=ROLLING_WINDOW, center=True).std()
        ax.plot(df["timestamp"].values, rolling.values, linewidth=0.5, alpha=0.8, color="tab:orange")
        ax.set_title(name.capitalize(), fontsize=11)
        ax.set_ylabel("Rolling Std")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)

    out_path = os.path.join(OUTPUT_DIR, "f1_fig2_rolling-std.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_cv_comparison(dfs: dict[str, pd.DataFrame]):
    names = []
    cvs = []
    for name in AGENTS:
        s = dfs[name]["total_count"]
        mean = s.mean()
        std = s.std()
        cv = std / mean if mean > 0 else float("nan")
        names.append(name.capitalize())
        cvs.append(cv)

    fig, ax = plt.subplots(figsize=(10, 5))
    x_pos = range(len(names))
    bars = ax.bar(x_pos, cvs, color=["tab:blue", "tab:red", "tab:green", "tab:brown", "tab:purple", "tab:gray"])
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(names)
    ax.set_ylabel("Coefficient of Variation (CV = σ/μ)")
    ax.set_title("Data Volatility: Coefficient of Variation per Agent")
    ax.grid(axis="y", alpha=0.3)
    ax.set_xlim(-0.6, len(names) - 0.4)

    import math
    for bar, cv in zip(bars, cvs):
        if math.isnan(cv):
            ax.text(bar.get_x() + bar.get_width() / 2, 0.01,
                    "N/A", ha="center", va="bottom", fontsize=9, color="gray")
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{cv:.4f}", ha="center", va="bottom", fontsize=9)

    out_path = os.path.join(OUTPUT_DIR, "f1_fig3_cv-comparison.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def main():
    print("=== f1_volatility.py: Volatility Analysis ===")

    dfs = {}
    for name in AGENTS:
        dfs[name] = load_agent(name)
        print(f"  Loaded {name}: {len(dfs[name])} rows")

    descriptive_stats(dfs)
    plot_total_count(dfs)
    plot_rolling_std(dfs)
    plot_cv_comparison(dfs)

    print("\nDone.")


if __name__ == "__main__":
    main()
