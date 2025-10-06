import json
import runpy
import unittest
from unittest.mock import patch, MagicMock
from main import handler

VALID_EVENT = {
    "Records": [
        {
            "messageId": "1",
            "receiptHandle": "r1",
            "body": '{"message_id":"123"}',
            "eventSourceARN": "arn:aws:sqs:::queue"
        }
    ]
}

class TestHandler(unittest.TestCase):

    @patch("main.message_handler")
    def test_handler_calls_message_handler(self, mock_message_handler):
        context = MagicMock()
        handler(VALID_EVENT, context)
        mock_message_handler.assert_called_once_with(VALID_EVENT)

    @patch("main.message_handler")
    def test_handler_multiple_calls(self, mock_message_handler):
        context = MagicMock()
        events = [VALID_EVENT, VALID_EVENT]
        for event in events:
            handler(event, context)
        self.assertEqual(mock_message_handler.call_count, 2)
        mock_message_handler.assert_any_call(VALID_EVENT)

    @patch("main.message_handler")
    def test_handler_exception_propagation(self, mock_message_handler):
        context = MagicMock()
        mock_message_handler.side_effect = Exception("Handler error")
        with self.assertRaises(Exception) as cm:
            handler(VALID_EVENT, context)
        self.assertEqual(str(cm.exception), "Handler error")
