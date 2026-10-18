"""Unit tests for ObjectStorageClient."""

from unittest.mock import MagicMock
import pytest
from botocore.exceptions import ClientError

from sids_ai.image_io.storage import ObjectStorageClient, StorageError


@pytest.fixture
def mock_s3_client():
    return MagicMock()


@pytest.fixture
def storage_client(mock_s3_client):
    return ObjectStorageClient(
        endpoint_url="http://localhost:9000",
        bucket_name="test-bucket",
        access_key="test-key",
        secret_key="test-secret",
        region_name="us-east-1",
        s3_client=mock_s3_client,
    )


def test_storage_client_initialization(monkeypatch):
    monkeypatch.setenv("STORAGE_ENDPOINT", "http://minio.local:9000")
    monkeypatch.setenv("STORAGE_BUCKET", "custom-bucket")
    monkeypatch.setenv("STORAGE_ACCESS_KEY", "minioadmin")
    monkeypatch.setenv("STORAGE_SECRET_KEY", "miniopass")
    monkeypatch.setenv("STORAGE_REGION", "eu-central-1")

    mock_boto = MagicMock()
    monkeypatch.setattr("boto3.client", mock_boto)

    client = ObjectStorageClient()
    assert client.endpoint_url == "http://minio.local:9000"
    assert client.bucket_name == "custom-bucket"
    assert client.access_key == "minioadmin"
    assert client.secret_key == "miniopass"
    assert client.region_name == "eu-central-1"
    mock_boto.assert_called_once()


def test_upload_image_success(storage_client, mock_s3_client):
    dummy_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    object_name = "test/pest_001.jpg"

    mock_s3_client.put_object.return_value = {"ETag": '"test-etag"'}

    result = storage_client.upload_image(dummy_bytes, object_name)

    assert result == object_name
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="test-bucket",
        Key=object_name,
        Body=dummy_bytes,
        ContentType="image/jpeg",
    )


def test_upload_image_with_custom_content_type_and_metadata(storage_client, mock_s3_client):
    dummy_bytes = b"<svg>test</svg>"
    object_name = "annotated.svg"
    metadata = {"diagnosis": "stem_borer", "confidence": "0.95"}

    storage_client.upload_image(
        file_bytes=dummy_bytes,
        object_name=object_name,
        content_type="image/svg+xml",
        metadata=metadata,
    )

    mock_s3_client.put_object.assert_called_once_with(
        Bucket="test-bucket",
        Key=object_name,
        Body=dummy_bytes,
        ContentType="image/svg+xml",
        Metadata=metadata,
    )


def test_upload_image_empty_bytes(storage_client):
    with pytest.raises(StorageError, match="Cannot upload empty file bytes"):
        storage_client.upload_image(b"", "empty.jpg")


def test_upload_image_empty_key(storage_client):
    with pytest.raises(StorageError, match="Object name must be specified"):
        storage_client.upload_image(b"data", "")


def test_upload_image_client_error(storage_client, mock_s3_client):
    mock_s3_client.put_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchBucket", "Message": "The specified bucket does not exist"}},
        "PutObject",
    )

    with pytest.raises(StorageError, match="Failed to upload image"):
        storage_client.upload_image(b"data", "test.jpg")


def test_get_image_url_success(storage_client, mock_s3_client):
    expected_url = "https://test-bucket.s3.amazonaws.com/test/pest_001.jpg?token=mock123"
    mock_s3_client.generate_presigned_url.return_value = expected_url

    url = storage_client.get_image_url("test/pest_001.jpg", expires_in=1800)

    assert url == expected_url
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        ClientMethod="get_object",
        Params={"Bucket": "test-bucket", "Key": "test/pest_001.jpg"},
        ExpiresIn=1800,
    )


def test_get_image_url_empty_key(storage_client):
    with pytest.raises(StorageError, match="Object name must be specified"):
        storage_client.get_image_url("")


def test_get_image_url_client_error(storage_client, mock_s3_client):
    mock_s3_client.generate_presigned_url.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
        "GeneratePresignedUrl",
    )

    with pytest.raises(StorageError, match="Failed to generate URL"):
        storage_client.get_image_url("test.jpg")


def test_get_image_bytes_success(storage_client, mock_s3_client):
    image_data = b"raw-image-bytes"
    mock_body = MagicMock()
    mock_body.read.return_value = image_data
    mock_s3_client.get_object.return_value = {"Body": mock_body}

    data = storage_client.get_image_bytes("test/pest_001.jpg")

    assert data == image_data
    mock_s3_client.get_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="test/pest_001.jpg",
    )


def test_delete_image_success(storage_client, mock_s3_client):
    mock_s3_client.delete_object.return_value = {"DeleteMarker": True}

    result = storage_client.delete_image("test/pest_001.jpg")

    assert result is True
    mock_s3_client.delete_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="test/pest_001.jpg",
    )
