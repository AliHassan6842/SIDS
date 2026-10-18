import numpy as np

from sids_ai.core.config import Settings
from sids_ai.image.quality import assess_quality
from sids_ai.schemas import ValidationReason


def test_dark_frame_is_rejected() -> None:
    result = assess_quality(np.zeros((320, 320, 3), dtype=np.uint8), Settings())
    assert result.reason is ValidationReason.TOO_DARK


def test_flat_frame_is_not_an_insect_candidate() -> None:
    result = assess_quality(np.full((320, 320, 3), 120, dtype=np.uint8), Settings(blur_variance_min=0))
    assert result.reason is ValidationReason.SUBJECT_TOO_SMALL
    assert not result.insect_candidate


def test_smooth_mid_exposure_frame_is_rejected_as_blurry() -> None:
    import cv2

    y, x = np.indices((320, 320))
    checkerboard = (((y // 32 + x // 32) % 2) * 255).astype(np.uint8)
    blurred = cv2.GaussianBlur(checkerboard, (0, 0), 3)
    rgb = np.repeat(blurred[:, :, np.newaxis], 3, axis=2)

    result = assess_quality(rgb, Settings())

    assert result.reason is ValidationReason.TOO_BLURRY
    assert not result.valid
