import json
import boto3
from schemas.messages import MessageSchema
from utils.config import Config


class MessageService:
    @staticmethod
    def get_sqs_client():
        try:
            return boto3.client("sqs", region_name=Config.REGION), None
        except Exception as e:
            return None, f"Error creating SQS client: {e}"

    @staticmethod
    def get_queue_url(sqs_client: boto3.client, queue_name: str):
        try:
            response = sqs_client.get_queue_url(QueueName=queue_name)
            return response["QueueUrl"], None
        except Exception as e:
            return None, f"Error getting queue URL for {queue_name}: {e}"

    @staticmethod
    def get_dlq_url(sqs_client: boto3.client, queue_url: str):
        try:
            attrs = sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=["RedrivePolicy"]
            )["Attributes"]
            redrive_policy = attrs.get("RedrivePolicy")

            if not redrive_policy:
                return None, None

            dlq_arn = json.loads(redrive_policy).get("deadLetterTargetArn")
            if not dlq_arn:
                return None, None

            dlq_name = dlq_arn.split(":")[-1]
            dlq_url = sqs_client.get_queue_url(QueueName=dlq_name)["QueueUrl"]
            return dlq_url, None
        except Exception as e:
            return None, f"Error getting DLQ URL: {e}"

    @staticmethod
    def get_queue_attributes(
        sqs_client: boto3.client,
        queue_url: str,
        attribute_names: list[str]
    ):
        try:
            attrs = sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=attribute_names
            )["Attributes"]
            return {k: int(attrs.get(k, 0)) for k in attribute_names}, None
        except Exception as e:
            return None, f"Error getting queue attributes for {queue_url}: {e}"

    @staticmethod
    def get_messages(sqs_client: boto3.client, queue_url: str):
        try:
            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=1
            )
            return response.get("Messages", []), None
        except Exception as e:
            return None, f"Error receiving messages from {queue_url}: {e}"

    @staticmethod
    def send_to_queue(
        sqs_client: boto3.client,
        message: MessageSchema,
        queue_url: str,
        message_group_id: str
    ):
        try:
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message.model_dump_json(),
                MessageGroupId=message_group_id,
                MessageDeduplicationId=str(message.message_id)
            )
            return None
        except Exception as e:
            return f"Error sending message to SQS: {e}"

    @staticmethod
    def delete_message(
        sqs_client: boto3.client,
        queue_url: str,
        receipt_handle: str
    ):
        try:
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            return None
        except Exception as e:
            return f"Error deleting message from SQS: {e}"
