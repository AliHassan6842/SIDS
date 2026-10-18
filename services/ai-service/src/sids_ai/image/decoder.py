from dataclasses import dataclass
from io import BytesIO

import numpy as np
from PIL import Image, ImageFile, UnidentifiedImageError

from sids_ai.core.config import Settings
from sids_ai.core.errors import ImageRejected

ImageFile.LOAD_TRUNCATED_IMAGES = False
Image.MAX_IMAGE_PIXELS = 20_000_000


@dataclass(frozen=True)
class DecodedImage:
    rgb: np.ndarray
    sanitized_jpeg: bytes


ALLOWED_MIME = {"image/jpeg", "image/png"}


def _valid_magic(data: bytes) -> bool:
    return data.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n"))


def decode_and_sanitize(data: bytes, content_type: str | None, settings: Settings) -> DecodedImage:
    if not data or len(data) > settings.max_upload_bytes:
        raise ImageRejected("INVALID_IMAGE", "Image is empty or exceeds the byte limit.")
    if content_type not in ALLOWED_MIME or not _valid_magic(data):
        raise ImageRejected("INVALID_IMAGE", "Only valid JPEG and PNG images are accepted.")

    try:
        with Image.open(BytesIO(data)) as probe:
            probe.verify()
        with Image.open(BytesIO(data)) as source:
            width, height = source.size
            if width * height > settings.max_image_pixels:
                raise ImageRejected("INVALID_IMAGE", "Decoded image exceeds the pixel limit.")
            if width < settings.min_width or height < settings.min_height:
                raise ImageRejected("SUBJECT_TOO_SMALL", "Image dimensions are too small.")
            rgb_image = source.convert("RGB")
            output = BytesIO()
            rgb_image.save(output, format="JPEG", quality=90, optimize=True)
            rgb = np.asarray(rgb_image, dtype=np.uint8)
    except ImageRejected:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ImageRejected("INVALID_IMAGE", "Image could not be safely decoded.") from exc

    return DecodedImage(rgb=rgb, sanitized_jpeg=output.getvalue())
