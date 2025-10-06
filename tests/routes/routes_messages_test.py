import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from routes import messages
from schemas.transactions import TransactionSchema
from schemas.messages import MessageSchema, QueueStatusSchema, ReprocessResponse
from uuid import uuid4
import boto3  # import real boto3

app = FastAPI()
app.include_router(messages.router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_boto3_client():
    with patch.object(boto3, "client") as mock_client:
        mock_sqs = MagicMock()
        mock_sqs.get_queue_url.return_value = {"QueueUrl": "https://fake-queue-url"}
        mock_sqs.send_message.return_value = {"MessageId": str(uuid4())}
        mock_sqs.receive_message.return_value = {"Messages": []}
        mock_sqs.delete_message.return_value = {}
        mock_sqs.purge_queue.return_value = {}
        mock_client.return_value = mock_sqs
        yield mock_client

@pytest.mark.asyncio
@patch("routes.messages.MessageController.send", new_callable=AsyncMock)
async def test_send_success(mock_send):
    transaction_data = {
        "transaction_id": "txn-123",
        "payer_id": "payer_001",
        "receiver_id": "receiver_001",
        "amount": 100,
        "currency": "USD"
    }

    mock_send.return_value = MessageSchema(
        message_id=uuid4(),
        timestamp="2025-10-05T12:00:00Z",
        source="transactions_api",
        type="transaction_created",
        payload=TransactionSchema.model_validate(transaction_data),
        metadata={"retries": 0, "trace_id": "trace-1"}
    )

    response = await messages.send(TransactionSchema.model_validate(transaction_data))
    assert isinstance(response, MessageSchema)
    assert response.payload.transaction_id == "txn-123"

@pytest.mark.asyncio
@patch("routes.messages.MessageController.send", new_callable=AsyncMock)
async def test_send_failure(mock_send):
    transaction_data = {
        "transaction_id": "txn-123",
        "payer_id": "payer_001",
        "receiver_id": "receiver_001",
        "amount": 100,
        "currency": "USD"
    }

    mock_send.side_effect = Exception("Internal error")
    with pytest.raises(Exception):
        await messages.send(TransactionSchema.model_validate(transaction_data))

@pytest.mark.asyncio
@patch("routes.messages.MessageController.get_status", new_callable=AsyncMock)
async def test_get_status_success(mock_status):
    mock_status.return_value = QueueStatusSchema(
        queue_name="main_queue",
        messages_available=10,
        messages_in_flight=2,
        messages_delayed=1,
        messages_in_dlq=3
    )
    response = await messages.get_status("main_queue")
    assert response.messages_available == 10
    assert response.messages_in_dlq == 3

@pytest.mark.asyncio
@patch("routes.messages.MessageController.reprocess_dlq", new_callable=AsyncMock)
async def test_reprocess_dlq_success(mock_reprocess):
    mock_reprocess.return_value = ReprocessResponse(
        message="Reprocessing completed.", total_reprocessed=5
    )
    response = await messages.reprocess_dlq("main_queue")
    assert response.total_reprocessed == 5
