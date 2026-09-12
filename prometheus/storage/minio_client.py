"""
prometheus/storage/minio_client.py
MinIO object storage client for raw scraped data.
"""
from __future__ import annotations

import io
import json
import logging
from datetime import datetime, timezone
from typing import Any

from minio import Minio
from minio.error import S3Error

from prometheus.config import settings

logger = logging.getLogger(__name__)


class MinIOClient:
    """Thin wrapper around the MinIO Python SDK."""

    def __init__(self) -> None:
        endpoint = settings.MINIO_ENDPOINT
        # Strip http:// or https:// if present (minio SDK wants host:port only)
        endpoint = endpoint.replace("http://", "").replace("https://", "")
        self._client = Minio(
            endpoint=endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    def ensure_bucket(self, bucket_name: str) -> None:
        """Create the bucket if it does not already exist."""
        try:
            if not self._client.bucket_exists(bucket_name):
                self._client.make_bucket(bucket_name)
                logger.info("MinIO bucket created: %s", bucket_name)
            else:
                logger.debug("MinIO bucket already exists: %s", bucket_name)
        except S3Error as exc:
            logger.error("MinIO ensure_bucket failed: %s", exc)
            raise

    def upload_json(self, bucket: str, key: str, data: Any) -> None:
        """Serialize data to JSON and upload to MinIO."""
        payload = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        stream = io.BytesIO(payload)
        try:
            self._client.put_object(
                bucket_name=bucket,
                object_name=key,
                data=stream,
                length=len(payload),
                content_type="application/json",
            )
            logger.info("Uploaded %s/%s (%d bytes)", bucket, key, len(payload))
        except S3Error as exc:
            logger.error("MinIO upload_json failed for %s/%s: %s", bucket, key, exc)
            raise

    def download_json(self, bucket: str, key: str) -> Any:
        """Download a JSON object from MinIO and deserialize it."""
        try:
            response = self._client.get_object(bucket_name=bucket, object_name=key)
            data = json.loads(response.read())
            response.close()
            response.release_conn()
            logger.info("Downloaded %s/%s", bucket, key)
            return data
        except S3Error as exc:
            logger.error("MinIO download_json failed for %s/%s: %s", bucket, key, exc)
            raise

    def list_objects(self, bucket: str, prefix: str = "") -> list[str]:
        """Return a list of object keys matching the prefix."""
        try:
            objs = self._client.list_objects(bucket_name=bucket, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objs]
        except S3Error as exc:
            logger.error("MinIO list_objects failed for %s/%s: %s", bucket, prefix, exc)
            raise

    def check_connection(self) -> bool:
        """Verify MinIO is reachable by listing buckets."""
        try:
            self._client.list_buckets()
            return True
        except Exception as exc:
            logger.error("MinIO connection check failed: %s", exc)
            return False


def make_raw_key(origin: str, destination: str) -> str:
    """Generate a MinIO object key for a raw scrape result."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"raw/{date}/{origin}_{destination}_{ts}.json"


# Module-level singleton — created lazily so import doesn't fail if MinIO is down
_client: MinIOClient | None = None


def get_minio_client() -> MinIOClient:
    global _client
    if _client is None:
        _client = MinIOClient()
    return _client
