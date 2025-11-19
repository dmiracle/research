"""Cancellation and timeout benchmark."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict

from ..backends import Backend


@dataclass
class CancellationParams:
    task_count: int = 5000
    cancel_after_s: float = 0.05


async def _long_task(backend: Backend, _: int) -> None:
    while True:
        await backend.sleep(1)


async def run_cancellation(backend: Backend, params: CancellationParams | None = None) -> Dict[str, Any]:
    """Launch many tasks and cancel them together to measure teardown overhead."""
    params = params or CancellationParams()
    launched_at = time.perf_counter()
    result = await backend.cancellation_storm(params.task_count, params.cancel_after_s, lambda i: _long_task(backend, i))
    finished_at = time.perf_counter()
    result.update(
        {
            "tasks": params.task_count,
            "cancel_after_s": params.cancel_after_s,
            "duration_s": finished_at - launched_at,
        }
    )
    return result
