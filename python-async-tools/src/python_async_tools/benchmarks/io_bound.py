"""Simulated I/O bound workload benchmark."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any, Dict

from ..backends import Backend
from ..utils import mean, percentile


@dataclass
class IOBoundParams:
    concurrency: int = 200
    ops_per_worker: int = 200
    mean_delay_ms: float = 5.0
    seed: int = 1337


async def run_io_bound(backend: Backend, params: IOBoundParams | None = None) -> Dict[str, Any]:
    """Run many short simulated I/O calls with jitter."""
    params = params or IOBoundParams()
    rng = random.Random(params.seed)
    op_latencies: list[float] = []

    async def worker(_: int) -> None:
        for _ in range(params.ops_per_worker):
            delay = rng.expovariate(1 / params.mean_delay_ms) / 1000
            start = time.perf_counter()
            await backend.sleep(delay)
            op_latencies.append(time.perf_counter() - start)

    started = time.perf_counter()
    await backend.spawn_many(params.concurrency, worker)
    elapsed = time.perf_counter() - started
    total_ops = params.concurrency * params.ops_per_worker
    return {
        "workers": params.concurrency,
        "ops_per_worker": params.ops_per_worker,
        "mean_delay_ms": params.mean_delay_ms,
        "duration_s": elapsed,
        "ops": total_ops,
        "ops_per_sec": total_ops / elapsed if elapsed else float("inf"),
        "latency_mean_ms": mean(op_latencies) * 1000,
        "latency_p95_ms": percentile(op_latencies, 95) * 1000,
        "latency_p99_ms": percentile(op_latencies, 99) * 1000,
    }
