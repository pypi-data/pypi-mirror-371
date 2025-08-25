
import asyncio
import time

import pytest

from ss_utils_async import gather_w_semaphore


async def sample_coroutine(delay: float, value: int) -> int:
    """A sample coroutine that sleeps for a given delay and returns a value."""
    await asyncio.sleep(delay)
    return value


@pytest.mark.asyncio
async def test_gather_w_semaphore_empty_list():
    """Test that gather_w_semaphore handles an empty list of coroutines."""
    coroutines = []
    results = await gather_w_semaphore(coroutines)
    assert results == []


@pytest.mark.asyncio
async def test_gather_w_semaphore_single_coroutine():
    """Test that gather_w_semaphore works with a single coroutine."""
    coroutines = [sample_coroutine(0.1, 1)]
    results = await gather_w_semaphore(coroutines)
    assert results == [1]


@pytest.mark.asyncio
async def test_gather_w_semaphore_multiple_coroutines():
    """Test that gather_w_semaphore runs multiple coroutines and returns results in order."""
    coroutines = [
        sample_coroutine(0.1, 1),
        sample_coroutine(0.05, 2),
        sample_coroutine(0.15, 3),
    ]
    results = await gather_w_semaphore(coroutines)
    assert results == [1, 2, 3]


@pytest.mark.asyncio
async def test_gather_w_semaphore_concurrency_limit():
    """Test that gather_w_semaphore respects the concurrency limit."""
    max_coroutines = 2
    coroutines = [
        sample_coroutine(0.2, 1),
        sample_coroutine(0.2, 2),
        sample_coroutine(0.2, 3),
        sample_coroutine(0.2, 4),
    ]
    start_time = time.time()
    await gather_w_semaphore(coroutines, max_coroutines=max_coroutines)
    end_time = time.time()
    duration = end_time - start_time
    # With 4 coroutines of 0.2s each and a limit of 2, it should take ~0.4s
    assert 0.4 <= duration < 0.6


@pytest.mark.asyncio
async def test_gather_w_semaphore_mixed_coroutines():
    """Test that gather_w_semaphore handles a mix of fast and slow coroutines."""
    coroutines = [
        sample_coroutine(0.3, 1),
        sample_coroutine(0.1, 2),
        sample_coroutine(0.2, 3),
    ]
    results = await gather_w_semaphore(coroutines)
    assert results == [1, 2, 3]
