from fastapi import APIRouter
from schemas.responses import ErrorResponse, ValidationLoginErrorResponse
from controllers.users import UserController
from schemas.users import AccessTokenSchema, UserLoginSchema

router = APIRouter()


@router.post(
    "/login",
    summary="User login",
    description=(
        "Authenticates a user with email and password. "
        "Returns a JWT access token upon successful authentication. "
        "Use the token in the Authorization header (`Bearer <token>`) "
        "for protected endpoints."
    ),
    response_model=AccessTokenSchema,
    tags=["Users"],
    responses={
        200: {"description": "Login successful. Returns an access token."},
        422: {
            "model": ValidationLoginErrorResponse,
            "description": "Invalid request payload."
        },
        500: {"model": ErrorResponse, "description": "Internal server error."},
    },
)
async def login(data: UserLoginSchema):
    return await UserController.login(data.model_dump())
