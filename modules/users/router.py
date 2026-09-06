from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from common.exceptions import NotFoundError
from common.response import ResponseModel, ok
from database.session import get_db
from modules.auth.dependencies import get_current_user
from modules.users.model import User
from modules.users.schemas import UserQueryParams, UserRead, UserUpdate
from modules.users.service import (
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=ResponseModel[list[UserRead]],
    summary="Get all users",
)
def list_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    params: Annotated[UserQueryParams, Query()] = UserQueryParams(),
) -> ResponseModel[list[UserRead]]:
    items, meta = get_all_users(db, params)
    return ok(data=items, meta=meta)


@router.get(
    "/{user_id}",
    response_model=ResponseModel[UserRead],
    summary="Get a user by ID",
)
def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResponseModel[UserRead]:
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError(message="User not found.", code="user_not_found")
    return ok(data=user)


@router.patch(
    "/{user_id}",
    response_model=ResponseModel[UserRead],
    summary="Update a user",
)
def update_user_route(
    user_id: int,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResponseModel[UserRead]:
    user = update_user(
        db,
        user_id,
        name=payload.name,
        email=payload.email,
    )
    if not user:
        raise NotFoundError(message="User not found.", code="user_not_found")
    return ok(data=user, message="User updated successfully.")


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
def delete_user_route(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    if not delete_user(db, user_id):
        raise NotFoundError(message="User not found.", code="user_not_found")
