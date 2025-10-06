import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DYNAMO_TABLE = os.environ.get("DYNAMO_TABLE", "messages_table")
    REGION = os.environ.get("REGION", "us-east-1")
