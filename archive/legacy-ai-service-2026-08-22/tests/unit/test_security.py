import io
from pathlib import Path

import pytest
from PIL import Image
from sids_ai.image_io.decoder import decode_image
from sids_ai.image_io.sanitizer import (
    SecurityError,
    validate_image,
    validate_path_traversal,
)


def create_dummy_image(format='JPEG', width=100, height=100):
    img = Image.new('RGB', (width, height), color='red')
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()

def test_path_traversal():
    base = Path("/safe/dir")
    
    # Safe path
    # Note: On Windows, /safe/dir will be anchored to the current drive.
    # To make this cross-platform for testing, we can use a relative base or tmp_path
    # we'll implement this properly below

def test_path_traversal_with_tmp_path(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    
    # Safe path
    safe_path = validate_path_traversal(str(base), "sub/file.txt")
    assert str(safe_path).startswith(str(base.resolve()))
    
    # Unsafe path
    with pytest.raises(SecurityError):
        validate_path_traversal(str(base), "../outside.txt")
        
    with pytest.raises(SecurityError):
        validate_path_traversal(str(base), "sub/../../outside.txt")

def test_validate_image_success():
    data = create_dummy_image('JPEG', 800, 600)
    assert validate_image(data) is True
    
def test_validate_image_oversized():
    # Max dimension is 10000
    data = create_dummy_image('JPEG', 10001, 100)
    with pytest.raises(SecurityError, match="dimensions exceed"):
        validate_image(data)

def test_validate_image_disallowed_format():
    # TIFF is not in ALLOWED_FORMATS
    data = create_dummy_image('TIFF', 800, 600)
    with pytest.raises(SecurityError, match="Disallowed image format"):
        validate_image(data)

def test_validate_image_non_image():
    data = b"This is a text file, not an image"
    with pytest.raises(SecurityError, match="Invalid image file"):
        validate_image(data)

def test_decode_image_success():
    data = create_dummy_image('PNG', 100, 100)
    img = decode_image(data)
    assert img.width == 100
    assert img.height == 100
    assert img.mode == 'RGB'
