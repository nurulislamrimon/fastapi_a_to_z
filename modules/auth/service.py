from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.auth.schemas import LoginRequest, RegisterRequest
from modules.auth.security import hash_password, verify_password
from modules.users.model import User


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def register_user(db: Session, payload: RegisterRequest) -> User:
    existing = get_user_by_email(db, payload.email)
    if existing is not None:
        raise DuplicateEmailError

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, payload: LoginRequest) -> User:
    user = get_user_by_email(db, payload.email)

    if user is None or not verify_password(payload.password, user.password_hash):
        raise InvalidCredentialsError

    return user