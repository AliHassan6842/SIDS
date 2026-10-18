import io

from PIL import Image

from .sanitizer import SecurityError, validate_image


def decode_image(file_data: bytes) -> Image.Image:
    """Decodes image safely."""
    validate_image(file_data)
    try:
        # Reset pointer or reopen because verify() leaves file in undetermined state
        return Image.open(io.BytesIO(file_data)).convert('RGB')
    except Exception as e:
        raise SecurityError(f"Failed to decode image: {e}")
