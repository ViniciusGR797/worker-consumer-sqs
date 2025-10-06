import pytest
from uuid import uuid4
from pydantic import ValidationError
from schemas.messages import MessageSchema, QueueStatusSchema, ReprocessResponse
from schemas.transactions import TransactionSchema

@pytest.mark.parametrize("valid_payload", [
    {
        "transaction_id": "txn-001",
        "payer_id": "payer001",
        "receiver_id": "receiver001",
        "amount": 100.5,
        "currency": "USD",
        "description": "Test payment"
    },
    {
        "transaction_id": "txn-002",
        "payer_id": "payer002",
        "receiver_id": "receiver002",
        "amount": 250,
        "currency": "BRL"
    }
])
def test_message_schema_success(valid_payload):
    data = {
        "message_id": str(uuid4()),
        "timestamp": "2025-10-05T12:00:00Z",
        "source": "transactions_api",
        "type": "transaction_created",
        "payload": valid_payload,
        "metadata": {"retries": 0, "trace_id": str(uuid4())}
    }
    msg = MessageSchema(**data)
    assert msg.payload.transaction_id == valid_payload["transaction_id"]

def test_message_schema_invalid_uuid():
    data = {
        "message_id": "invalid-uuid",
        "timestamp": "2025-10-05T12:00:00Z",
        "source": "transactions_api",
        "type": "transaction_created",
        "payload": {
            "transaction_id": "txn-001",
            "payer_id": "payer001",
            "receiver_id": "receiver001",
            "amount": 100,
            "currency": "USD"
        }
    }
    with pytest.raises(ValidationError):
        MessageSchema(**data)

def test_message_schema_default_metadata():
    data = {
        "message_id": str(uuid4()),
        "timestamp": "2025-10-05T12:00:00Z",
        "source": "transactions_api",
        "type": "transaction_created",
        "payload": {
            "transaction_id": "txn-003",
            "payer_id": "payer003",
            "receiver_id": "receiver003",
            "amount": 50,
            "currency": "EUR"
        }
    }
    msg = MessageSchema(**data)
    assert msg.metadata.retries == 0
    assert msg.metadata.trace_id is not None

def test_queue_status_schema_success():
    data = {
        "queue_name": "main_queue",
        "messages_available": 10,
        "messages_in_flight": 2,
        "messages_delayed": 1,
        "messages_in_dlq": 0
    }
    status = QueueStatusSchema(**data)
    assert status.messages_available == 10

def test_queue_status_schema_invalid_values():
    data = {
        "queue_name": "main_queue",
        "messages_in_flight": 0,
        "messages_delayed": 0,
        "messages_in_dlq": 0
    }
    with pytest.raises(ValidationError):
        QueueStatusSchema(**data)

def test_reprocess_response_success():
    resp = ReprocessResponse(total_reprocessed=5)
    assert resp.total_reprocessed == 5

def test_reprocess_response_missing_total():
    with pytest.raises(ValidationError):
        ReprocessResponse()
