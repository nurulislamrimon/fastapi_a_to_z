from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

T = TypeVar("T")


class PaginationMeta(BaseModel):
    limit: int
    page: int
    total: int
    pages: int


class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    message: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    meta: PaginationMeta | None = None
    data: T


def ok(
    data: T,
    *,
    message: str | None = None,
    meta: PaginationMeta | None = None,
) -> ResponseModel[T]:
    return ResponseModel(
        message=message,
        meta=meta,
        data=data,
    )


def paginate(
    db: Session,
    statement: object,
    page: int,
    limit: int,
) -> tuple[object, PaginationMeta]:
    page = max(page, 1)
    limit = max(limit, 1)

    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    pages = (total + limit - 1) // limit

    items = db.scalars(
        statement.offset((page - 1) * limit).limit(limit)
    ).all()

    meta = PaginationMeta(
        limit=limit,
        page=page,
        total=total,
        pages=pages,
    )

    return items, meta