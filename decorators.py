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

from functools import wraps
import time
def retry(max_attempts, delay_seconds):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return f(*args, **kwargs)
                except Exception:
                    last_exception = Exception
                
                if attempt < max_attempts:
                    time.sleep(delay_seconds)
            
        
        return wrapper
    
    return decorator