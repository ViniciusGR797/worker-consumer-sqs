import pytest
from unittest.mock import patch
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from security.token import create_token, is_token_valid
from utils.config import Config

@patch("security.token.Config.JWT_ACCESS_TOKEN_EXPIRES", timedelta(minutes=5))
@patch("security.token.Config.JWT_SECRET_KEY", "testsecret")
def test_create_token_returns_string():
    token = create_token()
    decoded = jwt.decode(token, "testsecret", algorithms=["HS256"])
    assert "exp" in decoded

@patch("security.token.Config.JWT_SECRET_KEY", "testsecret")
def test_is_token_valid_success():
    payload = {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    token = jwt.encode(payload, "testsecret", algorithm="HS256")
    assert is_token_valid(token) is True

@patch("security.token.Config.JWT_SECRET_KEY", "testsecret")
def test_is_token_valid_expired_token():
    payload = {"exp": datetime.now(timezone.utc) - timedelta(minutes=5)}
    token = jwt.encode(payload, "testsecret", algorithm="HS256")
    assert is_token_valid(token) is False

def test_is_token_valid_invalid_token():
    invalid_token = "invalid.token.string"
    assert is_token_valid(invalid_token) is False

@patch("security.token.jwt.decode", side_effect=JWTError)
def test_is_token_valid_raises_jwt_error(mock_decode):
    assert is_token_valid("any.token") is False
