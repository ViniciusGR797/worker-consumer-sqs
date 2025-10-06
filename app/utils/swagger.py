from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def create_app() -> FastAPI:
    app = FastAPI(
        title="Practical Challenge - Mid-Level Platform Engineer",
        description="""
**Objective:** Develop a RESTful API for integration with AWS SQS,
allowing message production, status querying, and reprocessing
from a dead-letter queue (DLQ).

**Architecture:** The solution includes an API Gateway exposing endpoints,
a Lambda producer sending messages to SQS, a FIFO queue with DLQ,
and a Lambda consumer worker processing messages asynchronously.
Message metadata and idempotency are managed via DynamoDB.

**Authentication:** POST /users/login provides a token that must be
used in subsequent requests to authorize access to the other endpoints.

**CI/CD:** Lambdas are packaged as Docker images stored in AWS ECR,
with automated build and deployment pipelines.

**Observability:** Logs and metrics are sent to CloudWatch,
covering message counts, processing times, retries, and errors.

**Endpoints:**
- POST /messages/send: produce messages to SQS.
- GET /messages/status: query SQS and DLQ message counts.
- POST /messages/dlq/reprocess: reprocess DLQ messages to main queue.

**Design Considerations:**
- Asynchronous message consumption via Lambda worker.
- DLQ handling with prevention of loops and invalid messages.
- Idempotent processing using DynamoDB.
- Full OpenAPI/Swagger documentation.
- Containerized deployment with Docker.
- CI/CD integration with ECR.

This solution ensures a fully functional, observable, and
containerized message processing pipeline with AWS native services.
""",
        version="1.0.0",
        contact={
            "name": "Vinicius Gomes Ribeiro",
            "url": "https://github.com/ViniciusGR797",
            "email": "grib.vinicius@gmail.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
    )

    app.openapi = lambda: custom_openapi(app)

    return app


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}

    openapi_schema["components"]["securitySchemes"]["jwt"] = {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": (
            "Use the format **Bearer <token>** to authenticate requests."
        ),
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema
