import pytest
from fastapi import Request, HTTPException
from middlewares.auth import auth_middleware
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_missing_authorization_header():
    request = MagicMock(spec=Request)
    request.headers.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        await auth_middleware(request)
    assert exc.value.status_code == 401
    assert "Missing or invalid Authorization header" in exc.value.detail

@pytest.mark.asyncio
async def test_invalid_authorization_prefix():
    request = MagicMock(spec=Request)
    request.headers.get.return_value = "Token abc123"  # errado, deve começar com Bearer

    with pytest.raises(HTTPException) as exc:
        await auth_middleware(request)
    assert exc.value.status_code == 401
    assert "Missing or invalid Authorization header" in exc.value.detail

@pytest.mark.asyncio
@patch("middlewares.auth.is_token_valid")
async def test_invalid_token(mock_is_valid):
    request = MagicMock(spec=Request)
    request.headers.get.return_value = "Bearer invalidtoken"
    mock_is_valid.return_value = False

    with pytest.raises(HTTPException) as exc:
        await auth_middleware(request)
    assert exc.value.status_code == 401
    assert "Invalid or expired token" in exc.value.detail
    mock_is_valid.assert_called_once_with("invalidtoken")

@pytest.mark.asyncio
@patch("middlewares.auth.is_token_valid")
async def test_valid_token_sets_request_state(mock_is_valid):
    request = MagicMock(spec=Request)
    request.headers.get.return_value = "Bearer validtoken"
    mock_is_valid.return_value = True
    request.state = MagicMock()

    await auth_middleware(request)
    mock_is_valid.assert_called_once_with("validtoken")
    assert request.state.token == "validtoken"
