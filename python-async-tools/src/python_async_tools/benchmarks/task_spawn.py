"""Task spawn/teardown benchmark."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict

from ..backends import Backend
from ..utils import percentile


@dataclass
class TaskSpawnParams:
    task_count: int = 20_000
    payload_sleep: float = 0.0005


async def _worker(backend: Backend, delay: float) -> None:
    await backend.sleep(delay)


async def run_task_spawn(backend: Backend, params: TaskSpawnParams | None = None) -> Dict[str, Any]:
    """Spawn many short-lived tasks and measure throughput."""
    params = params or TaskSpawnParams()
    latencies: list[float] = []

    async def run_one(_: int) -> None:
        start = time.perf_counter()
        await _worker(backend, params.payload_sleep)
        latencies.append(time.perf_counter() - start)

    started = time.perf_counter()
    await backend.spawn_many(params.task_count, run_one)
    elapsed = time.perf_counter() - started
    return {
        "tasks": params.task_count,
        "payload_sleep_s": params.payload_sleep,
        "duration_s": elapsed,
        "tasks_per_sec": params.task_count / elapsed if elapsed else float("inf"),
        "latency_p50_ms": percentile(latencies, 50) * 1000,
        "latency_p95_ms": percentile(latencies, 95) * 1000,
    }
