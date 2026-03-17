# 16. Wire everything together:
#     - Create a pipeline with ValidationProcessor and TransformProcessor
#     - Create a WorkerPool with 3 workers
#     - Submit 10 tasks with varying priorities and payloads
#       (some tasks should be intentionally invalid to test failure/retry path)
#     - Start the pool, wait for all tasks to complete
#     - Print a summary: total processed, failed, cache hits
#     - All activity must be logged via logger.py functions only