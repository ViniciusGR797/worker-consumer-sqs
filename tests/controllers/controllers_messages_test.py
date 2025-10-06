import json
import pytest
from uuid import uuid4
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from controllers.messages import MessageController
from schemas.messages import MessageSchema, QueueStatusSchema

@pytest.mark.asyncio
@patch("controllers.messages.log_message")
@patch("controllers.messages.put_metric")
@patch("controllers.messages.MessageService")
@patch("controllers.messages.validate")
async def test_send_success(mock_validate, mock_service, mock_metric, mock_log):
    data = {
        "transaction_id": "123",
        "payer_id": "payer_001",
        "receiver_id": "receiver_001",
        "amount": 100,
        "currency": "USD"
    }
    queue_name = "test-queue"

    mock_validate.return_value = (data, None)
    mock_service.get_sqs_client.return_value = ("mock_client", None)
    mock_service.get_queue_url.return_value = ("http://queue-url", None)
    mock_service.send_to_queue.return_value = None

    message = await MessageController.send(data, queue_name)

    assert isinstance(message, MessageSchema)
    mock_metric.assert_any_call("MessagesSent", 1)

@pytest.mark.asyncio
@patch("controllers.messages.log_message")
@patch("controllers.messages.put_metric")
@patch("controllers.messages.validate")
async def test_send_validation_error(mock_validate, mock_metric, mock_log):
    data = {"invalid": "data"}
    queue_name = "test-queue"

    mock_validate.return_value = (None, {"error": "Invalid"})

    with pytest.raises(HTTPException) as exc:
        await MessageController.send(data, queue_name)
    assert exc.value.status_code == 422


@pytest.mark.asyncio
@patch("controllers.messages.log_message")
@patch("controllers.messages.put_metric")
@patch("controllers.messages.MessageService")
@patch("controllers.messages.validate")
async def test_send_sqs_client_error(mock_validate, mock_service, mock_metric, mock_log):
    data = {
        "transaction_id": "123",
        "payer_id": "payer_001",
        "receiver_id": "receiver_001",
        "amount": 100,
        "currency": "USD"
    }
    queue_name = "test-queue"

    mock_validate.return_value = (data, None)
    mock_service.get_sqs_client.return_value = (None, "client error")

    with pytest.raises(HTTPException) as exc:
        await MessageController.send(data, queue_name)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
@patch("controllers.messages.log_message")
@patch("controllers.messages.put_metric")
@patch("controllers.messages.MessageService")
async def test_get_status_success(mock_service, mock_metric, mock_log):
    queue_name = "test-queue"
    mock_client = "mock_client"

    mock_service.get_sqs_client.return_value = (mock_client, None)
    mock_service.get_queue_url.return_value = ("http://queue-url", None)
    mock_service.get_dlq_url.return_value = ("http://dlq-url", None)
    mock_service.get_queue_attributes.side_effect = [
        ({
            "ApproximateNumberOfMessages": 10,
            "ApproximateNumberOfMessagesNotVisible": 2,
            "ApproximateNumberOfMessagesDelayed": 1
        }, None),
        ({"ApproximateNumberOfMessages": 3}, None)
    ]

    status = await MessageController.get_status(queue_name)
    assert isinstance(status, QueueStatusSchema)
    assert status.messages_available == 10
    assert status.messages_in_dlq == 3


@pytest.mark.asyncio
@patch("controllers.messages.log_message")
@patch("controllers.messages.put_metric")
@patch("controllers.messages.MessageService")
async def test_get_status_no_dlq(mock_service, mock_metric, mock_log):
    queue_name = "test-queue"
    mock_client = "mock_client"

    mock_service.get_sqs_client.return_value = (mock_client, None)
    mock_service.get_queue_url.return_value = ("http://queue-url", None)
    mock_service.get_dlq_url.return_value = (None, None)
    mock_service.get_queue_attributes.return_value = ({
        "ApproximateNumberOfMessages": 5,
        "ApproximateNumberOfMessagesNotVisible": 1,
        "ApproximateNumberOfMessagesDelayed": 0
    }, None)

    status = await MessageController.get_status(queue_name)
    assert status.messages_in_dlq == 0
    assert status.messages_available == 5


@pytest.mark.asyncio
@patch("controllers.messages.log_message")
@patch("controllers.messages.put_metric")
@patch("controllers.messages.MessageService")
async def test_reprocess_dlq_success(mock_service, mock_metric, mock_log):
    queue_name = "test-queue"
    mock_client = "mock_client"

    msg_body = {
        "message_id": str(uuid4()),
        "timestamp": "2025-10-05T12:00:00Z",
        "source": "transactions_api",
        "type": "transaction_created",
        "payload": {
            "transaction_id": "123",
            "payer_id": "payer_001",
            "receiver_id": "receiver_001",
            "amount": 100,
            "currency": "USD"
        },
        "metadata": {"retries": 0, "trace_id": "trace-1"}
    }

    mock_service.get_sqs_client.return_value = (mock_client, None)
    mock_service.get_queue_url.return_value = ("http://queue-url", None)
    mock_service.get_dlq_url.return_value = ("http://dlq-url", None)
    mock_service.get_messages.side_effect = [
        ([{"Body": json.dumps(msg_body), "ReceiptHandle": "rh1"}], None),
        ([], None)
    ]
    mock_service.send_to_queue.return_value = None
    mock_service.delete_message.return_value = None

    result = await MessageController.reprocess_dlq(queue_name)
    assert result["total_reprocessed"] == 1
    mock_metric.assert_any_call("MessagesReprocessed", 1)


@pytest.mark.asyncio
@patch("controllers.messages.log_message")
@patch("controllers.messages.put_metric")
@patch("controllers.messages.MessageService")
async def test_reprocess_dlq_failure(mock_service, mock_metric, mock_log):
    queue_name = "test-queue"
    mock_client = "mock_client"

    mock_service.get_sqs_client.return_value = (mock_client, None)
    mock_service.get_queue_url.return_value = ("http://queue-url", None)
    mock_service.get_dlq_url.return_value = ("http://dlq-url", None)
    mock_service.get_messages.side_effect = [(None, "error")]

    with pytest.raises(HTTPException) as exc:
        await MessageController.reprocess_dlq(queue_name)
    assert exc.value.status_code == 500
    mock_metric.assert_any_call("Errors", 1)
