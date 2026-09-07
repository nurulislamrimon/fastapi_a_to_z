from typing import Any, Callable, Mapping, Sequence

from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from common.response import PaginationMeta, paginate

Comparator = Callable[[object, Any], object]

COMPARISON_OPS: dict[str, Comparator] = {
    "gt": lambda column, value: column > value,
    "gte": lambda column, value: column >= value,
    "lt": lambda column, value: column < value,
    "lte": lambda column, value: column <= value,
}


class PageAndSearchParams(BaseModel):
    search: str | None = Field(default=None, max_length=100)
    sort: str | None = Field(
        default=None,
        max_length=200,
        description="Comma-separated sort fields; prefix a field with '-' for descending order.",
    )
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)


def apply_search(
    statement: Select,
    search: str | None,
    columns: Sequence[object],
) -> Select:
    if not search:
        return statement

    term = f"%{search.strip()}%"
    return statement.where(or_(*(column.ilike(term) for column in columns)))


def apply_exact_filters(
    statement: Select,
    conditions: Mapping[object, Any],
) -> Select:
    predicates = [
        column == value
        for column, value in conditions.items()
        if value is not None
    ]

    if not predicates:
        return statement

    return statement.where(*predicates)


def build_filter_conditions(
    params: PageAndSearchParams,
    filter_columns: Mapping[str, object],
) -> dict[object, Any]:
    return {
        column: getattr(params, field)
        for field, column in filter_columns.items()
    }


def build_range_conditions(
    params: PageAndSearchParams,
    range_columns: Mapping[str, tuple[object, str]],
) -> list[tuple[Any, object, str]]:
    return [
        (getattr(params, field), column, op)
        for field, (column, op) in range_columns.items()
        if getattr(params, field) is not None
    ]


def apply_range_filters(
    statement: Select,
    conditions: Sequence[tuple[Any, object, str]],
) -> Select:
    predicates = [
        COMPARISON_OPS[op](column, value)
        for value, column, op in conditions
    ]

    if not predicates:
        return statement

    return statement.where(*predicates)


def apply_sort(
    statement: Select,
    sort: str | None,
    columns: Mapping[str, object],
) -> Select:
    if not sort:
        return statement

    ordering = []
    for raw in sort.split(","):
        raw = raw.strip()
        if not raw:
            continue

        descending = raw.startswith("-")
        field = raw[1:] if descending else raw

        column = columns.get(field)
        if column is None:
            continue

        ordering.append(column.desc() if descending else column.asc())

    if not ordering:
        return statement

    return statement.order_by(*ordering)


def query_list(
    db: Session,
    statement: Select,
    params: PageAndSearchParams,
    *,
    search_columns: Sequence[object] | None = None,
    filter_columns: Mapping[str, object] | None = None,
    filter_conditions: Mapping[object, Any] | None = None,
    range_columns: Mapping[str, tuple[object, str]] | None = None,
    sort_columns: Mapping[str, object] | None = None,
) -> tuple[list[Any], PaginationMeta]:
    if search_columns:
        statement = apply_search(statement, params.search, search_columns)

    if filter_columns:
        filter_conditions = build_filter_conditions(params, filter_columns)

    if filter_conditions:
        statement = apply_exact_filters(statement, filter_conditions)

    if range_columns:
        statement = apply_range_filters(
            statement,
            build_range_conditions(params, range_columns),
        )

    if sort_columns:
        statement = apply_sort(statement, params.sort, sort_columns)

    return paginate(db, statement, params.page, params.limit)