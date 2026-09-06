import random
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

import database.base  # noqa: F401
from database.seeds.user import FIRST_NAMES, LAST_NAMES
from database.session import SessionLocal
from modules.users.model import User

DEFAULT_COUNT = 25


def generate_users(count: int) -> list[User]:
    users: list[User] = []
    used_emails: set[str] = set()

    for _ in range(count):
        email = None
        while email is None or email in used_emails:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            email = f"{first.lower()}.{last.lower()}@example.com"

        used_emails.add(email)
        users.append(User(name=f"{first} {last}", email=email))

    return users


def seed_users(db: Session, count: int) -> int:
    users = generate_users(count)
    existing_emails = set(db.scalars(select(User.email)).all())

    new_users = [user for user in users if user.email not in existing_emails]
    if not new_users:
        return 0

    db.add_all(new_users)
    db.commit()

    return len(new_users)


def seed_all(db: Session, count: int) -> None:
    seeded_users = seed_users(db, count)
    print(f"Seeded {seeded_users} new users.")


def main() -> None:
    count = DEFAULT_COUNT

    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print(f"Invalid count: {sys.argv[1]!r}. Using default of {DEFAULT_COUNT}.")

    with SessionLocal() as db:
        seed_all(db, count)


if __name__ == "__main__":
    main()