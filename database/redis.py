from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from config.settings import settings

_client: Redis | None = None


def get_redis() -> Redis:
    global _client

    if _client is None:
        _client = Redis.from_url(
            settings.redis_url or "redis://localhost:6379/0",
            decode_responses=True,
        )

    return _client


def close_redis() -> None:
    global _client

    if _client is not None:
        _client.close()
        _client = None


def check_redis() -> bool:
    try:
        return bool(get_redis().ping())
    except RedisError:
        return False


def cache_get(key: str) -> str | None:
    try:
        return get_redis().get(key)
    except RedisError:
        return None


def cache_set(key: str, value: Any, *, ttl: int | None = None) -> None:
    try:
        if ttl is not None:
            get_redis().setex(key, ttl, value)
        else:
            get_redis().set(key, value)
    except RedisError:
        pass


def cache_delete(*keys: str) -> None:
    if not keys:
        return
    try:
        get_redis().delete(*keys)
    except RedisError:
        pass


def cache_delete_pattern(pattern: str) -> None:
    try:
        client = get_redis()
        for key in client.scan_iter(pattern):
            client.delete(key)
    except RedisError:
        pass
