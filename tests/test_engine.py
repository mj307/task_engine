# 17. Write unittest.TestCase classes for:
#
#     TestTask
#       - auto-generated id is unique across instances
#       - default status is PENDING
#       - created_at is set on creation
#
#     TestLRUCache
#       - basic get/put
#       - eviction when capacity exceeded
#       - thread safety (concurrent reads/writes from 20 threads)
#       - invalidate removes key
#       - clear empties cache
#
#     TestDecorators
#       - @retry retries correct number of times
#       - @retry raises on final failure
#       - @retry succeeds if function eventually succeeds
#       - @timeout raises TimeoutError for slow function
#       - @timeout does not raise for fast function
#       - @rate_limit allows calls within limit
#       - @rate_limit raises RateLimitExceeded when exceeded
#
#     TestTaskPipeline
#       - valid task runs through all processors
#       - invalid task (missing key) is marked FAILED
#       - pipeline records duration on TaskResult
#       - pipeline stops at first failing processor
#
#     TestWorkerPool
#       - submitted task is processed and result cached
#       - failed task is retried up to max_retries
#       - cache hit skips processing (use Mock to verify processor not called)
#       - total_processed counter is accurate
#