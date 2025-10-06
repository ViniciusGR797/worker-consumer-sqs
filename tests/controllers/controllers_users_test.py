import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from controllers.users import UserController

@pytest.mark.asyncio
@patch("controllers.users.log_message")
@patch("controllers.users.put_metric")
@patch("controllers.users.validate")
async def test_login_validation_error(mock_validate, mock_metric, mock_log):
    mock_validate.return_value = (None, {"email": "Invalid format"})
    data = {"email": "invalid", "pwd": "123"}

    with pytest.raises(HTTPException) as exc:
        await UserController.login(data)
    assert exc.value.status_code == 422
    mock_metric.assert_called_with("Errors", 1)
    mock_log.assert_called()

@pytest.mark.asyncio
@patch("controllers.users.log_message")
@patch("controllers.users.put_metric")
@patch("controllers.users.validate")
async def test_login_missing_config(mock_validate, mock_metric, mock_log):
    # validação passa
    mock_credentials = MagicMock()
    mock_credentials.email = "user@test.com"
    mock_credentials.pwd = "pass"
    mock_validate.return_value = (mock_credentials, None)

    # remove configurações
    with patch("controllers.users.Config.APP_USER_EMAIL", None), \
         patch("controllers.users.Config.APP_USER_PASSWORD", None):

        with pytest.raises(HTTPException) as exc:
            await UserController.login({"email": "user@test.com", "pwd": "pass"})
        assert exc.value.status_code == 500
        mock_metric.assert_called_with("Errors", 1)
        mock_log.assert_called()

@pytest.mark.asyncio
@patch("controllers.users.log_message")
@patch("controllers.users.put_metric")
@patch("controllers.users.validate")
async def test_login_invalid_credentials(mock_validate, mock_metric, mock_log):
    mock_credentials = MagicMock()
    mock_credentials.email = "wrong@test.com"
    mock_credentials.pwd = "wrongpass"
    mock_validate.return_value = (mock_credentials, None)

    with patch("controllers.users.Config.APP_USER_EMAIL", "user@test.com"), \
         patch("controllers.users.Config.APP_USER_PASSWORD", "correctpass"):

        with pytest.raises(HTTPException) as exc:
            await UserController.login({"email": "wrong@test.com", "pwd": "wrongpass"})
        assert exc.value.status_code == 401
        mock_metric.assert_called_with("FailedLogins", 1)
        mock_log.assert_called()

@pytest.mark.asyncio
@patch("controllers.users.create_token")
@patch("controllers.users.log_message")
@patch("controllers.users.put_metric")
@patch("controllers.users.validate")
async def test_login_success(mock_validate, mock_metric, mock_log, mock_token):
    mock_credentials = MagicMock()
    mock_credentials.email = "user@test.com"
    mock_credentials.pwd = "correctpass"
    mock_validate.return_value = (mock_credentials, None)
    mock_token.return_value = "token123"

    with patch("controllers.users.Config.APP_USER_EMAIL", "user@test.com"), \
         patch("controllers.users.Config.APP_USER_PASSWORD", "correctpass"):

        result = await UserController.login({"email": "user@test.com", "pwd": "correctpass"})
        assert result["access_token"] == "token123"
        mock_metric.assert_any_call("SuccessfulLogins", 1)
        mock_log.assert_called()
