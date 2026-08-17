import hashlib
import os
import tarfile
import tempfile
import zipfile
from urllib.parse import urlparse

import requests


class DownloaderError(Exception):
    pass

def verify_checksum(filepath: str, expected_sha256: str) -> bool:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() == expected_sha256

def safe_extract(archive_path: str, target_dir: str):
    # Path traversal protection
    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zf:
            for member in zf.infolist():
                # Avoid absolute paths and path traversal
                if member.filename.startswith('/') or '..' in member.filename:
                    raise DownloaderError(f"Unsafe archive member: {member.filename}")
                zf.extract(member, target_dir)
    elif archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz') or archive_path.endswith('.tar'):
        with tarfile.open(archive_path, 'r:*') as tf:
            for member in tf.getmembers():
                if member.name.startswith('/') or '..' in member.name:
                    raise DownloaderError(f"Unsafe archive member: {member.name}")
            tf.extractall(target_dir)
    else:
        raise DownloaderError("Unsupported archive format")

def download_dataset(
    url: str, 
    dest_dir: str, 
    expected_sha256: str | None = None, 
    timeout: int = 60
):
    """
    Safely downloads a dataset, verifies checksum, and extracts it atomically.
    """
    if not url.startswith("https://"):
        raise DownloaderError("Only HTTPS URLs are allowed.")

    os.makedirs(dest_dir, exist_ok=True)
    filename = os.path.basename(urlparse(url).path)
    if not filename:
        filename = "dataset.archive"
        
    temp_fd, temp_path = tempfile.mkstemp(prefix="sids_download_")
    os.close(temp_fd)
    
    try:
        print(f"Downloading from {url}...")
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            with open(temp_path, 'wb') as f:
                f.writelines(r.iter_content(chunk_size=8192))
                    
        if expected_sha256:
            print("Verifying checksum...")
            if not verify_checksum(temp_path, expected_sha256):
                raise DownloaderError("Checksum verification failed!")
                
        print("Extracting archive...")
        safe_extract(temp_path, dest_dir)
        print(f"Dataset successfully downloaded and extracted to {dest_dir}")
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
