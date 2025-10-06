import pytest
from unittest.mock import patch
from utils.logging import log_message
from datetime import datetime, timezone
import json
import uuid

def test_log_message_success():
    trace_id = uuid.uuid4()
    action = "user_login"
    status = "started"
    details = {"email": "test@example.com"}

    with patch("utils.logging.logger.info") as mock_info:
        log_message(trace_id, action, status, details)
        assert mock_info.called
        log_arg = mock_info.call_args[0][0]
        log_data = json.loads(log_arg)
        assert log_data["trace_id"] == str(trace_id)
        assert log_data["action"] == action
        assert log_data["status"] == status
        assert log_data["details"] == details
        datetime.fromisoformat(log_data["timestamp"].replace("Z", "+00:00"))

def test_log_message_no_details():
    trace_id = uuid.uuid4()
    action = "transaction_created"
    status = "success"

    with patch("utils.logging.logger.info") as mock_info:
        log_message(trace_id, action, status)
        assert mock_info.called
        log_arg = mock_info.call_args[0][0]
        log_data = json.loads(log_arg)
        assert log_data["details"] is None

def test_log_message_invalid_trace_id():
    trace_id = 12345
    action = "error_test"
    status = "failed"
    details = {"error": "Invalid trace_id type"}

    with patch("utils.logging.logger.info") as mock_info:
        log_message(trace_id, action, status, details)
        log_arg = mock_info.call_args[0][0]
        log_data = json.loads(log_arg)
        assert log_data["trace_id"] == str(trace_id)
        assert log_data["action"] == action
        assert log_data["status"] == status
        assert log_data["details"] == details
