from alembic import context

from config.settings import settings

config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.database_url,
)