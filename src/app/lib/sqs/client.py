import json
import logging
from typing import Any, cast

import boto3

from app.lib.config import get_settings

logger = logging.getLogger(__name__)


class SQSClient:
    """Thin boto3 wrapper for SQS transport. Registered as a singleton and shared:
    the API enqueues, the worker consumes.

    ⚠ ``send_message`` returns ``None`` (no exception) when no queue is configured,
    so a 200 API response is not proof a job was queued -- check the return value.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._client = boto3.client(
            "sqs",
            region_name=settings.aws_region,
            endpoint_url=settings.aws_endpoint_url,  # set for LocalStack in dev
        )

    def send_message(self, queue_url: str | None, body: dict[str, Any]) -> str | None:
        """Send a message. Returns the SQS message id, or ``None`` when no queue is
        configured (dev/tests) -- callers must treat ``None`` as "not enqueued"."""
        if not queue_url:
            logger.warning(
                "send_message called with no queue configured; message dropped: %s", body
            )
            return None
        response = self._client.send_message(
            QueueUrl=queue_url, MessageBody=json.dumps(body)
        )
        return cast(str | None, response.get("MessageId"))

    def receive_messages(
        self, queue_url: str, *, max_messages: int, wait_seconds: int, visibility_timeout: int
    ) -> list[dict[str, Any]]:
        response = self._client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_seconds,
            VisibilityTimeout=visibility_timeout,
        )
        return cast(list[dict[str, Any]], response.get("Messages", []))

    def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        self._client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

    def change_message_visibility(
        self, queue_url: str, receipt_handle: str, visibility_timeout: int
    ) -> None:
        self._client.change_message_visibility(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
            VisibilityTimeout=visibility_timeout,
        )

    def send_to_dlq(self, body: dict[str, Any]) -> str | None:
        """Route a non-retryable message to the DLQ, if configured."""
        dlq_url = get_settings().sqs_dlq_url
        if not dlq_url:
            logger.warning("send_to_dlq called with no DLQ configured; message dropped: %s", body)
            return None
        response = self._client.send_message(QueueUrl=dlq_url, MessageBody=json.dumps(body))
        return cast(str | None, response.get("MessageId"))
