from sqlalchemy.orm import Session

from modules.users.model import User


def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()


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
