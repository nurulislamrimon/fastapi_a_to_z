from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from common.filters import PageAndSearchParams


class MediaRead(BaseModel):
    id: int
    original_filename: str
    mime_type: str
    size: int
    download_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MediaListParams(PageAndSearchParams):
    mime_type: str | None = None
    size_gte: int | None = Field(default=None, ge=0)
    size_lte: int | None = Field(default=None, ge=0)
    created_from: datetime | None = None
    created_to: datetime | None = None
