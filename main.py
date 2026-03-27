# 16. Wire everything together:
#     - Create a pipeline with ValidationProcessor and TransformProcessor
#     - Create a WorkerPool with 3 workers
#     - Submit 10 tasks with varying priorities and payloads
#       (some tasks should be intentionally invalid to test failure/retry path)
#     - Start the pool, wait for all tasks to complete
#     - Print a summary: total processed, failed, cache hits
#     - All activity must be logged via logger.py functions only

import asyncio
from models import Task
from engine import (
    ValidationProcessor,
    TransformProcessor,
    TaskPipeline,
    TaskQueue,
    WorkerPool
)
from cache import LRUCache
from logger import get_logger


def transform(payload):
    return {
        "name": payload["name"].lower(),
        "value": payload["value"] * -1
    }


async def main():
    logger = get_logger("main")

    pipeline = TaskPipeline([
        ValidationProcessor(["name", "value"]),
        TransformProcessor(transform)
    ])

    queue = TaskQueue()
    cache = LRUCache(3)

    worker_pool = WorkerPool(
        num_workers=3,
        pipeline=pipeline,
        cache=cache,
        logger=logger,
        queue=queue
    )

    await worker_pool.start()

    tasks = [
        Task("process_user", {"name": "med", "value": 10}, priority=2),
        Task("process_user", {"name": "mj", "value": 5}, priority=1),
        Task("process_user", {"testing": "bad"}, priority=3),
        Task("process_user", {"name": "aj", "value": 7}, priority=0),
    ]

    tasks.append(tasks[1])

    for t in tasks:
        await worker_pool.submit(t)

    await queue.queue.join()

    await worker_pool.stop()

    print("\n--- SUMMARY ---")
    print("Processed:", worker_pool.total_processed)
    print("Failed:", worker_pool.total_failed)
    print("Cache Hits:", worker_pool.total_cache_hits)


if __name__ == "__main__":
    asyncio.run(main())