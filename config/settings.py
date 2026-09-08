from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    app_env: str = "development"
    debug: bool = False

    database_url: str

    redis_url: str | None = None

    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    auth_cookie_name: str = "access_token"
    auth_cookie_secure: bool = False
    auth_cookie_samesite: str = "lax"

    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str = "media"
    s3_region: str = "us-east-1"
    s3_secure: bool = False
    s3_presigned_url_expiry: int = 3600

    upload_max_size_mb: int = 10
    upload_allowed_mime_types: Annotated[
        list[str],
        NoDecode,
    ] = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
    ]

    @field_validator("s3_secure", mode="before")
    @classmethod
    def parse_bool(cls, v: str | bool) -> bool:
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return v

    @field_validator("upload_allowed_mime_types", mode="before")
    @classmethod
    def parse_mime_list(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            if v.strip().startswith("["):
                import json

                return json.loads(v)
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()