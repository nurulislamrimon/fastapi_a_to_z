from sqlalchemy import select
from sqlalchemy.orm import Session

from common.filters import query_list
from common.response import PaginationMeta
from database.s3 import (
    delete_file,
    generate_object_key,
    get_presigned_url,
    upload_file,
)
from common.upload import validate_upload_file
from config.settings import settings
from modules.media.model import Media
from modules.media.schemas import MediaListParams

SEARCH_COLUMNS = [Media.original_filename, Media.mime_type]

FILTER_COLUMNS = {
    "mime_type": Media.mime_type,
}

RANGE_COLUMNS = {
    "size_gte": (Media.size, "gte"),
    "size_lte": (Media.size, "lte"),
    "created_from": (Media.created_at, "gte"),
    "created_to": (Media.created_at, "lte"),
}

SORT_COLUMNS = {
    "id": Media.id,
    "original_filename": Media.original_filename,
    "size": Media.size,
    "mime_type": Media.mime_type,
    "created_at": Media.created_at,
}


async def upload_media(
    db: Session,
    file,
    uploader_id: int,
) -> Media:
    size_bytes = await validate_upload_file(file)

    object_key = generate_object_key(uploader_id, file.filename or "unnamed")
    upload_file(file, object_key)

    media = Media(
        original_filename=file.filename or "unnamed",
        object_key=object_key,
        mime_type=file.content_type or "application/octet-stream",
        size=size_bytes,
        bucket=settings.s3_bucket,
        uploader_id=uploader_id,
    )

    db.add(media)
    db.commit()
    db.refresh(media)

    return media


def get_media_by_id(db: Session, media_id: int) -> Media | None:
    return db.get(Media, media_id)


def attach_download_url(media: Media) -> Media:
    media.download_url = get_presigned_url(media.object_key)
    return media


def get_user_media(
    db: Session,
    user_id: int,
    params: MediaListParams,
) -> tuple[list[Media], PaginationMeta]:
    return query_list(
        db,
        select(Media).where(Media.uploader_id == user_id),
        params,
        search_columns=SEARCH_COLUMNS,
        filter_columns=FILTER_COLUMNS,
        range_columns=RANGE_COLUMNS,
        sort_columns=SORT_COLUMNS,
    )


def delete_media(db: Session, media_id: int) -> bool:
    media = db.get(Media, media_id)
    if media is None:
        return False

    delete_file(media.object_key)
    db.delete(media)
    db.commit()

    return True
