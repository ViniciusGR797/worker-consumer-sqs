import json
from controllers.messages import message_handler


def handler(event, context):
    return message_handler(event)


if __name__ == "__main__":
    event = {
        "Records": [
            {
                "messageId": "123",
                "receiptHandle": "abc",
                "body": json.dumps(
                    {
                        "message_id": "1",
                        "payload": {},
                        "timestamp": "2025-10-06T00:00:00",
                        "source": "local",
                        "type": "test"
                    }
                ),
                "eventSourceARN":
                    "arn:aws:sqs:us-east-1:123456789012:main_queue.fifo"
            }
        ]
    }
    handler(event, None)
