"""
Image I/O module with security checks and object storage adapter.
"""

from .decoder import decode_image
from .sanitizer import SecurityError, validate_image, validate_path_traversal
from .storage import ObjectStorageClient, StorageError

__all__ = [
    "decode_image",
    "validate_image",
    "validate_path_traversal",
    "SecurityError",
    "ObjectStorageClient",
    "StorageError",
]

