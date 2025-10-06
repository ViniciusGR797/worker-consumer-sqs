import boto3
from utils.config import Config
from utils.logging import log_message
from utils.metrics import put_metric


class SQSService:
    def __init__(self, queue_url=None):
        self.queue_url = queue_url
        self.sqs = boto3.client("sqs", region_name=Config.REGION)

    def get_queue_url(self, queue_name: str) -> str | None:
        try:
            response = self.sqs.get_queue_url(QueueName=queue_name)
            queue_url = response["QueueUrl"]
            log_message(
                queue_name, "sqs_get_url", "success", {
                    "queue_url": queue_url})
            return queue_url
        except Exception as e:
            log_message(queue_name, "sqs_get_url", "error", {"error": str(e)})
            put_metric("SQSGetURLError", 1)
            return None

    def delete_message(self, receipt_handle: str, trace_id: str):
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            log_message(trace_id, "sqs_delete_message", "success")
            put_metric("MessagesDeleted", 1)
        except Exception as e:
            log_message(
                trace_id, "sqs_delete_message", "error", {
                    "error": str(e)})
            put_metric("SQSDeleteError", 1)
