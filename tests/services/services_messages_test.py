import json
import pytest
from unittest.mock import AsyncMock, Mock, patch
from schemas.messages import MessageSchema, MetadataSchema, TransactionSchema
from services.messages import MessageService
from datetime import datetime, timezone
from uuid import uuid4

@pytest.fixture
def sqs_client_mock():
    return Mock()

@pytest.fixture
def message_mock():
    payload = TransactionSchema(
        transaction_id="txn-001",
        payer_id="payer001",
        receiver_id="receiver001",
        amount=100.0,
        currency="USD"
    )
    return MessageSchema(
        message_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        source="test_source",
        type="transaction_created",
        payload=payload,
        metadata=MetadataSchema(retries=0, trace_id=str(uuid4()))
    )

def test_get_sqs_client_success():
    client, error = MessageService.get_sqs_client()
    assert client is not None
    assert error is None

def test_get_queue_url_success(sqs_client_mock):
    sqs_client_mock.get_queue_url.return_value = {"QueueUrl": "url"}
    url, err = MessageService.get_queue_url(sqs_client_mock, "queue")
    assert url == "url"
    assert err is None

def test_get_queue_url_failure(sqs_client_mock):
    sqs_client_mock.get_queue_url.side_effect = Exception("fail")
    url, err = MessageService.get_queue_url(sqs_client_mock, "queue")
    assert url is None
    assert "fail" in err

def test_get_dlq_url_success(sqs_client_mock):
    redrive_policy = {"deadLetterTargetArn": "arn:aws:sqs:::dlq"}
    sqs_client_mock.get_queue_attributes.return_value = {"Attributes": {"RedrivePolicy": json.dumps(redrive_policy)}}
    sqs_client_mock.get_queue_url.return_value = {"QueueUrl": "dlq_url"}
    dlq_url, err = MessageService.get_dlq_url(sqs_client_mock, "queue_url")
    assert dlq_url == "dlq_url"
    assert err is None

def test_get_dlq_url_no_redrive(sqs_client_mock):
    sqs_client_mock.get_queue_attributes.return_value = {"Attributes": {}}
    dlq_url, err = MessageService.get_dlq_url(sqs_client_mock, "queue_url")
    assert dlq_url is None
    assert err is None

def test_get_dlq_url_exception(sqs_client_mock):
    sqs_client_mock.get_queue_attributes.side_effect = Exception("fail")
    dlq_url, err = MessageService.get_dlq_url(sqs_client_mock, "queue_url")
    assert dlq_url is None
    assert "fail" in err

def test_get_queue_attributes_success(sqs_client_mock):
    sqs_client_mock.get_queue_attributes.return_value = {"Attributes": {"A": "1", "B": "2"}}
    attrs, err = MessageService.get_queue_attributes(sqs_client_mock, "queue_url", ["A", "B"])
    assert attrs == {"A": 1, "B": 2}
    assert err is None

def test_get_queue_attributes_failure(sqs_client_mock):
    sqs_client_mock.get_queue_attributes.side_effect = Exception("fail")
    attrs, err = MessageService.get_queue_attributes(sqs_client_mock, "queue_url", ["A"])
    assert attrs is None
    assert "fail" in err

def test_get_messages_success(sqs_client_mock):
    sqs_client_mock.receive_message.return_value = {"Messages": ["msg1", "msg2"]}
    msgs, err = MessageService.get_messages(sqs_client_mock, "queue_url")
    assert msgs == ["msg1", "msg2"]
    assert err is None

def test_get_messages_failure(sqs_client_mock):
    sqs_client_mock.receive_message.side_effect = Exception("fail")
    msgs, err = MessageService.get_messages(sqs_client_mock, "queue_url")
    assert msgs is None
    assert "fail" in err

def test_send_to_queue_success(sqs_client_mock, message_mock):
    err = MessageService.send_to_queue(sqs_client_mock, message_mock, "queue_url", "group")
    assert err is None

def test_send_to_queue_failure(sqs_client_mock, message_mock):
    sqs_client_mock.send_message.side_effect = Exception("fail")
    err = MessageService.send_to_queue(sqs_client_mock, message_mock, "queue_url", "group")
    assert "fail" in err

def test_delete_message_success(sqs_client_mock):
    err = MessageService.delete_message(sqs_client_mock, "queue_url", "handle")
    assert err is None

def test_delete_message_failure(sqs_client_mock):
    sqs_client_mock.delete_message.side_effect = Exception("fail")
    err = MessageService.delete_message(sqs_client_mock, "queue_url", "handle")
    assert "fail" in err
