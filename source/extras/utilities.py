"""Store common and general functions to use in any place of code"""
import asyncio
import functools


def run_asynchronously(f):
    """Run function in executor letting the function be performed asynchronously"""

    @functools.wraps(f)
    def decorator(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))

    return decorator
