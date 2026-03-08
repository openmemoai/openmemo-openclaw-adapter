import pytest
import asyncio
from openmemo_openclaw.queue_worker import AsyncMemoryWorker, SyncMemoryWorker


class TestSyncMemoryWorker:
    def test_successful_write(self):
        written = []
        worker = SyncMemoryWorker(write_fn=lambda p: written.append(p))
        success = worker.write({"content": "test"})
        assert success is True
        assert len(written) == 1
        assert worker.stats["written"] == 1

    def test_retry_on_failure(self):
        attempts = []

        def flaky_write(payload):
            attempts.append(1)
            if len(attempts) < 3:
                raise ConnectionError("server down")

        worker = SyncMemoryWorker(
            write_fn=flaky_write,
            max_retry=3,
            backoff_base=0.01,
        )
        success = worker.write({"content": "test"})
        assert success is True
        assert len(attempts) == 3

    def test_failure_after_max_retries(self):
        def always_fail(payload):
            raise ConnectionError("server down")

        worker = SyncMemoryWorker(
            write_fn=always_fail,
            max_retry=2,
            backoff_base=0.01,
        )
        success = worker.write({"content": "test"})
        assert success is False
        assert worker.stats["failed"] == 1


class TestAsyncMemoryWorker:
    @pytest.mark.asyncio
    async def test_async_write(self):
        written = []

        def write_fn(payload):
            written.append(payload)

        worker = AsyncMemoryWorker(write_fn=write_fn)
        await worker.start()
        await worker.enqueue({"content": "test1"})
        await worker.enqueue({"content": "test2"})

        await asyncio.sleep(0.2)
        await worker.stop()

        assert len(written) == 2
        assert worker.stats["written"] == 2
        assert worker.stats["enqueued"] == 2

    @pytest.mark.asyncio
    async def test_async_retry(self):
        attempts = []

        def flaky_write(payload):
            attempts.append(1)
            if len(attempts) < 2:
                raise ConnectionError("fail")

        worker = AsyncMemoryWorker(
            write_fn=flaky_write,
            max_retry=3,
            backoff_base=0.01,
        )
        await worker.start()
        await worker.enqueue({"content": "test"})

        await asyncio.sleep(0.5)
        await worker.stop()

        assert worker.stats["written"] == 1

    @pytest.mark.asyncio
    async def test_async_failure(self):
        def always_fail(payload):
            raise ConnectionError("down")

        worker = AsyncMemoryWorker(
            write_fn=always_fail,
            max_retry=2,
            backoff_base=0.01,
        )
        await worker.start()
        await worker.enqueue({"content": "test"})

        await asyncio.sleep(1.0)
        await worker.stop()

        assert worker.stats["failed"] == 1
