# AWS SQS Consumer – Lambda

<div align="center">
  <img src="https://img.shields.io/static/v1?label=python&message=language&color=blue&style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/static/v1?label=lambda&message=runtime&color=orange&style=for-the-badge&logo=aws"/>
  <img src="https://img.shields.io/static/v1?label=boto3&message=SDK&color=yellow&style=for-the-badge"/>
  <img src="https://img.shields.io/static/v1?label=docker&message=container&color=blue&style=for-the-badge&logo=docker"/>
  <img src="http://img.shields.io/static/v1?label=STATUS&message=Development&color=GREEN&style=for-the-badge"/>
</div>

<div align="center">
  <img src="docs/architecture_consumer.svg" alt="Consumer Architecture" width="600"/>
</div>

[architecture.drawio](docs/architecture.drawio)

> This Lambda function consumes messages from an AWS SQS FIFO queue, ensuring idempotent processing using DynamoDB. Messages already processed are skipped, and metrics are sent to CloudWatch for observability.

---

## 📝 Overview / Objectives

* Consume messages from **SQS FIFO** asynchronously.
* Check **idempotency** in **DynamoDB** before processing.
* Save unprocessed messages in DynamoDB and delete them from SQS.
* Provide **metrics** for monitoring message flow and failures.
* Ensure **observability** with structured logging and CloudWatch metrics.
* Operates as a **Lambda function** triggered directly by SQS.

---

## 🏛 Architecture

* **SQS FIFO Queue** → triggers Lambda consumer for each message.
* **Lambda Consumer** → checks idempotency and processes messages.
* **DynamoDB** → stores message metadata to prevent duplicate processing.
* **CloudWatch** → logs and metrics.
* **Metrics** tracked:

  * `MessagesSaved` – messages successfully processed and saved.
  * `DuplicateMessages` – messages skipped due to idempotency.
  * `InvalidMessages` – messages that failed parsing.
  * `MessagesDeleted` – messages successfully removed from SQS.
  * `DynamoDBCheckError` / `DynamoDBSaveError` / `SQSGetURLError` / `SQSDeleteError` – operational errors.

---

## ⚡ Message Processing Flow

1. SQS triggers Lambda for each message.
2. Message body is parsed (`JSON` expected).

   * If invalid → log error + increment `InvalidMessages`.
3. Check DynamoDB if message was already processed (`idempotency`).

   * If exists → log skip + increment `DuplicateMessages`.
4. If new, save message to DynamoDB.

   * Success → delete message from SQS + increment `MessagesDeleted`.
   * Failure → log error + increment `DynamoDBSaveError`.
5. All actions are logged with structured JSON and metrics sent to CloudWatch.

---

## 🔒 Idempotency

* Implemented via **DynamoDB**:

  * Each message has a unique `message_id`.
  * `ConditionExpression="attribute_not_exists(message_id)"` ensures only new messages are saved.
* Prevents **duplicate processing** even if the same message is retried from SQS.

---

## 📊 Observability

### Logging

Structured logs include:

```json
{
  "trace_id": "uuid-of-message",
  "action": "message_received|message_skipped|dynamodb_save|sqs_delete_message",
  "status": "info|success|error",
  "details": {"queue_name": "main_queue", "error": "..."},
  "timestamp": "UTC timestamp"
}
```

### Metrics

| Metric               | Description                                |
| -------------------- | ------------------------------------------ |
| `MessagesSaved`      | Messages successfully processed and saved  |
| `DuplicateMessages`  | Messages skipped due to idempotency        |
| `InvalidMessages`    | Messages that failed parsing               |
| `MessagesDeleted`    | Messages removed from SQS after processing |
| `DynamoDBCheckError` | Errors checking idempotency in DynamoDB    |
| `DynamoDBSaveError`  | Errors saving message in DynamoDB          |
| `SQSGetURLError`     | Errors retrieving SQS queue URL            |
| `SQSDeleteError`     | Errors deleting message from SQS           |

---

## 📂 Folder Structure / Patterns

```
├── app/
│   ├── main.py                       # FastAPI + Mangum entrypoint
│   ├── controllers/
│   │   └── messages.py               # Lambda entrypoint (message_handler)
│   ├── services/
│   │   ├── dynamodb.py               # DynamoDBService
│   │   └── sqs.py                    # SQSService
│   └── utils/
│       ├── config.py                 # Environment configuration
│       ├── convert.py                # Convert types
│       ├── logging.py                # Structured logging
│       └── metrics.py                # CloudWatch metrics
├── tests/                            # Unit tests
├── .env.sample                       # Sample environment variables
├── Dockerfile                        # Lambda container (optional)
├── README.md
├── requirements.txt                  # Dependencies
└── requirements_test.txt             # Test dependencies
```

---

## 🏡 Running Locally

**Requirements:** Python 3.11, AWS credentials with pre-created resources.

### Steps

* Clone the repository:

```bash
git clone https://github.com/ViniciusGR797/worker-consumer-sqs.git
cd worker-consumer-sqs
```

* Create and activate Python virtual environment (`venv`):

```bash
python -m venv venv
```

```bash
source ./venv/Scripts/activate
```

* Install project dependencies:

```bash
pip install -r requirements.txt
```

* Create `.env` file from `.env.sample`:

```bash
DYNAMO_TABLE=messages_table
REGION=us-east-1
```

* Set environment variables for AWS credentials and other configs:

```bash
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
export AWS_DEFAULT_REGION="your_region"
```

> These variables allow the application to access existing AWS resources in your account.

* Run the lambda:

```bash
python "app\main.py"
```

---

## 🧪 Tests

All tests are in `tests/` and assume you have followed the **local setup** steps (activated virtual environment, installed dependencies, and configured environment variables).

To run tests:

* Install additional test dependencies:

```bash
pip install -r requirements_test.txt
```

* Set environment variables:

```bash
export PYTHONPATH="app"
```

* Run unit tests with `pytest`:

```bash
pytest -v
```

* Run tests checking test coverage:

```bash
pytest --cov=app tests/
```
