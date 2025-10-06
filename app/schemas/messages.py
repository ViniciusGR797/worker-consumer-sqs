from uuid import uuid4
from pydantic import BaseModel, Field, UUID4, ConfigDict
from datetime import datetime
from typing import Optional
from schemas.transactions import TransactionSchema


class MetadataSchema(BaseModel):
    retries: int = Field(
        0,
        description="Number of attempts to process the message"
    )
    trace_id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        description="Trace ID for logs and tracing"
    )


class MessageSchema(BaseModel):
    message_id: UUID4 = Field(
        ...,
        description="Globally unique identifier for the message (UUID)"
    )
    timestamp: datetime = Field(
        ...,
        description="UTC date and time when the message was created"
    )
    source: str = Field(
        ...,
        description="Origin of the message, e.g., 'transactions_api'"
    )
    type: str = Field(
        ...,
        description="Event type, e.g., 'transaction_created'"
    )
    payload: TransactionSchema = Field(
        ...,
        description="Main message data (transaction)"
    )
    metadata: MetadataSchema = Field(
        default_factory=MetadataSchema,
        description="Message metadata"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2025-10-04T12:00:00Z",
                "source": "transactions_api",
                "type": "transaction_created",
                "payload": {
                    "transaction_id": "txn-908765",
                    "payer_id": "user-12345",
                    "receiver_id": "user-67890",
                    "amount": 250.75,
                    "currency": "BRL",
                    "description": "Donation to project X"
                },
                "metadata": {
                    "retries": 0,
                    "trace_id": "5bcb9f08-7dce-474e-aea5-7445ac1a174e"
                }
            }
        }
    )


class QueueStatusSchema(BaseModel):
    queue_name: str = Field(
        ...,
        description="Name of the SQS queue being queried"
    )
    messages_available: int = Field(
        ...,
        description="Number of messages available in the queue"
    )
    messages_in_flight: int = Field(
        ...,
        description="Number of messages being processed"
    )
    messages_delayed: int = Field(
        ...,
        description="Number of delayed messages in the queue"
    )
    messages_in_dlq: int = Field(
        ...,
        description="Number of messages in the dead-letter queue"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "queue_name": "main_queue",
                "messages_available": 15,
                "messages_in_flight": 2,
                "messages_delayed": 0,
                "messages_in_dlq": 3
            }
        }
    )


class ReprocessResponse(BaseModel):
    message: str = "Reprocessing completed."
    total_reprocessed: int = Field(
        ...,
        description="Total messages reprocessed from DLQ."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Reprocessing completed.",
                "total_reprocessed": 5
            }
        }
    )
