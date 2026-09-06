from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from config.settings import settings

DATABASE_URL = settings.database_url 

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def check_database() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True

    except Exception:
        return False