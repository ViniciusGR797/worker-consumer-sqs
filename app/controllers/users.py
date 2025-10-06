import time
from uuid import uuid4
from fastapi import HTTPException
from utils.metrics import put_metric
from utils.logging import log_message
from schemas.users import UserLoginSchema
from utils.config import Config
from utils.validate import validate
from security.token import create_token


class UserController:
    @staticmethod
    async def login(data: dict):
        trace_id = uuid4()
        action = "user_login"
        log_message(
            trace_id, action, "started", {"email": data.get("email")}
        )
        start_time = time.time()

        credentials, error = validate(UserLoginSchema, data)
        if error:
            log_message(trace_id, action, "error", {"error": error})
            put_metric("Errors", 1)
            raise HTTPException(
                status_code=422,
                detail=error
            )

        email = credentials.email
        password = credentials.pwd

        valid_email = Config.APP_USER_EMAIL
        pwd = Config.APP_USER_PASSWORD

        if not valid_email or not pwd:
            log_message(
                trace_id, action, "error", {"error": "Server config missing"}
            )
            put_metric("Errors", 1)
            raise HTTPException(
                status_code=500,
                detail="Server configuration error"
            )

        if email != valid_email or password != pwd:
            log_message(
                trace_id, action, "error", {"error": "Invalid credentials"}
            )
            put_metric("FailedLogins", 1)
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        access_token = create_token()

        duration = time.time() - start_time
        log_message(
            trace_id, action, "success", {"email": email, "duration": duration}
        )
        put_metric("SuccessfulLogins", 1)
        put_metric("ProcessingTime", duration)

        return {"access_token": access_token}
