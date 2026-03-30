"""
f1_enrich_csv.py

Data enrichment: join raw commit-count CSVs with incomplete_results from JSON snapshots.

For each agent:
  - Parse the raw CSV (timestamp, total_count)
  - For each CSV row, find the matching JSON snapshot by timestamp
  - Extract incomplete_results from the JSON
  - Write enriched CSV: timestamp, total_count, incomplete

Output (data/processed/):
  data/processed/f1_enriched_<agent>.csv

Columns:
  timestamp       — ISO 8601 string (normalized)
  total_count     — int
  incomplete      — True / False / (empty if no JSON match for that timestamp)

Matching strategy:
  - Normalize both CSV timestamps and JSON filenames to datetime objects
  - For each CSV row, find exact JSON match within ±30 seconds tolerance
  - If no match found: incomplete is left empty (read as NaN by pandas)

Prerequisites:
  - Raw commit-count CSVs must be present in data/raw/
  - JSON snapshot files must be present in a data/snapshots/ directory
    (21,000+ files not included in this repository due to size;
     obtainable from the source collection at github.com/ASSERT-KTH/agent-commits)
  - Configure REPO_DIR below to point to the agent-commits snapshot archive
"""

from __future__ import annotations

import os
import json
from datetime import datetime, timedelta

# Path to the agent-commits snapshot archive (contains raw CSVs and data/ JSON snapshots).
# Update this to match your local checkout of github.com/ASSERT-KTH/agent-commits.
REPO_DIR = "D:/GithubProjects/agent-commits"
DATA_DIR = os.path.join(REPO_DIR, "data")
OUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT_DIR, exist_ok=True)

AGENTS = {
    "claude":   "noreply%40anthropic.com",
    "codex":    "codex%40openai.com",
    "copilot":  "copilot%40users.noreply.github.com",
    "cursor":   "cursor%40anysphere.io",
    "devin":    "devin%40cognition.ai",
    "gemini":   "gemini-code-assist%40google.com",
}

TOLERANCE = timedelta(seconds=30)


def parse_csv_ts(ts: str) -> datetime | None:
    ts = ts.strip()
    try:
        if "T" in ts:
            return datetime.strptime(ts.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.strptime(ts, "%Y-%m-%d-%H:%M:%S")
    except Exception:
        return None


def parse_json_filename_ts(fname: str, agent_key: str) -> datetime | None:
    prefix = agent_key + "_"
    if not fname.startswith(prefix) or not fname.endswith(".json"):
        return None
    ts_part = fname[len(prefix):-5]
    try:
        if "T" in ts_part:
            # e.g. 2026-03-11T06_20_01Z
            ts_part = ts_part.replace("_", ":").rstrip("Z")
            return datetime.strptime(ts_part, "%Y-%m-%dT%H:%M:%S")
        elif ts_part.count("-") == 3:
            # e.g. 2026-03-03-22_35_01
            ts_part = ts_part.replace("_", ":")
            return datetime.strptime(ts_part, "%Y-%m-%d-%H:%M:%S")
        else:
            # date-only format: not used for matching
            return None
    except Exception:
        return None


def build_json_index(agent_key: str) -> dict:
    """Build a dict: datetime -> json filepath for one agent."""
    index = {}
    for fname in os.listdir(DATA_DIR):
        if not fname.startswith(agent_key + "_"):
            continue
        dt = parse_json_filename_ts(fname, agent_key)
        if dt is not None:
            index[dt] = os.path.join(DATA_DIR, fname)
    return index


def find_nearest(dt: datetime, index: dict) -> tuple[datetime | None, str | None]:
    """Return the closest datetime key within TOLERANCE, or None."""
    best_dt, best_path, best_delta = None, None, TOLERANCE + timedelta(seconds=1)
    for key, path in index.items():
        delta = abs(dt - key)
        if delta < best_delta:
            best_delta = delta
            best_dt = key
            best_path = path
    return best_dt, best_path


def read_incomplete(json_path: str) -> bool | None:
    try:
        with open(json_path, encoding="utf-8") as f:
            d = json.load(f)
        return d.get("incomplete_results", None)
    except Exception:
        return None


def enrich_agent(name: str, agent_key: str):
    csv_path = os.path.join(REPO_DIR, agent_key + "_commits.csv")
    out_path = os.path.join(OUT_DIR, f"f1_enriched_{name}.csv")

    # Read CSV
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",", 1)
            ts_raw = parts[0].strip()
            count_raw = parts[1].strip() if len(parts) > 1 else ""
            dt = parse_csv_ts(ts_raw)
            try:
                count = int(count_raw)
            except Exception:
                count = None
            rows.append((ts_raw, dt, count))

    # Build JSON index
    json_index = build_json_index(agent_key)
    print(f"  {name}: {len(rows)} CSV rows, {len(json_index)} JSON files indexed")

    matched = 0
    unmatched = 0

    with open(out_path, "w", encoding="utf-8") as out:
        out.write("timestamp,total_count,incomplete\n")
        for ts_raw, dt, count in rows:
            if dt is None:
                count_str = str(count) if count is not None else ""
                out.write(f"{ts_raw},{count_str},\n")
                unmatched += 1
                continue

            _, json_path = find_nearest(dt, json_index)
            if json_path is None:
                incomplete = ""
                unmatched += 1
            else:
                val = read_incomplete(json_path)
                incomplete = str(val) if val is not None else ""
                if incomplete:
                    matched += 1
                else:
                    unmatched += 1

            # Normalize timestamp to ISO 8601
            ts_norm = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            count_str = str(count) if count is not None else ""
            out.write(f"{ts_norm},{count_str},{incomplete}\n")

    coverage = matched / len(rows) * 100 if rows else 0
    print(f"  -> matched={matched}, unmatched={unmatched}, coverage={coverage:.1f}%")
    print(f"  -> saved: {out_path}")


def main():
    print("=== f1_enrich_csv.py: enriching CSVs with incomplete_results ===\n")
    for name, key in AGENTS.items():
        print(f"[{name}]")
        enrich_agent(name, key)
        print()
    print("Done.")


if __name__ == "__main__":
    main()
