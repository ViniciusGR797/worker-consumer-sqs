import pytest
from pydantic import ValidationError
from schemas.responses import (
    ErrorResponse,
    ValidationLoginErrorResponse,
    ValidationMessageErrorResponse,
    QueueNotFoundErrorResponse
)

def test_error_response_success():
    data = {"detail": "Something went wrong"}
    resp = ErrorResponse(**data)
    assert resp.detail == "Something went wrong"

def test_error_response_missing_detail():
    with pytest.raises(ValidationError):
        ErrorResponse()

def test_validation_login_error_response_success():
    data = {
        "detail": [
            {"loc": ["body", "email"], "msg": "Field required", "type": "value_error.missing"}
        ]
    }
    resp = ValidationLoginErrorResponse(**data)
    assert isinstance(resp.detail, list)
    assert resp.detail[0]["msg"] == "Field required"

def test_validation_login_error_response_empty_detail():
    with pytest.raises(ValidationError):
        ValidationLoginErrorResponse(detail=None)

def test_validation_message_error_response_success():
    data = {
        "detail": [
            {"loc": ["body", "currency"], "msg": "Field required", "type": "value_error.missing"}
        ]
    }
    resp = ValidationMessageErrorResponse(**data)
    assert resp.detail[0]["loc"] == ["body", "currency"]

def test_validation_message_error_response_empty_detail():
    with pytest.raises(ValidationError):
        ValidationMessageErrorResponse(detail=None)

def test_queue_not_found_error_response_success():
    resp = QueueNotFoundErrorResponse()
    assert resp.detail == "The specified queue does not exist or the name is invalid."

def test_queue_not_found_error_response_override():
    data = {"detail": "Custom queue error"}
    resp = QueueNotFoundErrorResponse(**data)
    assert resp.detail == "Custom queue error"

def test_queue_not_found_error_response_invalid_type():
    with pytest.raises(ValidationError):
        QueueNotFoundErrorResponse(detail=123)  # detail deve ser str
