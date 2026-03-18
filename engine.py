# 10. Processor — abstract base class
#     - process(task) — abstract async method
#     - name property — abstract
#
# 11. ValidationProcessor(Processor)
#     - Validates task payload has required keys (pass required_keys at init)
#     - Raises ValueError if any key missing
#
# 12. TransformProcessor(Processor)
#     - Applies a transform_fn (passed at init) to task.payload
#     - Returns transformed payload as result
#
# 13. TaskPipeline
#     - Chains multiple Processors
#     - execute(task) runs task through each processor in sequence
#     - If any processor fails, pipeline stops and marks task FAILED
#     - On success marks task SUCCESS
#     - Records duration
import time
class TaskPipeline:
    def __init__(self,processors):
        self.processors = processors
    def execute(self, task):
        start = time.time()
        try:
            for processor in self.processors:
                processor.process(task)
            task.status = "SUCCESS"
            duration = (time.time()-start) * 1000 # convert to milli seconds
            return {
                "task_id": task.id,
                "output": task.payload,
                "success": True,
                "duration_ms": duration,
                "error": None
            }
        except Exception as e:
            task.status = "FAILED"
            duration = (time.time()-start) * 1000
            return {
                "task_id": task.id,
                "output": None,
                "success": False,
                "duration_ms": duration,
                "error": str(e)
            }
#
# 14. TaskQueue — thread-safe priority queue
#     - submit(task) — adds task, higher priority tasks dequeued first
#     - next() — returns next task (blocks if empty)
#     - empty property
#     - size property
#
import heapq
import asyncio
import queue

class TaskQueue:
    def __init__(self):
        self.queue = asyncio.PriorityQueue()
        
    async def submit(self, task):
        await self.queue.put((-task.priority, task))
    
    async def next(self):
        _, task = await self.queue.get()
        return task
    
    @property
    def empty(self):
        return self.queue.empty()
    @property
    def size(self):
        return self.queue.qsize()
        
    
    
# 15. WorkerPool
#     - __init__(num_workers, pipeline, cache, logger)
#     - start() — starts num_workers async workers
#     - stop() — gracefully shuts down
#     - submit(task) — adds to queue
#     - Each worker:
#         a. pulls task from queue
#         b. checks cache — if result cached, returns cached result (skip processing)
#         c. processes via pipeline
#         d. on success: caches result, logs success
#         e. on failure: if retry_count < max_retries, re-submits with RETRYING status
#         f. on final failure: logs failure with error details
#     - Tracks: total_processed, total_failed, total_cache_hits counters