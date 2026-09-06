from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from modules.users.model import User
