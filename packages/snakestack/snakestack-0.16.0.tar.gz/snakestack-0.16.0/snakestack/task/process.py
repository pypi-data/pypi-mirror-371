import asyncio
import logging
from typing import Any, Awaitable, Callable, Self

logger = logging.getLogger(__name__)


class Process:
    def __init__(
        self: Self,
        queue_max_size: int = 100,
        func_callback: Callable[..., Awaitable[Any]] | None = None,
        sentinel: Any = None,
        concurrency: int | None = 5
    ) -> None:
        self.queue = asyncio.Queue[Any](maxsize=queue_max_size)
        self.sentinel = sentinel
        self.func_callback = func_callback
        self.semaphore = asyncio.BoundedSemaphore(concurrency) if concurrency else None

    async def enqueue(self: Self, item: Any) -> None:
        await self.queue.put(item)

    async def wait(self: Self) -> None:
        await self.queue.join()

    async def worker(
        self: Self,
        num: int
    ) -> None:
        logger.info(f"Starting worker [{num}]")
        while True:
            try:
                logger.debug(f"Worker [{num}] waiting items...")
                item = await self.queue.get()
                if item is self.sentinel:
                    logger.debug(f"Worker [{num}] was finished after get a sentinel")
                    break
                logger.debug(f"Worker [{num}] pulled item {item}")
                cb = self.func_callback or self.callback

                if self.semaphore:
                    async with self.semaphore:
                        await cb(num=num, item=item)
                else:
                    await cb(num=num, item=item)
            except Exception as _:
                logger.exception("Error on process")
            finally:
                self.queue.task_done()

    async def callback(
        self: Self,
        num: int,
        item: Any
    ) -> None:
        await asyncio.sleep(0.1)
        logger.debug(f"Worker [{num}] process item {item}")
