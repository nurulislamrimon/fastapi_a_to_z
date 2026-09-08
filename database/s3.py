import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError
from fastapi import UploadFile

from common.exceptions import ServiceUnavailableError
from config.settings import settings

_client = None


def get_s3_client():
    global _client

    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=Config(
                connect_timeout=5,
                read_timeout=30,
                retries={"max_attempts": 2, "mode": "standard"},
                signature_version="s3v4",
            ),
        )

    return _client


def ensure_bucket() -> None:
    client = get_s3_client()

    try:
        client.head_bucket(Bucket=settings.s3_bucket)
        return
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code not in ("404", "NoSuchBucket", "NotFound"):
            raise ServiceUnavailableError(
                message="Object storage is unavailable.",
                code="storage_unavailable",
            ) from exc
    except EndpointConnectionError as exc:
        raise ServiceUnavailableError(
            message="Object storage is unavailable.",
            code="storage_unavailable",
        ) from exc

    client.create_bucket(
        Bucket=settings.s3_bucket,
        CreateBucketConfiguration={"LocationConstraint": settings.s3_region}
        if settings.s3_region != "us-east-1"
        else {},
    )


def generate_object_key(user_id: int, filename: str) -> str:
    safe_name = "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in filename)
    return f"{user_id}/{uuid.uuid4().hex}_{safe_name}"


def _storage_ok() -> None:
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        ensure_bucket()
    except EndpointConnectionError as exc:
        raise ServiceUnavailableError(
            message="Object storage is unavailable.",
            code="storage_unavailable",
        ) from exc


def upload_file(file: UploadFile, object_key: str) -> dict:
    client = get_s3_client()

    try:
        _storage_ok()
        file.file.seek(0)
        client.upload_fileobj(
            file.file,
            settings.s3_bucket,
            object_key,
            ExtraArgs={
                "ContentType": file.content_type or "application/octet-stream",
            },
        )
    except (ClientError, EndpointConnectionError) as exc:
        raise ServiceUnavailableError(
            message="Object storage is unavailable.",
            code="storage_unavailable",
        ) from exc

    return {
        "bucket": settings.s3_bucket,
        "object_key": object_key,
    }


def get_presigned_url(object_key: str) -> str:
    client = get_s3_client()

    try:
        return client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.s3_bucket,
                "Key": object_key,
            },
            ExpiresIn=settings.s3_presigned_url_expiry,
        )
    except (ClientError, EndpointConnectionError) as exc:
        raise ServiceUnavailableError(
            message="Object storage is unavailable.",
            code="storage_unavailable",
        ) from exc


def delete_file(object_key: str) -> bool:
    client = get_s3_client()

    try:
        client.delete_object(Bucket=settings.s3_bucket, Key=object_key)
        return True
    except (ClientError, EndpointConnectionError):
        return False


def list_files(prefix: str = "", max_keys: int = 1000) -> list[dict]:
    client = get_s3_client()

    try:
        response = client.list_objects_v2(
            Bucket=settings.s3_bucket,
            Prefix=prefix,
            MaxKeys=max_keys,
        )
    except (ClientError, EndpointConnectionError) as exc:
        raise ServiceUnavailableError(
            message="Object storage is unavailable.",
            code="storage_unavailable",
        ) from exc

    return [
        {
            "key": obj["Key"],
            "size": obj["Size"],
            "last_modified": obj["LastModified"],
        }
        for obj in response.get("Contents", [])
    ]


def copy_file(source_key: str, dest_key: str) -> bool:
    client = get_s3_client()

    try:
        client.copy_object(
            Bucket=settings.s3_bucket,
            CopySource={"Bucket": settings.s3_bucket, "Key": source_key},
            Key=dest_key,
        )
        return True
    except (ClientError, EndpointConnectionError):
        return False


def move_file(source_key: str, dest_key: str) -> bool:
    if copy_file(source_key, dest_key):
        return delete_file(source_key)
    return False


def check_s3() -> bool:
    try:
        _storage_ok()
        return True
    except (ClientError, EndpointConnectionError, ServiceUnavailableError):
        return False