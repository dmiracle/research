"""Plotting utilities for benchmark results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DEFAULT_RESULTS = Path("results/latest.json")
PLOTS_DIR = Path("plots")


def flatten_results(payload: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for entry in payload["results"]:
        row: Dict[str, Any] = {
            "library": entry["library"],
            "scenario": entry["scenario"],
            "rep": entry.get("rep", 1),
        }
        row.update({f"param_{k}": v for k, v in entry.get("params", {}).items()})
        row.update(entry.get("metrics", {}))
        rows.append(row)
    return pd.DataFrame(rows)


def plot_task_spawn(df: pd.DataFrame) -> None:
    subset = df[df["scenario"] == "task_spawn"]
    plt.figure(figsize=(5.5, 4))
    sns.barplot(subset, x="library", y="tasks_per_sec", hue="library", legend=False)
    plt.ylabel("Tasks / sec (higher is better)")
    plt.title("Task spawn/teardown throughput")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "task_spawn.png")


def plot_io_bound(df: pd.DataFrame) -> None:
    subset = df[df["scenario"] == "io_bound"]
    plt.figure(figsize=(5.5, 4))
    sns.barplot(subset, x="library", y="ops_per_sec", hue="library", legend=False)
    plt.ylabel("Ops / sec (higher is better)")
    plt.title("Simulated I/O throughput")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "io_bound_ops.png")

    plt.figure(figsize=(5.5, 4))
    sns.barplot(subset, x="library", y="latency_p95_ms", hue="library", legend=False)
    plt.ylabel("p95 latency (ms, lower better)")
    plt.title("I/O latency under load")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "io_bound_latency.png")


def plot_cancellation(df: pd.DataFrame) -> None:
    subset = df[df["scenario"] == "cancellation"]
    plt.figure(figsize=(5.5, 4))
    sns.barplot(subset, x="library", y="settle_s", hue="library", legend=False)
    plt.ylabel("Seconds to settle after cancel (lower better)")
    plt.title("Cancellation storm teardown time")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "cancellation.png")


def main(results_path: Path = DEFAULT_RESULTS) -> None:
    if not results_path.exists():
        raise SystemExit(f"Results file not found: {results_path}")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    with results_path.open() as f:
        payload = json.load(f)
    df = flatten_results(payload)
    plot_task_spawn(df)
    plot_io_bound(df)
    plot_cancellation(df)
    print(f"Plots written to {PLOTS_DIR}")


if __name__ == "__main__":
    main()
