import time
import asyncio
from abc import ABC, abstractmethod
from models import TaskStatus, TaskResult
from decorators import retry, timeout, rate_limit

class Processor(ABC):
    @abstractmethod
    async def process(self, task):
        pass

    @property
    @abstractmethod
    def name(self):
        pass


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


class TransformProcessor(Processor):
    def __init__(self, transform_fn):
        self.transform_fn = transform_fn

    @property
    def name(self):
        return "TransformProcessor"
    
    @retry(max_attempts=3, delay_seconds=1)
    @timeout(2)
    @rate_limit(calls=5, period=10)
    async def process(self, task):
        task.payload = self.transform_fn(task.payload)
        return task.payload



class TaskPipeline:
    def __init__(self, processors):
        self.processors = processors

    async def execute(self, task):
        start = time.time()

        try:
            for processor in self.processors:
                await processor.process(task)

            duration = (time.time() - start) * 1000

            return TaskResult(
                task.id,
                task.payload,
                True,
                duration,
                None
            )

        except Exception as e:
            duration = (time.time() - start) * 1000

            return TaskResult(
                task.id,
                None,
                False,
                duration,
                str(e)
            )



class TaskQueue:
    def __init__(self):
        self.queue = asyncio.PriorityQueue()

    async def submit(self, task):
        await self.queue.put((-task.priority, task))

    async def next(self):
        _, task = await self.queue.get()
        return task

    def task_done(self):
        self.queue.task_done() # priority queue method --> just informs that the queue has fully processed task

    def empty(self):
        return self.queue.empty()

    def size(self):
        return self.queue.qsize()



class WorkerPool:
    def __init__(self, num_workers, pipeline, cache, logger, queue):
        self.num_workers = num_workers
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

                cached = self.cache.get(task.id)

                if cached is not None:
                    self.total_cache_hits += 1
                    task.result = cached
                    continue

                task.status = TaskStatus.RUNNING

                result = await self.pipeline.execute(task)

                if result.success:
                    self.cache.put(task.id, result)
                    self.total_processed += 1
                else:
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = TaskStatus.RETRYING
                        await self.queue.submit(task)
                    else:
                        self.total_failed += 1

            except Exception as e:
                self.logger.error(f"Worker error: {e}")

            finally:
                self.queue.task_done()
    
    # start running the worker pipeline
    async def start(self):
        self.running = True
        self.workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.num_workers)
        ] 

    async def stop(self):
        self.running = False

        for w in self.workers:
            w.cancel()

        await asyncio.gather(*self.workers, return_exceptions=True)

    async def submit(self, task):
        await self.queue.submit(task)