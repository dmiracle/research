"""Backend adapters wrapping asyncio, trio, and anyio primitives."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, List, Protocol

import anyio
import trio

AsyncFn = Callable[[int], Awaitable[Any]]


class Backend(Protocol):
    """Protocol shared by all backends."""

    name: str

    def run(self, scenario: Callable[["Backend"], Awaitable[Any]]) -> Any:
        ...

    async def sleep(self, delay: float) -> None:
        ...

    async def spawn_many(self, count: int, fn: AsyncFn) -> List[Any]:
        ...

    async def cancellation_storm(
        self, task_count: int, cancel_after: float, task_fn: Callable[[int], Awaitable[Any]]
    ) -> dict[str, Any]:
        ...


@dataclass
class AsyncioBackend:
    name: str = "asyncio"

    def run(self, scenario: Callable[[Backend], Awaitable[Any]]) -> Any:
        return asyncio.run(scenario(self))

    async def sleep(self, delay: float) -> None:  # pragma: no cover - tiny wrapper
        await asyncio.sleep(delay)

    async def spawn_many(self, count: int, fn: AsyncFn) -> List[Any]:
        tasks = [asyncio.create_task(fn(i)) for i in range(count)]
        return await asyncio.gather(*tasks)

    async def cancellation_storm(
        self, task_count: int, cancel_after: float, task_fn: Callable[[int], Awaitable[Any]]
    ) -> dict[str, Any]:
        tasks = [asyncio.create_task(task_fn(i)) for i in range(task_count)]
        await asyncio.sleep(cancel_after)
        cancel_start = time.perf_counter()
        for task in tasks:
            task.cancel()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        cancelled = sum(isinstance(res, asyncio.CancelledError) for res in results)
        other_errors = sum(1 for res in results if isinstance(res, Exception) and not isinstance(res, asyncio.CancelledError))
        settle = time.perf_counter() - cancel_start
        return {"cancelled": cancelled, "exceptions": other_errors, "settle_s": settle}


@dataclass
class TrioBackend:
    name: str = "trio"

    def run(self, scenario: Callable[[Backend], Awaitable[Any]]) -> Any:
        return trio.run(scenario, self)

    async def sleep(self, delay: float) -> None:  # pragma: no cover - tiny wrapper
        await trio.sleep(delay)

    async def spawn_many(self, count: int, fn: AsyncFn) -> List[Any]:
        results: List[Any] = [None] * count

        async def runner(idx: int) -> None:
            results[idx] = await fn(idx)

        async with trio.open_nursery() as nursery:
            for idx in range(count):
                nursery.start_soon(runner, idx)
        return results

    async def cancellation_storm(
        self, task_count: int, cancel_after: float, task_fn: Callable[[int], Awaitable[Any]]
    ) -> dict[str, Any]:
        cancelled = 0
        other_errors = 0
        scopes: list[trio.CancelScope] = []

        async def runner(idx: int) -> None:
            nonlocal cancelled, other_errors
            with trio.CancelScope() as scope:
                scopes.append(scope)
                try:
                    await task_fn(idx)
                except trio.Cancelled:
                    cancelled += 1
                    raise
                except Exception:
                    other_errors += 1
                    raise

        async with trio.open_nursery() as nursery:
            for idx in range(task_count):
                nursery.start_soon(runner, idx)
            await trio.sleep(cancel_after)
            cancel_start = time.perf_counter()
            for scope in scopes:
                scope.cancel()
        settle = time.perf_counter() - cancel_start
        return {"cancelled": cancelled, "exceptions": other_errors, "settle_s": settle}


@dataclass
class AnyioBackend:
    name: str = "anyio"

    def run(self, scenario: Callable[[Backend], Awaitable[Any]]) -> Any:
        return anyio.run(scenario, self)

    async def sleep(self, delay: float) -> None:  # pragma: no cover - tiny wrapper
        await anyio.sleep(delay)

    async def spawn_many(self, count: int, fn: AsyncFn) -> List[Any]:
        results: List[Any] = [None] * count

        async def runner(idx: int) -> None:
            results[idx] = await fn(idx)

        async with anyio.create_task_group() as tg:
            for idx in range(count):
                tg.start_soon(runner, idx)
        return results

    async def cancellation_storm(
        self, task_count: int, cancel_after: float, task_fn: Callable[[int], Awaitable[Any]]
    ) -> dict[str, Any]:
        cancelled = 0
        other_errors = 0

        async def runner(idx: int) -> None:
            nonlocal cancelled, other_errors
            try:
                await task_fn(idx)
            except anyio.get_cancelled_exc_class():
                cancelled += 1
                raise
            except Exception:
                other_errors += 1
                raise

        async with anyio.create_task_group() as tg:
            for idx in range(task_count):
                tg.start_soon(runner, idx)
            await anyio.sleep(cancel_after)
            cancel_start = time.perf_counter()
            tg.cancel_scope.cancel()
        settle = time.perf_counter() - cancel_start
        return {"cancelled": cancelled, "exceptions": other_errors, "settle_s": settle}


BACKENDS: dict[str, Backend] = {
    "asyncio": AsyncioBackend(),
    "trio": TrioBackend(),
    "anyio": AnyioBackend(),
}
