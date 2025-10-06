import pytest
from pydantic import ValidationError, EmailStr
from schemas.users import UserLoginSchema, AccessTokenSchema

@pytest.mark.parametrize("valid_data", [
    {"email": "test@example.com", "pwd": "abcdef"},
    {"email": "user@domain.com", "pwd": "strongpassword123"},
])
def test_user_login_schema_success(valid_data):
    schema = UserLoginSchema(**valid_data)
    assert schema.email == valid_data["email"]
    assert schema.pwd == valid_data["pwd"]

@pytest.mark.parametrize("invalid_email", [
    {"email": "invalidemail", "pwd": "abcdef"},
    {"email": "user@domain", "pwd": "strongpassword123"},
])
def test_user_login_schema_invalid_email(invalid_email):
    with pytest.raises(ValidationError):
        UserLoginSchema(**invalid_email)

@pytest.mark.parametrize("invalid_pwd", [
    {"email": "test@example.com", "pwd": "abc"},       # <6 chars
    {"email": "user@domain.com", "pwd": ""},          # empty
    {"email": "user@domain.com", "pwd": 123456},      # not a string
])
def test_user_login_schema_invalid_password(invalid_pwd):
    with pytest.raises(ValidationError):
        UserLoginSchema(**invalid_pwd)

def test_access_token_schema_success():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    schema = AccessTokenSchema(access_token=token)
    assert schema.access_token == token

@pytest.mark.parametrize("invalid_token", [
    {"access_token": None},
    {"access_token": 12345},
])
def test_access_token_schema_invalid(invalid_token):
    with pytest.raises(ValidationError):
        AccessTokenSchema(**invalid_token)
