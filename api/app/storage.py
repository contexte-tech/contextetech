"""Stockage des gros datasets sur Scaleway Object Storage (API S3)."""
from functools import lru_cache

from starlette.concurrency import run_in_threadpool

from .config import get_settings


@lru_cache
def _client():
    import boto3

    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.s3_endpoint,
        region_name=s.s3_region,
        aws_access_key_id=s.s3_access_key,
        aws_secret_access_key=s.s3_secret_key,
    )


async def put_file(key: str, path: str, content_type: str = "application/x-ndjson") -> None:
    s = get_settings()
    await run_in_threadpool(
        _client().upload_file, path, s.s3_bucket, key, ExtraArgs={"ContentType": content_type}
    )


async def presigned_url(key: str, filename: str, seconds: int = 600) -> str:
    s = get_settings()
    return await run_in_threadpool(
        _client().generate_presigned_url,
        "get_object",
        Params={"Bucket": s.s3_bucket, "Key": key,
                "ResponseContentDisposition": f'attachment; filename="{filename}"'},
        ExpiresIn=seconds,
    )


async def delete(key: str) -> None:
    s = get_settings()
    await run_in_threadpool(_client().delete_object, Bucket=s.s3_bucket, Key=key)
