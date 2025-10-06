import boto3
from utils.convert import convert_floats_to_decimal
from utils.config import Config
from utils.logging import log_message
from utils.metrics import put_metric


class DynamoDBService:
    def __init__(self):
        self.table_name = Config.DYNAMO_TABLE
        self.dynamodb = boto3.resource("dynamodb", region_name=Config.REGION)
        self.table = self.dynamodb.Table(self.table_name)

    def exists_message(self, message_id: str) -> tuple[bool, str | None]:
        try:
            response = self.table.get_item(Key={"message_id": message_id})
            exists = "Item" in response
            log_message(
                message_id,
                "dynamodb_check",
                "success",
                {"exists": exists}
            )
            return exists, None
        except Exception as e:
            log_message(
                message_id,
                "dynamodb_check",
                "error",
                {"error": str(e)}
            )
            put_metric("DynamoDBCheckError", 1)
            return False, "DynamoDB error"

    def save_message(
            self, message_id: str,
            message: dict
    ) -> tuple[bool, str | None]:
        try:
            payload = convert_floats_to_decimal(message.get("payload", {}))
            self.table.put_item(
                Item={
                    "message_id": message_id,
                    "timestamp": message.get("timestamp"),
                    "source": message.get("source"),
                    "type": message.get("type"),
                    "payload": payload,
                },
                ConditionExpression="attribute_not_exists(message_id)"
            )
            log_message(message_id, "dynamodb_save", "success")
            put_metric("MessagesSaved", 1)
            return True, None
        except Exception as e:
            log_message(message_id, "dynamodb_save", "error", {
                "error": str(e)})
            put_metric("DynamoDBSaveError", 1)
            return False, "DynamoDB error"
