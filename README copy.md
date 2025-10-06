# RESTful API Producer – AWS SQS

<div align="center">
  <img src="https://img.shields.io/static/v1?label=python&message=language&color=blue&style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/static/v1?label=fastapi&message=framework&color=green&style=for-the-badge&logo=fastapi"/>
  <img src="https://img.shields.io/static/v1?label=lambda&message=runtime&color=orange&style=for-the-badge&logo=aws"/>
  <img src="https://img.shields.io/static/v1?label=boto3&message=SDK&color=yellow&style=for-the-badge"/>
  <img src="https://img.shields.io/static/v1?label=docker&message=container&color=blue&style=for-the-badge&logo=docker"/>
  <img src="https://img.shields.io/static/v1?label=openapi&message=docs&color=red&style=for-the-badge"/>
  <img src="http://img.shields.io/static/v1?label=STATUS&message=Development&color=GREEN&style=for-the-badge"/>
</div>

<div align="center">
  <img src="docs/architecture.svg" alt="API Architecture" width="600"/>
</div>

[architecture.drawio](docs/architecture.drawio)

> This RESTful API enables sending and consuming messages in AWS SQS queues, providing endpoints for producing messages, checking status, and reprocessing messages in the DLQ. The architecture is based on Lambda with FastAPI + Mangum, ensuring asynchronous processing, idempotency, and observability.

---

## 📝 Overview / Objectives

* Develop a **message producer** for SQS with RESTful endpoints.
* Enable **status checking** of main queues and DLQ.
* Implement **DLQ message reprocessing** with loop prevention and invalid message handling.
* Ensure **idempotency**, **detailed logging**, basic metrics, and Docker containerization.
* Provide **OpenAPI/Swagger** documentation.

---

## 🏛 Architecture

The solution follows a serverless and distributed architecture:

* **API Gateway** → exposes API endpoints.
* **Lambda Producer** → sends messages to the SQS FIFO queue.
* **SQS FIFO Queue** → main queue, with a configured **DLQ**.
* **Lambda Consumer Worker** → asynchronously processes messages.
* **DynamoDB** → manages message metadata and guarantees idempotency.
* **CloudWatch** → logs and metrics.

---

## ⚖ Consumption Decision: Lambda vs ECS

| Criteria           | Lambda (Chosen)       | ECS Fargate (Alternative) |
| ------------------ | --------------------- | ------------------------- |
| Setup Complexity   | Low                   | Medium/High               |
| Scalability        | Automatic             | Manual / Configurable     |
| Cost               | Pay-per-use           | Always running container  |
| Processing Latency | Immediate             | Variable                  |
| Retries / DLQ      | Configurable via SQS  | Manual / Scheduled        |
| Observability      | Integrated CloudWatch | Manual integration        |

> **Rationale:** Lambda provides automatic scaling, easy SQS integration, and lower operational costs for this use case.

---

## 📂 Folder Structure / Patterns

```
├── .github/
│   └── workflows/
│       └── ci-cd.yml                # CI/CD pipelines
├── app/
│   ├── controllers/
│   │   ├── messages.py              # Message controllers logic
│   │   └── users.py                 # User controllers logic
│   ├── middlewares/
│   │   └── auth.py                  # Authentication and token validation
│   ├── routes/
│   │   ├── messages.py              # Message route definitions
│   │   └── users.py                 # User route definitions
│   ├── schemas/
│   │   ├── messages.py              # Pydantic schemas for messages
│   │   ├── responses.py             # General response schemas
│   │   ├── transactions.py          # Transaction schemas
│   │   └── users.py                 # User schemas
│   ├── security/
│   │   └── token.py                 # JWT token generation and validation
│   ├── services/
│   │   └── messages.py              # SQS integration logic
│   └── utils/
│       ├── config.py                # Environment configuration
│       ├── logging.py               # Logging configuration
│       ├── metrics.py               # Custom metrics
│       ├── swagger.py               # Swagger/OpenAPI setup
│       └── validate.py              # Utility validation functions
│   └── main.py                      # FastAPI + Mangum entrypoint
├── tests/                           # Unit tests
├── .env.sample                      # Sample environment variables
├── .gitignore                       # Git ignored files/folders
├── Dockerfile                       # Dockerfile for containerization
├── README.md
├── requirements.txt                 # Project dependencies
└── requirements_test.txt            # Test dependencies

```

---

## 🔌 Endpoints (OpenAPI)

* **POST /messages/send** – Sends a message to the SQS queue.
* **GET /messages/status** – Checks the status of the main queue and DLQ.
* **POST /messages/dlq/reprocess** – Reprocesses messages from DLQ to the main queue.
* **POST /users/login** – Generates authentication token.

Interactive documentation: [Local Swagger UI](http://localhost:8000/docs) or [AWS Swagger UI](https://fqgn7lclxb.execute-api.us-east-1.amazonaws.com/docs)

---

## 🔄 Message Processing Flow

1. Produced via POST `/messages/send`.
2. Message saved in **DynamoDB** for traceability and idempotency.
3. Lambda Worker consumes messages from the main queue.
4. Asynchronous processing and logging via CloudWatch.
5. Invalid messages or those exceeding retries → sent to DLQ.

---

## ⚠ Error Handling, Retries, and DLQ

* Configured **SQS FIFO + DLQ FIFO**.
* Invalid messages moved to DLQ.
* Automatic retries via SQS (`maxReceiveCount`).
* Loop prevention during DLQ reprocessing.

---

## ✅ Idempotency

Implemented **on two levels**:

* **DynamoDB**: each message has a unique key to ensure duplicates are not processed again.
* **SQS FIFO + DLQ FIFO**: uses `MessageDeduplicationId` to prevent duplicates in the queue, even during retries or temporary failures.

This ensures **idempotent** message processing, avoiding side effects from duplicate messages and guaranteeing DLQ reprocessing integrity.

---

## 📊 Observability

The API provides **structured logging** and **custom metrics** for detailed monitoring.

### Detailed Logs

* All important events logged using Python `logger`.
* Logs structured in **JSON** with the following fields:

  * `trace_id`: unique operation identifier for tracking.
  * `action`: performed action (e.g., `send_message`, `get_status`, `reprocess_dlq`, `user_login`).
  * `status`: operation status (`started`, `success`, `error`).
  * `details`: additional information like queue name, duration, or error.
  * `timestamp`: UTC execution time.

**Example log:**

```json
{
  "trace_id": "51063aff-594b-41c7-9ddd-649817dfefa3",
  "action": "send_message",
  "status": "success",
  "details": {"queue_name": "main_queue", "duration": 0.124},
  "timestamp": "2025-10-05T20:26:22.883320+00:00"
}
```

### Custom Metrics

Metrics are sent to **AWS CloudWatch** under the namespace `Worker-consumer-SQS/Messages`.

Main metrics:

| Metric                | Description                                     |
| --------------------- | ----------------------------------------------- |
| `MessagesSent`        | Count of messages successfully sent to SQS      |
| `MessagesReprocessed` | Number of messages reprocessed from DLQ         |
| `ProcessingTime`      | Average processing time per operation (seconds) |
| `Errors`              | Count of errors during operations               |
| `FailedLogins`        | Invalid login attempts                          |
| `SuccessfulLogins`    | Successful authenticated logins                 |

> This provides full visibility of the message flow, including production, asynchronous consumption via Lambda, and DLQ reprocessing, helping detect failures and monitor performance.

---

## 🔒 Security

* `/users/login` endpoint generates **JWT token**.
* Token required in `Authorization` headers for other endpoints.

---

## 🏡 Running Locally

**Requirements:** Python 3.11, AWS credentials with pre-created resources.

### Steps

* Clone the repository:

```bash
git clone https://github.com/ViniciusGR797/producer-sqs-api.git
cd producer-sqs-api
```

* Create and activate Python virtual environment (`venv`):

```bash
python -m venv venv
```

```bash
# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

* Install project dependencies:

```bash
pip install -r requirements.txt
```

* Create `.env` file from `.env.sample`:

```bash
APP_USER_EMAIL=user@example.com
APP_USER_PASSWORD=strongpassword123
JWT_SECRET_KEY=<random_secret_key>
JWT_ACCESS_TOKEN_EXPIRES=6
REGION=us-east-1
SQS_NAME=main_queue.fifo
DLQ_NAME=dlq_queue.fifo
```

* Set environment variables for AWS credentials and other configs:

```bash
export ENV=LOCAL
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
export AWS_DEFAULT_REGION="your_region"
```

> These variables allow the application to access existing AWS resources in your account.

* Run the API:

```bash
python "app\main.py"
```

* Access documentation via [Swagger UI](http://localhost:8080/docs)

* [Insomnia collection](docs/insomnia.yaml) available for testing endpoints.

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