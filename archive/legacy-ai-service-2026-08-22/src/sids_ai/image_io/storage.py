"""
Object storage client for S3/MinIO compatible image storage in SIDS.
"""

import logging
import mimetypes
import os
from typing import Any

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from sids_ai.core.config import settings

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Exception raised for storage-related operations."""

    pass


class ObjectStorageClient:
    """Client for interacting with S3 / MinIO object storage."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        bucket_name: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        region_name: str | None = None,
        s3_client: Any = None,
    ) -> None:
        self.endpoint_url = (
            endpoint_url
            or os.getenv("STORAGE_ENDPOINT")
            or os.getenv("AWS_ENDPOINT_URL_S3")
            or os.getenv("AWS_ENDPOINT_URL")
            or getattr(settings, "storage_endpoint", None)
        )
        self.bucket_name = (
            bucket_name
            or os.getenv("STORAGE_BUCKET")
            or os.getenv("AWS_STORAGE_BUCKET_NAME")
            or os.getenv("S3_BUCKET_NAME")
            or getattr(settings, "storage_bucket", "sids-images")
        )
        self.access_key = (
            access_key
            or os.getenv("STORAGE_ACCESS_KEY")
            or os.getenv("AWS_ACCESS_KEY_ID")
            or getattr(settings, "storage_access_key", None)
        )
        self.secret_key = (
            secret_key
            or os.getenv("STORAGE_SECRET_KEY")
            or os.getenv("AWS_SECRET_ACCESS_KEY")
            or getattr(settings, "storage_secret_key", None)
        )
        self.region_name = (
            region_name
            or os.getenv("STORAGE_REGION")
            or os.getenv("AWS_DEFAULT_REGION")
            or os.getenv("AWS_REGION")
            or getattr(settings, "storage_region", "us-east-1")
        )

        if s3_client is not None:
            self._s3_client = s3_client
        else:
            client_kwargs: dict[str, Any] = {
                "service_name": "s3",
                "region_name": self.region_name,
                "config": Config(
                    signature_version="s3v4",
                    s3={"addressing_style": "path"},
                ),
            }
            if self.endpoint_url:
                client_kwargs["endpoint_url"] = self.endpoint_url
            if self.access_key and self.secret_key:
                client_kwargs["aws_access_key_id"] = self.access_key
                client_kwargs["aws_secret_access_key"] = self.secret_key

            self._s3_client = boto3.client(**client_kwargs)

    @property
    def client(self) -> Any:
        """Get the underlying boto3 client."""
        return self._s3_client

    def upload_image(
        self,
        file_bytes: bytes,
        object_name: str,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload image bytes to S3/MinIO bucket.

        Args:
            file_bytes: Raw image bytes to upload.
            object_name: S3 key/object name.
            content_type: MIME type of the image. Auto-detected from object_name if None.
            metadata: Optional user metadata key-value dict.

        Returns:
            The object_name key upon successful upload.
        """
        if not file_bytes:
            raise StorageError("Cannot upload empty file bytes")
        if not object_name:
            raise StorageError("Object name must be specified")

        if content_type is None:
            guessed_type, _ = mimetypes.guess_type(object_name)
            content_type = guessed_type or "image/jpeg"

        extra_args: dict[str, Any] = {
            "Bucket": self.bucket_name,
            "Key": object_name,
            "Body": file_bytes,
            "ContentType": content_type,
        }
        if metadata:
            extra_args["Metadata"] = metadata

        try:
            self._s3_client.put_object(**extra_args)
            logger.info("Successfully uploaded %s to bucket %s", object_name, self.bucket_name)
            return object_name
        except ClientError as e:
            logger.error("Failed to upload %s: %s", object_name, e)
            raise StorageError(f"Failed to upload image {object_name}: {e}") from e
        except Exception as e:
            logger.error("Unexpected error uploading %s: %s", object_name, e)
            raise StorageError(f"Unexpected error uploading image {object_name}: {e}") from e

    def get_image_url(self, object_name: str, expires_in: int = 3600) -> str:
        """Generate a presigned GET URL for an object in the bucket.

        Args:
            object_name: S3 key/object name.
            expires_in: Expiration time in seconds (default: 3600).

        Returns:
            Presigned URL string to download/view the image.
        """
        if not object_name:
            raise StorageError("Object name must be specified")

        try:
            url = self._s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_name,
                },
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error("Failed to generate URL for %s: %s", object_name, e)
            raise StorageError(f"Failed to generate URL for {object_name}: {e}") from e
        except Exception as e:
            logger.error("Unexpected error generating URL for %s: %s", object_name, e)
            raise StorageError(f"Unexpected error generating URL for {object_name}: {e}") from e

    def get_image_bytes(self, object_name: str) -> bytes:
        """Download image bytes from S3/MinIO bucket.

        Args:
            object_name: S3 key/object name.

        Returns:
            Raw bytes of the retrieved image.
        """
        if not object_name:
            raise StorageError("Object name must be specified")

        try:
            response = self._s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_name,
            )
            return response["Body"].read()
        except ClientError as e:
            logger.error("Failed to download %s: %s", object_name, e)
            raise StorageError(f"Failed to download image {object_name}: {e}") from e
        except Exception as e:
            logger.error("Unexpected error downloading %s: %s", object_name, e)
            raise StorageError(f"Unexpected error downloading image {object_name}: {e}") from e

    def delete_image(self, object_name: str) -> bool:
        """Delete an image from the bucket.

        Args:
            object_name: S3 key/object name.

        Returns:
            True if deletion succeeded.
        """
        if not object_name:
            raise StorageError("Object name must be specified")

        try:
            self._s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name,
            )
            return True
        except ClientError as e:
            logger.error("Failed to delete %s: %s", object_name, e)
            raise StorageError(f"Failed to delete image {object_name}: {e}") from e
        except Exception as e:
            logger.error("Unexpected error deleting %s: %s", object_name, e)
            raise StorageError(f"Unexpected error deleting image {object_name}: {e}") from e
