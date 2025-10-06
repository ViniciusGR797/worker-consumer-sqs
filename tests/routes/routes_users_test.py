import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException
from controllers.users import UserController
from schemas.users import UserLoginSchema
from security.token import create_token

@pytest.mark.asyncio
@patch("controllers.users.put_metric")
@patch("controllers.users.log_message")
@patch("controllers.users.validate")
@patch("controllers.users.Config")
@patch("controllers.users.create_token")
async def test_login_success(mock_create_token, mock_config, mock_validate, mock_log, mock_metric):
    user_data = {"email": "test@example.com", "pwd": "password123"}
    mock_validate.return_value = (MagicMock(email="test@example.com", pwd="password123"), None)
    mock_config.APP_USER_EMAIL = "test@example.com"
    mock_config.APP_USER_PASSWORD = "password123"
    mock_create_token.return_value = "token123"

    result = await UserController.login(user_data)

    assert result["access_token"] == "token123"
    mock_log.assert_called()
    mock_metric.assert_any_call("SuccessfulLogins", 1)

@pytest.mark.asyncio
@patch("controllers.users.put_metric")
@patch("controllers.users.log_message")
@patch("controllers.users.validate")
async def test_login_validation_error(mock_validate, mock_log, mock_metric):
    user_data = {"email": "", "pwd": ""}
    mock_validate.return_value = (None, {"email": "Field required"})

    with pytest.raises(HTTPException) as exc:
        await UserController.login(user_data)

    assert exc.value.status_code == 422
    assert exc.value.detail == {"email": "Field required"}
    mock_log.assert_called()
    mock_metric.assert_called_with("Errors", 1)

@pytest.mark.asyncio
@patch("controllers.users.put_metric")
@patch("controllers.users.log_message")
@patch("controllers.users.validate")
@patch("controllers.users.Config")
async def test_login_missing_config(mock_config, mock_validate, mock_log, mock_metric):
    user_data = {"email": "test@example.com", "pwd": "password123"}
    mock_validate.return_value = (MagicMock(email="test@example.com", pwd="password123"), None)
    mock_config.APP_USER_EMAIL = None
    mock_config.APP_USER_PASSWORD = None

    with pytest.raises(HTTPException) as exc:
        await UserController.login(user_data)

    assert exc.value.status_code == 500
    assert exc.value.detail == "Server configuration error"
    mock_log.assert_called()
    mock_metric.assert_called_with("Errors", 1)

@pytest.mark.asyncio
@patch("controllers.users.put_metric")
@patch("controllers.users.log_message")
@patch("controllers.users.validate")
@patch("controllers.users.Config")
async def test_login_invalid_credentials(mock_config, mock_validate, mock_log, mock_metric):
    user_data = {"email": "wrong@example.com", "pwd": "wrongpass"}
    mock_validate.return_value = (MagicMock(email="wrong@example.com", pwd="wrongpass"), None)
    mock_config.APP_USER_EMAIL = "test@example.com"
    mock_config.APP_USER_PASSWORD = "password123"

    with pytest.raises(HTTPException) as exc:
        await UserController.login(user_data)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"
    mock_log.assert_called()
    mock_metric.assert_called_with("FailedLogins", 1)
