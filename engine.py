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

import asyncio
from logger import log_task_event

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
    def __init__(self, num_words, pipeline, cache, logger, queue):
        self.num_words = num_words
        self.pipeline = pipeline
        self.cache = cache
        self.logger = logger
        self.queue = queue
        
        self.total_processed = 0
        self.total_failed = 0
        self.total_cache_hits = 0

        self.workers = []
        self.running = False
    
    async def worker(self):
        while self.running:
            try: 
                task = await self.queue.next()
                is_cached = self.cache.get(task.id)
                if is_cached:
                    self.total_cache_hits += 1
                    task.result = is_cached
                    log_task_event(self.logger, task, "cache_hit")
                    continue
                # run pipeline (this is if event isnt already cached)
                task.status = TaskStatus.RUNNING
                log_task_event(self.logger, task, "started")
                result = await self.pipeline.execute(task)
                if result.success:
                    self.cache.put(task.id, result)
                    self.total_processed += 1
                # retry logic if there was a failure
                else:
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = TaskStatus.RETRYING
                        log_task_event(self.logger, task, "retrying")

                        await self.queue.submit(task)
                    else:
                        self.total_failed += 1
                        log_task_event(self.logger, task, "failed", {"error": result.error})

            except asyncio.CancelledError:
                break
    
    async def start(self):
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self.num_workers)
        ]

    async def stop(self):
        self._running = False

        for w in self._workers:
            w.cancel()

        await asyncio.gather(*self._workers, return_exceptions=True)

    async def submit(self, task):
        await self.queue.submit(task)
    
        