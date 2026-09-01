import asyncio
import logging
import signal
import time
from typing import Any

import svcs

from app.lib.config import Settings, get_settings
from app.lib.service_registry import register_all_services
from app.lib.sqs import SQSClient
from app.worker.exceptions import NonRetryableJobError, RetryableJobError
from app.worker.job_router import parse_message_body, route

logger = logging.getLogger(__name__)


class Worker:
    """Long-polls SQS and processes batches concurrently under a semaphore.

    boto3 is synchronous, so all SQS calls run in the default executor. Message
    lifecycle branches on the exception type raised by the handler (see
    ``worker/exceptions.py``).
    """

    def __init__(self, settings: Settings, sqs: SQSClient) -> None:
        self._settings = settings
        self._sqs = sqs
        self._semaphore = asyncio.Semaphore(settings.worker_concurrency)
        self._shutdown = asyncio.Event()
        self._last_heartbeat = time.monotonic()

    def request_shutdown(self) -> None:
        logger.info("Shutdown requested; finishing in-flight work.")
        self._shutdown.set()

    async def run(self) -> None:
        queue_url = self._settings.sqs_queue_url
        if not queue_url:
            raise RuntimeError("APP_SQS_QUEUE_URL must be set to run the worker.")
        logger.info("Worker started; polling %s", queue_url)
        while not self._shutdown.is_set():
            self._heartbeat()
            messages = await self._receive(queue_url)
            if not messages:
                continue
            await asyncio.gather(
                *(self._process(queue_url, message) for message in messages)
            )
        logger.info("Worker stopped.")

    def _heartbeat(self) -> None:
        now = time.monotonic()
        if now - self._last_heartbeat >= self._settings.worker_heartbeat_seconds:
            logger.info("worker heartbeat")
            self._last_heartbeat = now

    async def _receive(self, queue_url: str) -> list[dict[str, Any]]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sqs.receive_messages(
                queue_url,
                max_messages=self._settings.worker_max_messages_per_poll,
                wait_seconds=self._settings.worker_poll_wait_seconds,
                visibility_timeout=self._settings.worker_visibility_timeout_seconds,
            ),
        )

    async def _process(self, queue_url: str, message: dict[str, Any]) -> None:
        async with self._semaphore:
            receipt_handle = message["ReceiptHandle"]
            body = message.get("Body", "")
            try:
                data = parse_message_body(body)
                await route(data)
            except NonRetryableJobError:
                logger.exception("Non-retryable job failure; routing to DLQ")
                await self._to_dlq(queue_url, receipt_handle, body)
                return
            except RetryableJobError:
                # Leave the message; the visibility timeout will redeliver it.
                logger.warning("Retryable job failure; leaving message for redelivery")
                return
            except Exception:
                # Unexpected errors are treated as retryable (⚠ a bug can loop forever).
                logger.exception("Unexpected job failure; leaving message for redelivery")
                return
            await self._delete(queue_url, receipt_handle)

    async def _delete(self, queue_url: str, receipt_handle: str) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, self._sqs.delete_message, queue_url, receipt_handle
        )

    async def _to_dlq(self, queue_url: str, receipt_handle: str, body: str) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._sqs.send_to_dlq, {"raw_body": body})
        await self._delete(queue_url, receipt_handle)


async def run_worker() -> None:
    settings = get_settings()
    registry = svcs.Registry()
    register_all_services(registry)
    async with svcs.Container(registry) as container:
        sqs = await container.aget(SQSClient)
        worker = Worker(settings, sqs)

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, worker.request_shutdown)

        await worker.run()
    await registry.aclose()
