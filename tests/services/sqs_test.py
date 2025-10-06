import unittest
from unittest.mock import patch, MagicMock
from services.sqs import SQSService

class TestSQSService(unittest.TestCase):

    @patch("services.sqs.put_metric")
    @patch("services.sqs.log_message")
    @patch("services.sqs.boto3.client")
    def test_get_queue_url_success(self, mock_boto, mock_log, mock_metric):
        mock_sqs_client = MagicMock()
        mock_sqs_client.get_queue_url.return_value = {"QueueUrl": "https://queue-url"}
        mock_boto.return_value = mock_sqs_client

        service = SQSService()
        result = service.get_queue_url("queue_name", "trace123")

        self.assertEqual(result, "https://queue-url")
        mock_log.assert_called_with("trace123", "sqs_get_url", "success", {"queue_name": "queue_name", "queue_url": "https://queue-url"})
        mock_metric.assert_not_called()

    @patch("services.sqs.put_metric")
    @patch("services.sqs.log_message")
    @patch("services.sqs.boto3.client")
    def test_get_queue_url_failure(self, mock_boto, mock_log, mock_metric):
        mock_sqs_client = MagicMock()
        mock_sqs_client.get_queue_url.side_effect = Exception("fail")
        mock_boto.return_value = mock_sqs_client

        service = SQSService()
        result = service.get_queue_url("queue_name", "trace123")

        self.assertIsNone(result)
        mock_log.assert_called_with("trace123", "sqs_get_url", "error", {"error": "fail", "queue_name": "queue_name"})
        mock_metric.assert_called_with("SQSGetURLError", 1)

    @patch("services.sqs.put_metric")
    @patch("services.sqs.log_message")
    @patch("services.sqs.boto3.client")
    def test_delete_message_success(self, mock_boto, mock_log, mock_metric):
        mock_sqs_client = MagicMock()
        mock_boto.return_value = mock_sqs_client

        service = SQSService(queue_url="https://queue-url")
        service.delete_message("receipt123", "trace123")

        mock_sqs_client.delete_message.assert_called_once_with(
            QueueUrl="https://queue-url",
            ReceiptHandle="receipt123"
        )
        mock_log.assert_called_with("trace123", "sqs_delete_message", "success")
        mock_metric.assert_called_with("MessagesDeleted", 1)

    @patch("services.sqs.put_metric")
    @patch("services.sqs.log_message")
    @patch("services.sqs.boto3.client")
    def test_delete_message_failure(self, mock_boto, mock_log, mock_metric):
        mock_sqs_client = MagicMock()
        mock_sqs_client.delete_message.side_effect = Exception("fail")
        mock_boto.return_value = mock_sqs_client

        service = SQSService(queue_url="https://queue-url")
        service.delete_message("receipt123", "trace123")

        mock_sqs_client.delete_message.assert_called_once_with(
            QueueUrl="https://queue-url",
            ReceiptHandle="receipt123"
        )
        mock_log.assert_called_with("trace123", "sqs_delete_message", "error", {"error": "fail"})
        mock_metric.assert_called_with("SQSDeleteError", 1)
