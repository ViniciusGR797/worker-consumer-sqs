import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_USER_EMAIL = os.environ.get("APP_USER_EMAIL", "user@example.com")
    APP_USER_PASSWORD = os.environ.get(
        "APP_USER_PASSWORD", "strongpassword123"
    )

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "<random_secret_key>")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 6))
    )

    REGION = os.environ.get("REGION", "us-east-1")

    SQS_NAME = os.environ.get("SQS_NAME", "main_queue.fifo")
    DLQ_NAME = os.environ.get("DLQ_NAME", "dlq_queue.fifo")
