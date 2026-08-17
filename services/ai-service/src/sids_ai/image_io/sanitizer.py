import io
from pathlib import Path

from PIL import Image

MAX_IMAGE_PIXELS = 89478485  # Default PIL limit
MAX_DIMENSION = 10000
ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP'}

class SecurityError(Exception):
    pass

def validate_path_traversal(base_dir: str, file_path: str) -> Path:
    """Ensure that the file_path resolves within the base_dir to prevent path traversal."""
    base = Path(base_dir).resolve()
    # If file_path is absolute and outside base, Path(base, file_path).resolve() will just be file_path.resolve() on some OS
    # Wait, on Windows Path("C:/base", "D:/target") is D:/target. 
    # Best way: join them safely.
    target = (base / file_path).resolve()
    
    if not str(target).startswith(str(base)):
        raise SecurityError(f"Path traversal detected: {file_path}")
    return target

def validate_image(file_data: bytes) -> bool:
    """Validate image codec and dimensions, rejecting non-images or oversized files."""
    try:
        Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
        with Image.open(io.BytesIO(file_data)) as img:
            img.verify()  # verify format/codec without fully decoding
            
            if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
                raise SecurityError(f"Image dimensions exceed maximum allowed ({MAX_DIMENSION}x{MAX_DIMENSION})")
                
            if img.format not in ALLOWED_FORMATS:
                raise SecurityError(f"Disallowed image format: {img.format}")
                
        return True
    except SecurityError:
        raise
    except Exception as e:
        raise SecurityError(f"Invalid image file: {e}")
