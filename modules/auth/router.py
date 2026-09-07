from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from common.exceptions import ConflictError, ForbiddenError
from common.response import ResponseModel, ok
from database.session import get_db
from modules.auth.dependencies import get_current_user
from modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from modules.auth.security import (
    clear_auth_cookie,
    create_access_token,
    set_auth_cookie,
)
from modules.auth.service import (
    DuplicateEmailError,
    InvalidCredentialsError,
    authenticate_user,
    register_user,
)
from modules.users.model import User
from modules.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=ResponseModel[UserRead],
    status_code=201,
    summary="Register a new user",
)
def register(
    payload: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ResponseModel[UserRead]:
    try:
        user = register_user(db, payload)
    except DuplicateEmailError:
        raise ConflictError(
            message="An account with this email already exists.",
            code="duplicate_email",
        )

    return ok(data=user, message="User registered successfully.")


@router.post(
    "/login",
    response_model=ResponseModel[TokenResponse],
    summary="Login and receive an access token",
)
def login(
    payload: LoginRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> ResponseModel[TokenResponse]:
    try:
        user = authenticate_user(db, payload)
    except InvalidCredentialsError:
        raise ForbiddenError(
            message="Incorrect email or password.",
            code="invalid_credentials",
        )

    token = TokenResponse(access_token=create_access_token(subject=str(user.id)))
    set_auth_cookie(response, token.access_token)
    return ok(data=token, message="Login successful.")


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and clear the auth cookie",
)
def logout(
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    clear_auth_cookie(response)


@router.get(
    "/me",
    response_model=ResponseModel[UserRead],
    summary="Get the currently authenticated user",
)
def me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResponseModel[UserRead]:
    return ok(data=current_user)