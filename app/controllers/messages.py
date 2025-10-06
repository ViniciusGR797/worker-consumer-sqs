import json
from services.dynamodb import DynamoDBService
from services.sqs import SQSService
from utils.logging import log_message
from utils.metrics import put_metric

dynamodb_service = DynamoDBService()
sqs_service = SQSService()


def message_handler(event):
    for record in event.get("Records", []):
        message_id = record["messageId"]
        receipt_handle = record["receiptHandle"]
        message_body = record["body"]
        queue_name = record["eventSourceARN"].split(":")[-1]

        log_message(
            message_id, "message_received", "info", {
                "queue_name": queue_name})

        try:
            data = json.loads(message_body)
            message_id = message_body.get("message_id")
        except Exception:
            log_message(
                message_id, "message_parse", "error", {
                    "body": message_body})
            put_metric("InvalidMessages", 1)
            continue

        if dynamodb_service.exists_message(message_id):
            log_message(message_id, "message_skipped", "duplicate")
            put_metric("DuplicateMessages", 1)
            continue

        if dynamodb_service.save_message(message_id, data):
            if not sqs_service.queue_url:
                sqs_service.queue_url = sqs_service.get_queue_url(
                    queue_name, message_id)
            sqs_service.delete_message(receipt_handle, message_id)
        else:
            log_message(message_id, "message_save_failed", "error")
