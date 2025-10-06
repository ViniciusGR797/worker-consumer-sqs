import unittest
from unittest.mock import patch, MagicMock
from services.dynamodb import DynamoDBService

VALID_MESSAGE = {
    "message_id": "123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2025-10-04T12:00:00Z",
    "source": "transactions_api",
    "type": "transaction_created",
    "dlq_retry": 0,
    "payload": {
        "transaction_id": "txn-908765",
        "payer_id": "user-12345",
        "receiver_id": "user-67890",
        "amount": 250.75,
        "currency": "BRL",
        "description": "Donation to project X",
    },
}


class TestDynamoDBService(unittest.TestCase):
    @patch("services.dynamodb.put_metric")
    @patch("services.dynamodb.log_message")
    @patch("services.dynamodb.boto3.resource")
    def test_exists_message_success_true(self, mock_boto, mock_log, mock_metric):
        mock_table = MagicMock()
        mock_table.get_item.return_value = {"Item": VALID_MESSAGE}
        mock_boto.return_value.Table.return_value = mock_table

        service = DynamoDBService()
        result, err = service.exists_message("123")

        self.assertTrue(result)
        self.assertIsNone(err)
        mock_log.assert_called_with("123", "dynamodb_check", "success", {"exists": True})
        mock_metric.assert_not_called()

    @patch("services.dynamodb.put_metric")
    @patch("services.dynamodb.log_message")
    @patch("services.dynamodb.boto3.resource")
    def test_exists_message_success_false(self, mock_boto, mock_log, mock_metric):
        mock_table = MagicMock()
        mock_table.get_item.return_value = {}
        mock_boto.return_value.Table.return_value = mock_table

        service = DynamoDBService()
        result, err = service.exists_message("123")

        self.assertFalse(result)
        self.assertIsNone(err)
        mock_log.assert_called_with("123", "dynamodb_check", "success", {"exists": False})
        mock_metric.assert_not_called()

    @patch("services.dynamodb.put_metric")
    @patch("services.dynamodb.log_message")
    @patch("services.dynamodb.boto3.resource")
    def test_exists_message_exception(self, mock_boto, mock_log, mock_metric):
        mock_table = MagicMock()
        mock_table.get_item.side_effect = Exception("fail")
        mock_boto.return_value.Table.return_value = mock_table

        service = DynamoDBService()
        result, err = service.exists_message("123")

        self.assertFalse(result)
        self.assertEqual(err, "DynamoDB error")
        mock_log.assert_called_with("123", "dynamodb_check", "error", {"error": "fail"})
        mock_metric.assert_called_with("DynamoDBCheckError", 1)

    @patch("services.dynamodb.put_metric")
    @patch("services.dynamodb.log_message")
    @patch("services.dynamodb.convert_floats_to_decimal")
    @patch("services.dynamodb.boto3.resource")
    def test_save_message_success(self, mock_boto, mock_convert, mock_log, mock_metric):
        mock_table = MagicMock()
        mock_boto.return_value.Table.return_value = mock_table
        mock_convert.return_value = VALID_MESSAGE["payload"]

        service = DynamoDBService()
        result, err = service.save_message("123", VALID_MESSAGE)

        self.assertTrue(result)
        self.assertIsNone(err)
        mock_table.put_item.assert_called_once()
        mock_log.assert_called_with("123", "dynamodb_save", "success")
        mock_metric.assert_called_with("MessagesSaved", 1)

    @patch("services.dynamodb.put_metric")
    @patch("services.dynamodb.log_message")
    @patch("services.dynamodb.convert_floats_to_decimal")
    @patch("services.dynamodb.boto3.resource")
    def test_save_message_failure_exception(self, mock_boto, mock_convert, mock_log, mock_metric):
        mock_table = MagicMock()
        mock_table.put_item.side_effect = Exception("fail")
        mock_boto.return_value.Table.return_value = mock_table
        mock_convert.return_value = VALID_MESSAGE["payload"]

        service = DynamoDBService()
        result, err = service.save_message("123", VALID_MESSAGE)

        self.assertFalse(result)
        self.assertEqual(err, "DynamoDB error")
        mock_log.assert_called_with("123", "dynamodb_save", "error", {"error": "fail"})
        mock_metric.assert_called_with("DynamoDBSaveError", 1)

    @patch("services.dynamodb.put_metric")
    @patch("services.dynamodb.log_message")
    @patch("services.dynamodb.convert_floats_to_decimal")
    @patch("services.dynamodb.boto3.resource")
    def test_save_message_failure_conditional_check(self, mock_boto, mock_convert, mock_log, mock_metric):
        from botocore.exceptions import ClientError

        mock_table = MagicMock()
        mock_table.put_item.side_effect = ClientError(
            {"Error": {"Code": "ConditionalCheckFailedException", "Message": "Item exists"}},
            "PutItem",
        )
        mock_boto.return_value.Table.return_value = mock_table
        mock_convert.return_value = VALID_MESSAGE["payload"]

        service = DynamoDBService()
        result, err = service.save_message("123", VALID_MESSAGE)

        self.assertFalse(result)
        self.assertEqual(err, "DynamoDB error")
        mock_log.assert_called_with("123", "dynamodb_save", "error", {"error": "An error occurred (ConditionalCheckFailedException) when calling the PutItem operation: Item exists"})
        mock_metric.assert_called_with("DynamoDBSaveError", 1)
