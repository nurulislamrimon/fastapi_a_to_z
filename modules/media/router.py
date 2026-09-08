from typing import Annotated

from fastapi import APIRouter, Depends, Query, UploadFile, status
from sqlalchemy.orm import Session

from common.exceptions import ForbiddenError, NotFoundError
from common.response import ResponseModel, ok
from database.session import get_db
from modules.auth.dependencies import get_current_user
from modules.media.schemas import MediaListParams, MediaRead
from modules.media.service import (
    attach_download_url,
    delete_media,
    get_media_by_id,
    get_user_media,
    upload_media,
)
from modules.users.model import User

router = APIRouter(prefix="/media", tags=["Media"])


@router.post(
    "/upload",
    response_model=ResponseModel[MediaRead],
    status_code=201,
    summary="Upload a file",
)
async def upload_file(
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResponseModel[MediaRead]:
    media = await upload_media(db, file, current_user.id)
    media.download_url = None
    return ok(data=media, message="File uploaded successfully.")


@router.get(
    "/",
    response_model=ResponseModel[list[MediaRead]],
    summary="List the current user's files",
)
def list_media(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    params: Annotated[MediaListParams, Query()] = MediaListParams(),
) -> ResponseModel[list[MediaRead]]:
    items, meta = get_user_media(db, current_user.id, params)
    return ok(data=items, meta=meta)


@router.get(
    "/{media_id}",
    response_model=ResponseModel[MediaRead],
    summary="Get file details with download URL",
)
def get_media(
    media_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResponseModel[MediaRead]:
    media = get_media_by_id(db, media_id)
    if not media:
        raise NotFoundError(message="Media not found.", code="media_not_found")

    if media.uploader_id != current_user.id:
        raise ForbiddenError(
            message="You do not have permission to view this file.",
            code="not_file_owner",
        )

    attach_download_url(media)
    return ok(data=media)


@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a file",
)
def delete_file(
    media_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    media = get_media_by_id(db, media_id)
    if not media:
        raise NotFoundError(message="Media not found.", code="media_not_found")

    if media.uploader_id != current_user.id:
        raise ForbiddenError(
            message="You do not have permission to delete this file.",
            code="not_file_owner",
        )

    delete_media(db, media_id)
