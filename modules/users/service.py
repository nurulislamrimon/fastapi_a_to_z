from sqlalchemy import select
from sqlalchemy.orm import Session

from common.filters import query_list
from common.response import PaginationMeta
from modules.users.variables import FILTER_COLUMNS, SEARCH_COLUMNS
from modules.users.model import User
from modules.users.schemas import UserQueryParams


def get_all_users(
    db: Session,
    params: UserQueryParams,
) -> tuple[list[User], PaginationMeta]:
    return query_list(
        db,
        select(User),
        params,
        search_columns=SEARCH_COLUMNS,
        filter_columns=FILTER_COLUMNS,
    )


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, user_id: int, name: str | None = None, email: str | None = None) -> User | None:
    user = db.get(User, user_id)
    if not user:
        return None

    if name is not None:
        user.name = name
    if email is not None:
        user.email = email

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = db.get(User, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True
