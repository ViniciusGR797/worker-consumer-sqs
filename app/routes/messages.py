from fastapi import APIRouter, Depends, Path
from utils.config import Config
from middlewares.auth import auth_middleware
from controllers.messages import MessageController
from schemas.responses import (
    ErrorResponse,
    QueueNotFoundErrorResponse,
    ValidationMessageErrorResponse
)
from schemas.messages import (
    MessageSchema,
    QueueStatusSchema,
    ReprocessResponse
)
from schemas.transactions import TransactionSchema

router = APIRouter()


@router.post(
    "/send",
    summary="Send message to the main SQS FIFO queue",
    description=(
        "Sends a new transaction to the SQS FIFO queue based on the "
        "data provided in the request body."
    ),
    response_model=MessageSchema,
    dependencies=[Depends(auth_middleware)],
    responses={
        422: {
            "model": ValidationMessageErrorResponse,
            "description": "Invalid request payload."
        },
        500: {"model": ErrorResponse, "description": "Internal server error."}
    },
    openapi_extra={"security": [{"jwt": []}]},
)
async def send(data: TransactionSchema):
    return await MessageController.send(data.model_dump(), Config.SQS_NAME)


@router.post(
    "/send/dlq",
    summary="Send message to the DLQ (Dead-Letter Queue)",
    description=(
        "Sends a new transaction to the SQS Dead-Letter Queue (DLQ) based "
        "on the data provided in the request body."
    ),
    response_model=MessageSchema,
    dependencies=[Depends(auth_middleware)],
    responses={
        422: {
            "model": ValidationMessageErrorResponse,
            "description": "Invalid request payload."
        },
        500: {"model": ErrorResponse, "description": "Internal server error."}
    },
    openapi_extra={"security": [{"jwt": []}]},
)
async def send_dlq(data: TransactionSchema):
    return await MessageController.send(data.model_dump(), Config.DLQ_NAME)


@router.get(
    "/status/{queue_name}",
    summary="Get SQS queue status",
    description=(
        "Returns the message counts for the specified SQS queue and its DLQ. "
        "Use this endpoint to monitor queue activity and pending messages."
    ),
    response_model=QueueStatusSchema,
    dependencies=[Depends(auth_middleware)],
    responses={
        400: {
            "model": QueueNotFoundErrorResponse,
            "description": "Invalid queue name or queue does not exist."
        },
        422: {
            "model": ValidationMessageErrorResponse,
            "description": "Invalid request payload."
        },
        500: {"model": ErrorResponse, "description": "Internal server error."}
    },
    openapi_extra={"security": [{"jwt": []}]},
)
async def get_status(
    queue_name: str = Path(
        ...,
        title="Queue Name",
        description=(
            "The name of the SQS queue to get status for. "
            "Example: 'main_queue.fifo'"
        ),
        examples="main_queue.fifo"
    )
):
    return await MessageController.get_status(queue_name)


@router.post(
    "/reprocess/{queue_name}",
    summary="Reprocess messages from DLQ",
    description=(
        "Reprocesses messages from the Dead-Letter Queue (DLQ) back to the "
        "main SQS queue specified by the queue name. Returns a success "
        "message when all messages are reprocessed."
    ),
    response_model=ReprocessResponse,
    dependencies=[Depends(auth_middleware)],
    responses={
        400: {
            "model": QueueNotFoundErrorResponse,
            "description": "Invalid queue name or queue does not exist."
        },
        422: {
            "model": ValidationMessageErrorResponse,
            "description": "Invalid request payload."
        },
        500: {"model": ErrorResponse, "description": "Internal server error."}
    },
    openapi_extra={"security": [{"jwt": []}]},
)
async def reprocess_dlq(
    queue_name: str = Path(
        ...,
        title="Queue Name",
        description=(
            "The name of the SQS queue to reprocess messages from. "
            "Example: 'main_queue.fifo'"
        ),
        examples="main_queue.fifo"
    )
):
    return await MessageController.reprocess_dlq(queue_name)
