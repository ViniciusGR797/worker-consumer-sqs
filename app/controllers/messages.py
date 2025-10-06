import time
import json
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from utils.metrics import put_metric
from utils.logging import log_message
from services.messages import MessageService
from schemas.messages import MessageSchema, QueueStatusSchema
from schemas.transactions import TransactionSchema
from utils.validate import validate


class MessageController:
    @staticmethod
    async def send(data: dict, queue_name: str):
        transaction, err = validate(TransactionSchema, data)
        if err:
            raise HTTPException(status_code=422, detail=err)

        message = MessageSchema(
            message_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            source="transactions_api",
            type="transaction_created",
            payload=transaction
        )
        trace_id = message.metadata.trace_id
        message_group_id = "default-group"

        start_time = time.time()
        log_message(
            trace_id,
            "send_message",
            "started",
            {"queue_name": queue_name}
        )

        sqs_client, err = MessageService.get_sqs_client()
        if err:
            log_message(trace_id, "send_message", "error", {"error": err})
            raise HTTPException(status_code=500, detail=err)

        queue_url, err = MessageService.get_queue_url(sqs_client, queue_name)
        if err:
            log_message(trace_id, "send_message", "error", {"error": err})
            raise HTTPException(status_code=400, detail=err)

        err = MessageService.send_to_queue(
            sqs_client, message, queue_url, message_group_id
        )
        if err:
            log_message(trace_id, "send_message", "error", {"error": err})
            raise HTTPException(status_code=500, detail=err)

        duration = time.time() - start_time
        put_metric("MessagesSent", 1)
        put_metric("ProcessingTime", duration)
        log_message(
            trace_id,
            "send_message",
            "success",
            {"queue_name": queue_name, "duration": duration}
        )

        return message

    @staticmethod
    async def get_status(queue_name: str):
        trace_id = uuid4()
        action = "get_status"
        start_time = time.time()
        log_message(trace_id, action, "started", {"queue_name": queue_name})

        sqs_client, err = MessageService.get_sqs_client()
        if err:
            log_message(trace_id, action, "error", {"error": err})
            put_metric("Errors", 1)
            raise HTTPException(status_code=500, detail=err)

        queue_url, err = MessageService.get_queue_url(sqs_client, queue_name)
        if err:
            log_message(trace_id, action, "error", {"error": err})
            put_metric("Errors", 1)
            raise HTTPException(status_code=400, detail=err)

        attrs, err = MessageService.get_queue_attributes(
            sqs_client,
            queue_url,
            [
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
                "ApproximateNumberOfMessagesDelayed"
            ]
        )
        if err:
            log_message(trace_id, action, "error", {"error": err})
            put_metric("Errors", 1)
            raise HTTPException(status_code=500, detail=err)

        messages_in_dlq = 0
        dlq_url, err = MessageService.get_dlq_url(sqs_client, queue_url)
        if err:
            log_message(trace_id, action, "error", {"error": err})
            put_metric("Errors", 1)
            raise HTTPException(status_code=500, detail=err)

        if dlq_url:
            dlq_attrs, err = MessageService.get_queue_attributes(
                sqs_client, dlq_url, ["ApproximateNumberOfMessages"]
            )
            if err:
                log_message(trace_id, action, "error", {"error": err})
                put_metric("Errors", 1)
                raise HTTPException(status_code=500, detail=err)
            messages_in_dlq = dlq_attrs.get("ApproximateNumberOfMessages", 0)

        duration = time.time() - start_time
        put_metric("ProcessingTime", duration)
        log_message(
            trace_id,
            action,
            "success",
            {
                "queue_name": queue_name,
                "messages_available": attrs.get(
                    "ApproximateNumberOfMessages", 0),
                "messages_in_flight": attrs.get(
                    "ApproximateNumberOfMessagesNotVisible", 0),
                "messages_delayed": attrs.get(
                    "ApproximateNumberOfMessagesDelayed", 0),
                "messages_in_dlq": messages_in_dlq,
                "duration": duration
            }
        )

        return QueueStatusSchema(
            queue_name=queue_name,
            messages_available=attrs.get(
                "ApproximateNumberOfMessages", 0),
            messages_in_flight=attrs.get(
                "ApproximateNumberOfMessagesNotVisible", 0),
            messages_delayed=attrs.get(
                "ApproximateNumberOfMessagesDelayed", 0),
            messages_in_dlq=messages_in_dlq
        )

    @staticmethod
    async def reprocess_dlq(queue_name: str):
        trace_id = uuid4()
        action = "reprocess_dlq"
        start_time = time.time()
        log_message(trace_id, action, "started", {"queue_name": queue_name})

        sqs_client, err = MessageService.get_sqs_client()
        if err:
            log_message(trace_id, action, "error", {"error": err})
            put_metric("Errors", 1)
            raise HTTPException(status_code=500, detail=err)

        queue_url, err = MessageService.get_queue_url(sqs_client, queue_name)
        if err:
            log_message(trace_id, action, "error", {"error": err})
            put_metric("Errors", 1)
            raise HTTPException(status_code=400, detail=err)

        dlq_url, err = MessageService.get_dlq_url(sqs_client, queue_url)
        if err:
            log_message(trace_id, action, "error", {"error": err})
            put_metric("Errors", 1)
            raise HTTPException(status_code=500, detail=err)

        total_reprocessed = 0
        while True:
            messages, err = MessageService.get_messages(sqs_client, dlq_url)
            if err:
                log_message(trace_id, action, "error", {"error": err})
                put_metric("Errors", 1)
                raise HTTPException(status_code=500, detail=err)
            if not messages:
                break

            for msg in messages:
                body_dict = json.loads(msg["Body"])
                body = MessageSchema(**body_dict)
                message_group_id = "default-group"

                err = MessageService.send_to_queue(
                    sqs_client, body, queue_url, message_group_id
                )
                if err:
                    log_message(trace_id, action, "error", {"error": err})
                    put_metric("Errors", 1)
                    raise HTTPException(status_code=500, detail=err)

                err = MessageService.delete_message(
                    sqs_client, dlq_url, msg["ReceiptHandle"]
                )
                if err:
                    log_message(trace_id, action, "error", {"error": err})
                    put_metric("Errors", 1)
                    raise HTTPException(status_code=500, detail=err)

                total_reprocessed += 1

        duration = time.time() - start_time
        put_metric("MessagesReprocessed", total_reprocessed)
        put_metric("ProcessingTime", duration)
        log_message(
            trace_id,
            action,
            "success",
            {
                "queue_name": queue_name,
                "total_reprocessed": total_reprocessed,
                "duration": duration
            }
        )

        return {
            "message": "Reprocessing completed.",
            "total_reprocessed": total_reprocessed
        }
