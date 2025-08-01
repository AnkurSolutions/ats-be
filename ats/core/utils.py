# Thread pool for running sync Odoo service operations
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

executor = ThreadPoolExecutor(max_workers=10)

async def run_in_thread(func, *args, **kwargs):
    """Helper to run sync functions in thread pool"""
    loop = asyncio.get_event_loop()
    if kwargs:
        # Use functools.partial to bind keyword arguments
        partial_func = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, partial_func)
    else:
        # If no kwargs, use the original approach
        return await loop.run_in_executor(executor, func, *args)