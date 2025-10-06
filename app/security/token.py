from jose import jwt
from datetime import datetime, timezone
from utils.config import Config


def create_token() -> str:
    expire = datetime.now(timezone.utc) + Config.JWT_ACCESS_TOKEN_EXPIRES
    payload = {"exp": expire}
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def is_token_valid(token: str) -> bool:
    try:
        jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        return True
    except Exception:
        return False
