from fastapi import UploadFile

from common.exceptions import BadRequestError
from config.settings import settings


async def validate_upload_file(file: UploadFile) -> int:
    if file.content_type not in settings.upload_allowed_mime_types:
        raise BadRequestError(
            message=f"File type '{file.content_type}' is not allowed.",
            code="invalid_file_type",
            details={
                "allowed": settings.upload_allowed_mime_types,
            },
        )

    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    file.file.seek(0)

    max_bytes = settings.upload_max_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise BadRequestError(
            message=f"File size exceeds the maximum limit of {settings.upload_max_size_mb}MB.",
            code="file_too_large",
            details={
                "max_size_mb": settings.upload_max_size_mb,
                "actual_size_bytes": size_bytes,
            },
        )

    if size_bytes == 0:
        raise BadRequestError(
            message="Uploaded file is empty.",
            code="empty_file",
        )

    return size_bytes
