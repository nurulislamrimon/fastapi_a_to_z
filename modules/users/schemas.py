from pydantic import BaseModel, ConfigDict, EmailStr

from common.filters import PageAndSearchParams


class UserQueryParams(PageAndSearchParams):
    name: str | None = None
    email: str | None = None


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None