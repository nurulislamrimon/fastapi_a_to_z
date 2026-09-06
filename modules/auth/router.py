from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from modules.auth.dependencies import get_current_user
from modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from modules.auth.security import create_access_token
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
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(
    payload: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        return register_user(db, payload)
    except DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive an access token",
)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    try:
        user = authenticate_user(db, payload)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(subject=str(user.id)))


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the currently authenticated user",
)
def me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user