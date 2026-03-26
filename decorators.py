# 4. @retry(max_attempts, delay_seconds)
#    - retries the decorated function up to max_attempts on exception
#    - waits delay_seconds between attempts
#    - raises the last exception if all attempts exhausted
#    - preserves function metadata with @wraps
#
# 5. @timeout(seconds)
#    - raises TimeoutError if function takes longer than seconds
#    - works for both sync and async functions
#    - preserves function metadata
# 
# 6. @rate_limit(calls, period)
#    - allows max `calls` invocations per `period` seconds
#    - raises RateLimitExceeded (custom exception) if exceeded
#    - must be thread-safe
#    - preserves function metadata

class RateLimitExceeded(Exception):
    def __init__(self, message="Rate limit exceeded"):
        super().__init__(message)
        

from functools import wraps
import time, asyncio

def retry(max_attempts, delay_seconds):
    def decorator(func):
        # async
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None

                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            await asyncio.sleep(delay_seconds)

                raise last_exception

            return async_wrapper
        # sync
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                last_exception = None

                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            time.sleep(delay_seconds)

                raise last_exception

            return sync_wrapper

    return decorator

import threading

def timeout(seconds):
    def decorator(func):
        # async
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)

            return async_wrapper

        # sync
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                result = [None]
                exception = [None]

                def target():
                    try:
                        result[0] = func(*args, **kwargs)
                    except Exception as e:
                        exception[0] = e

                t = threading.Thread(target=target)
                t.start()
                t.join(timeout=seconds)

                if t.is_alive():
                    raise TimeoutError("Function execution timed out")

                if exception[0]:
                    raise exception[0]

                return result[0]

            return sync_wrapper

    return decorator


def rate_limit(calls, period):
    def decorator(func):
        lock = threading.Lock()
        timestamps = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timestamps

            with lock:
                now = time.time()
                # remove old timestamps
                timestamps = [t for t in timestamps if now - t < period]

                if len(timestamps) >= calls:
                    raise RateLimitExceeded()

                timestamps.append(now)

            return func(*args, **kwargs)

        return wrapper

    return decorator