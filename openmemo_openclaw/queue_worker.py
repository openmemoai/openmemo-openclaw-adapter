"""
Async queue worker — non-blocking memory writes with retry and backoff.
"""

import asyncio
import logging
import time
from typing import Callable, Any

logger = logging.getLogger("openmemo_openclaw.queue_worker")


class AsyncMemoryWorker:
    def __init__(self, write_fn: Callable, max_retry: int = 3,
                 backoff_base: float = 0.5):
        self._write_fn = write_fn
        self._max_retry = max_retry
        self._backoff_base = backoff_base
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task = None
        self._stats = {"enqueued": 0, "written": 0, "failed": 0}

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._worker_loop())

    async def stop(self):
        self._running = False
        if self._task:
            await self._queue.put(None)
            await self._task
            self._task = None

    async def enqueue(self, payload: dict):
        self._stats["enqueued"] += 1
        await self._queue.put(payload)

    def enqueue_sync(self, payload: dict):
        self._stats["enqueued"] += 1
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._queue.put(payload))
        except RuntimeError:
            self._queue.put_nowait(payload)

    @property
    def stats(self) -> dict:
        return {**self._stats, "pending": self._queue.qsize()}

    async def _worker_loop(self):
        while self._running:
            try:
                payload = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            if payload is None:
                break

            success = await self._write_with_retry(payload)
            if success:
                self._stats["written"] += 1
            else:
                self._stats["failed"] += 1

    async def _write_with_retry(self, payload: dict) -> bool:
        for attempt in range(self._max_retry):
            try:
                result = self._write_fn(payload)
                if asyncio.iscoroutine(result):
                    await result
                return True
            except Exception as e:
                delay = self._backoff_base * (2 ** attempt)
                logger.warning(
                    "Memory write attempt %d/%d failed: %s. Retrying in %.1fs",
                    attempt + 1, self._max_retry, str(e), delay,
                )
                await asyncio.sleep(delay)

        logger.warning("Memory write failed after %d retries, dropping event", self._max_retry)
        return False


class SyncMemoryWorker:
    def __init__(self, write_fn: Callable, max_retry: int = 3,
                 backoff_base: float = 0.5):
        self._write_fn = write_fn
        self._max_retry = max_retry
        self._backoff_base = backoff_base
        self._stats = {"written": 0, "failed": 0}

    def write(self, payload: dict) -> bool:
        for attempt in range(self._max_retry):
            try:
                self._write_fn(payload)
                self._stats["written"] += 1
                return True
            except Exception as e:
                delay = self._backoff_base * (2 ** attempt)
                logger.warning(
                    "Memory write attempt %d/%d failed: %s. Retrying in %.1fs",
                    attempt + 1, self._max_retry, str(e), delay,
                )
                time.sleep(delay)

        logger.warning("Memory write failed after %d retries, dropping event", self._max_retry)
        self._stats["failed"] += 1
        return False

    @property
    def stats(self) -> dict:
        return {**self._stats}
