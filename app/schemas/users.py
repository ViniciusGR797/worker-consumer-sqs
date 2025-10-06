from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Any


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User's email address used for login"
    )
    pwd: str = Field(
        ...,
        description="User's password, minimum 6 characters"
    )

    @field_validator("pwd")
    def validate_password(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("Password must be a string")
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "pwd": "strongpassword123"
            }
        }
    )


class AccessTokenSchema(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT token generated after successful login"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )
