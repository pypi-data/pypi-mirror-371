import asyncio
from collections.abc import Coroutine
from collections.abc import Iterable
from typing import Any


async def gather_w_semaphore(coroutines: Iterable[Coroutine], max_coroutines: int = 4) -> list[Any]:
    """
    Gathers coroutines with a semaphore to limit concurrent execution, allowing arguments to be passed to coroutines.

    Args:
        coroutines: An interable of coroutines to run concurrently (NOTE: i.e. `async_fn(arg, **kwargs)`, NOT the `async_fn` itself).
        max_coroutines: The maximum number of coroutines to run concurrently.

    Returns:
        List of results.
    """
    semaphore = asyncio.Semaphore(max_coroutines)

    async def _wrap_coroutine(coroutine: Coroutine):
        async with semaphore:
            return await coroutine

    return await asyncio.gather(*[_wrap_coroutine(coroutine) for coroutine in coroutines])
