from unittest.mock import patch
import json
from controllers.messages import message_handler

VALID_MESSAGE = {
    "message_id": "123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2025-10-04T12:00:00Z",
    "source": "transactions_api",
    "type": "transaction_created",
    "payload": {
        "transaction_id": "txn-908765",
        "payer_id": "user-12345",
        "receiver_id": "user-67890",
        "amount": 250.75,
        "currency": "BRL",
        "description": "Donation to project X"
    }
}

INVALID_JSON = "{invalid_json}"


@patch("controllers.messages.put_metric")
@patch("controllers.messages.log_message")
@patch("controllers.messages.sqs_service")
@patch("controllers.messages.dynamodb_service")
def test_message_parse_error(mock_dynamo, mock_sqs, mock_log, mock_metric):
    event = {"Records": [{"messageId": "1", "receiptHandle": "r1", "body": INVALID_JSON, "eventSourceARN": "arn:aws:sqs:::queue"}]}
    message_handler(event)
    mock_log.assert_called_with("1", "message_parse", "error", {"body": INVALID_JSON})
    mock_metric.assert_called_with("InvalidMessages", 1)
    mock_dynamo.exists_message.assert_not_called()
    mock_sqs.delete_message.assert_not_called()


@patch("controllers.messages.put_metric")
@patch("controllers.messages.log_message")
@patch("controllers.messages.sqs_service")
@patch("controllers.messages.dynamodb_service")
def test_message_already_exists(mock_dynamo, mock_sqs, mock_log, mock_metric):
    mock_dynamo.exists_message.return_value = True
    body = json.dumps(VALID_MESSAGE)
    event = {"Records": [{"messageId": "1", "receiptHandle": "r1", "body": body, "eventSourceARN": "arn:aws:sqs:::queue"}]}
    message_handler(event)
    mock_dynamo.exists_message.assert_called_once_with("123e4567-e89b-12d3-a456-426614174000")
    mock_log.assert_called_with("123e4567-e89b-12d3-a456-426614174000", "message_skipped", "duplicate")
    mock_metric.assert_called_with("DuplicateMessages", 1)
    mock_sqs.delete_message.assert_not_called()


@patch("controllers.messages.put_metric")
@patch("controllers.messages.log_message")
@patch("controllers.messages.sqs_service")
@patch("controllers.messages.dynamodb_service")
def test_message_saved_successfully(mock_dynamo, mock_sqs, mock_log, mock_metric):
    mock_dynamo.exists_message.return_value = False
    mock_dynamo.save_message.return_value = True
    mock_sqs.queue_url = None
    mock_sqs.get_queue_url.return_value = "queue_url"
    body = json.dumps(VALID_MESSAGE)
    event = {"Records": [{"messageId": "1", "receiptHandle": "r1", "body": body, "eventSourceARN": "arn:aws:sqs:::queue"}]}
    message_handler(event)
    mock_dynamo.exists_message.assert_called_once_with("123e4567-e89b-12d3-a456-426614174000")
    mock_dynamo.save_message.assert_called_once_with("123e4567-e89b-12d3-a456-426614174000", VALID_MESSAGE)
    mock_sqs.get_queue_url.assert_called_once_with("queue", "123e4567-e89b-12d3-a456-426614174000")
    mock_sqs.delete_message.assert_called_once_with("r1", "123e4567-e89b-12d3-a456-426614174000")


@patch("controllers.messages.put_metric")
@patch("controllers.messages.log_message")
@patch("controllers.messages.sqs_service")
@patch("controllers.messages.dynamodb_service")
def test_message_save_failure(mock_dynamo, mock_sqs, mock_log, mock_metric):
    mock_dynamo.exists_message.return_value = False
    mock_dynamo.save_message.return_value = False
    body = json.dumps(VALID_MESSAGE)
    event = {"Records": [{"messageId": "1", "receiptHandle": "r1", "body": body, "eventSourceARN": "arn:aws:sqs:::queue"}]}
    message_handler(event)
    mock_dynamo.save_message.assert_called_once_with("123e4567-e89b-12d3-a456-426614174000", VALID_MESSAGE)
    mock_sqs.delete_message.assert_not_called()
    mock_log.assert_any_call("123e4567-e89b-12d3-a456-426614174000", "message_save_failed", "error")
