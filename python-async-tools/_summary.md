Python async libraries were benchmarked—`asyncio`, `trio`, and `anyio` (on Python 3.13)—using scenarios like task spawning, simulated I/O, and cancellation storms. `asyncio` led task churn and cancellation speed, while `trio` lagged on heavy spawn workloads but matched I/O latency and offered structured concurrency advantages. `anyio` performed between the two, matching `asyncio` on I/O and providing a unified task/group interface. All three libraries showed similar I/O latency under load, differing mainly in spawn and cancellation behavior. The full benchmarking code and results plots are available in the [python_async_tools repo](https://github.com/example/python_async_tools), and `anyio` itself offers a [cross-backend async API](https://anyio.readthedocs.io/).

Key findings:
- `asyncio` is fastest for raw task churn and bulk cancellation.
- `trio` offers robust structured concurrency, but with higher spawn overhead.
- `anyio` unifies APIs and matches `asyncio` on I/O when using its default backend.
- All libraries had similar p95 I/O latency under stress (≈15 ms).
