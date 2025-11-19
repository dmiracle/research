"""Unified benchmark runner."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

from .backends import BACKENDS, Backend
from .benchmarks.cancellation import CancellationParams, run_cancellation
from .benchmarks.io_bound import IOBoundParams, run_io_bound
from .benchmarks.task_spawn import TaskSpawnParams, run_task_spawn

BenchmarkFn = Callable[[Backend, Any], Any]


SCENARIOS: dict[str, dict[str, Any]] = {
    "task_spawn": {"fn": run_task_spawn, "params_cls": TaskSpawnParams},
    "io_bound": {"fn": run_io_bound, "params_cls": IOBoundParams},
    "cancellation": {"fn": run_cancellation, "params_cls": CancellationParams},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run async library benchmarks.")
    parser.add_argument("--benchmarks", nargs="+", choices=list(SCENARIOS.keys()), default=list(SCENARIOS.keys()))
    parser.add_argument("--libraries", nargs="+", choices=list(BACKENDS.keys()), default=list(BACKENDS.keys()))
    parser.add_argument("--repetitions", type=int, default=1, help="Repetitions per benchmark/library.")
    parser.add_argument("--output", type=Path, default=Path("results/latest.json"), help="Where to store JSON results.")

    # task spawn
    parser.add_argument("--task-count", type=int, default=TaskSpawnParams.task_count)
    parser.add_argument("--payload-sleep", type=float, default=TaskSpawnParams.payload_sleep, help="Sleep payload in seconds")

    # I/O bound
    parser.add_argument("--concurrency", type=int, default=IOBoundParams.concurrency)
    parser.add_argument("--ops-per-worker", type=int, default=IOBoundParams.ops_per_worker)
    parser.add_argument("--mean-io-ms", type=float, default=IOBoundParams.mean_delay_ms, help="Mean simulated I/O delay in ms")
    parser.add_argument("--io-seed", type=int, default=IOBoundParams.seed)

    # cancellation
    parser.add_argument("--cancel-tasks", type=int, default=CancellationParams.task_count)
    parser.add_argument("--cancel-after", type=float, default=CancellationParams.cancel_after_s, help="Seconds before issuing cancellation")
    return parser.parse_args()


def build_params(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "task_spawn": TaskSpawnParams(task_count=args.task_count, payload_sleep=args.payload_sleep),
        "io_bound": IOBoundParams(
            concurrency=args.concurrency,
            ops_per_worker=args.ops_per_worker,
            mean_delay_ms=args.mean_io_ms,
            seed=args.io_seed,
        ),
        "cancellation": CancellationParams(task_count=args.cancel_tasks, cancel_after_s=args.cancel_after),
    }


def run_benchmark(backend: Backend, name: str, fn: BenchmarkFn, params: Any) -> Dict[str, Any]:
    """Run a single benchmark through the backend."""
    result = backend.run(lambda b: fn(b, params))
    return {
        "library": backend.name,
        "scenario": name,
        "params": asdict(params),
        "metrics": result,
    }


def ensure_output_dir(path: Path) -> None:
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    params = build_params(args)
    ensure_output_dir(args.output)

    entries: List[Dict[str, Any]] = []
    for lib in args.libraries:
        backend = BACKENDS[lib]
        for scenario_name in args.benchmarks:
            fn = SCENARIOS[scenario_name]["fn"]
            for rep in range(args.repetitions):
                started = time.perf_counter()
                entry = run_benchmark(backend, scenario_name, fn, params[scenario_name])
                entry["rep"] = rep + 1
                entry["duration_s"] = time.perf_counter() - started
                entries.append(entry)
                print(f"{scenario_name} on {lib} (rep {rep+1}) -> {entry['metrics']}")

    payload = {
        "meta": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "timestamp": time.time(),
            "benchmarks": args.benchmarks,
            "libraries": args.libraries,
            "repetitions": args.repetitions,
        },
        "results": entries,
    }
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved results to {args.output}")


if __name__ == "__main__":
    main()
