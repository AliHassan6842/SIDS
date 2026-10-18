import hashlib
from pathlib import Path


def calculate_sha256(file_path: Path) -> str:
    """Calculates the SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_artifact_integrity(file_path: Path, expected_sha256: str) -> bool:
    """Verifies that a file's SHA-256 matches the expected value."""
    if not file_path.exists():
        return False
    actual_sha256 = calculate_sha256(file_path)
    return actual_sha256.lower() == expected_sha256.lower()
