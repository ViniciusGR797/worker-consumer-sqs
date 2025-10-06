from pydantic import BaseModel, Field, ConfigDict


class ErrorResponse(BaseModel):
    detail: str = Field(
        ...,
        description="Error message describing the unexpected issue"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Unexpected error occurred."
            }
        }
    )


class ValidationLoginErrorResponse(BaseModel):
    detail: list = Field(
        ...,
        description="List of validation errors in the request payload."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": [
                {
                    "loc": ["body", "email"],
                    "msg": "Field required",
                    "type": "value_error.missing"
                }
            ]
        }
    )


class ValidationMessageErrorResponse(BaseModel):
    detail: list = Field(
        ...,
        description="List of validation errors in the request payload."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": [
                {
                    "loc": ["body", "currency"],
                    "msg": "Field required",
                    "type": "value_error.missing"
                }
            ]
        }
    )


class QueueNotFoundErrorResponse(BaseModel):
    detail: str = Field(
        "The specified queue does not exist or the name is invalid.",
        description="Error message when the specified SQS queue is not found"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Queue does not exist or name is invalid."
            }
        }
    )
