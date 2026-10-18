from io import BytesIO

import pytest
from PIL import Image

from sids_ai.core.config import Settings
from sids_ai.core.errors import ImageRejected
from sids_ai.image.decoder import decode_and_sanitize


def image_bytes(color=(80, 130, 70), size=(320, 320), fmt="JPEG") -> bytes:
    output = BytesIO()
    Image.new("RGB", size, color).save(output, format=fmt)
    return output.getvalue()


def test_decodes_and_strips_metadata_by_reencoding() -> None:
    decoded = decode_and_sanitize(image_bytes(), "image/jpeg", Settings())
    assert decoded.rgb.shape == (320, 320, 3)
    assert decoded.sanitized_jpeg.startswith(b"\xff\xd8\xff")


@pytest.mark.parametrize("data,mime", [(b"not an image", "image/jpeg"), (image_bytes(), "text/plain")])
def test_rejects_malformed_or_mismatched_input(data: bytes, mime: str) -> None:
    with pytest.raises(ImageRejected) as error:
        decode_and_sanitize(data, mime, Settings())
    assert error.value.reason == "INVALID_IMAGE"


def test_rejects_oversized_pixel_count() -> None:
    with pytest.raises(ImageRejected):
        decode_and_sanitize(image_bytes(size=(1500, 1500)), "image/jpeg", Settings(max_image_pixels=1_000_000))
