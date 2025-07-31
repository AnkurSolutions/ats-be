# Thread pool for running sync Odoo service operations
import asyncio
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=10)

async def run_in_thread(func, *args, **kwargs):
    """Helper to run sync functions in thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args, **kwargs)