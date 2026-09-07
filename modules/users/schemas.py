from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from common.filters import PageAndSearchParams


class UserQueryParams(PageAndSearchParams):
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None

    age_gte: int | None = Field(default=None, ge=0)
    age_lte: int | None = Field(default=None, ge=0)

    created_from: datetime | None = None
    created_to: datetime | None = None


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    age: int | None = Field(default=None, ge=0)
    is_active: bool | None = None