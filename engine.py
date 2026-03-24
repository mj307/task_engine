# 10. Processor — abstract base class
#     - process(task) — abstract async method
#     - name property — abstract
from models import TaskStatus, TaskResult
from abc import abstractmethod, ABC

class Processor(ABC):
    @abstractmethod
    async def process(self, task):
        pass
    
    @property
    @abstractmethod
    def name(self):
        pass
     
#
# 11. ValidationProcessor(Processor)
#     - Validates task payload has required keys (pass required_keys at init)
#     - Raises ValueError if any key missing
#
class ValidationProcessor(Processor):
    def __init__(self, required_keys):
        self.required_keys = required_keys

    @property
    def name(self):
        return "ValidationProcessor"

    async def process(self, task):
        for key in self.required_keys:
            if key not in task.payload:
                raise ValueError(f"Missing required key: {key}")
        
    

# 12. TransformProcessor(Processor)
#     - Applies a transform_fn (passed at init) to task.payload
#     - Returns transformed payload as result
class TransformProcessor(Processor):
    def __init__(self, transform_fn):
        self.transform_fn = transform_fn

    @property
    def name(self):
        return "TransformProcessor"

    async def process(self, task):
        task.payload = self.transform_fn(task.payload)
        return task.payload

#
# 13. TaskPipeline
#     - Chains multiple Processors
#     - execute(task) runs task through each processor in sequence
#     - If any processor fails, pipeline stops and marks task FAILED
#     - On success marks task SUCCESS
#     - Records duration
import time
class TaskPipeline:
    def __init__(self, processors):
        self.processors = processors

    async def execute(self, task):
        start = time.time()

        try:
            for processor in self.processors:
                await processor.process(task)

            task.status = TaskStatus.SUCCESS

            duration = (time.time() - start) * 1000

            res = TaskResult(task.id, task.payload, True,duration,None)
            task.result = res
            return res

        except Exception as e:
            task.status = TaskStatus.FAILED

            duration = (time.time() - start) * 1000
            res = TaskResult(task.id,
                None,
                False,
                duration,
                str(e))
            task.res = res
            return res

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

class WorkerPool:
    def __init__(self, num_words, pipeline, cache, logger):
        self.num_words = num_words
        self.pipeline = pipeline
        self.cache = cache
        self.logger = logger
        