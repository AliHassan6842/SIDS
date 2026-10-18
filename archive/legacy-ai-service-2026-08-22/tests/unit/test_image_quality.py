import cv2
import numpy as np
from sids_ai.image_quality.blur import evaluate_blur
from sids_ai.image_quality.exposure import evaluate_exposure
from sids_ai.image_quality.resolution import evaluate_resolution
from sids_ai.image_quality.service import build_quality_result


def test_evaluate_resolution():
    issues = evaluate_resolution(200, 300, min_width=224, min_height=224)
    assert len(issues) == 1
    assert issues[0].code == "RESOLUTION_TOO_LOW"
    assert issues[0].measurement == 200.0
    assert issues[0].threshold == 224.0

    issues = evaluate_resolution(300, 300, min_width=224, min_height=224)
    assert len(issues) == 0

def test_evaluate_blur():
    # Create a perfectly uniform image (zero variance = blurry)
    img_blurry = np.zeros((100, 100, 3), dtype=np.uint8)
    issues = evaluate_blur(img_blurry, threshold=85.0)
    assert len(issues) == 1
    assert issues[0].code == "IMAGE_TOO_BLURRY"

    # Create a high variance image (checkerboard or random noise)
    img_sharp = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    issues = evaluate_blur(img_sharp, threshold=85.0)
    assert len(issues) == 0

def test_evaluate_exposure():
    # Very dark image
    img_dark = np.ones((100, 100, 3), dtype=np.uint8) * 10
    issues = evaluate_exposure(img_dark, min_threshold=40.0, max_threshold=220.0)
    assert len(issues) == 1
    assert issues[0].code == "UNDEREXPOSED"

    # Very bright image
    img_bright = np.ones((100, 100, 3), dtype=np.uint8) * 240
    issues = evaluate_exposure(img_bright, min_threshold=40.0, max_threshold=220.0)
    assert len(issues) == 1
    assert issues[0].code == "OVEREXPOSED"

    # Good exposure image
    img_good = np.ones((100, 100, 3), dtype=np.uint8) * 128
    issues = evaluate_exposure(img_good, min_threshold=40.0, max_threshold=220.0)
    assert len(issues) == 0

def test_build_quality_result():
    # Generate a good synthetic image and encode to bytes
    img = np.random.randint(50, 200, (300, 300, 3), dtype=np.uint8)
    success, buffer = cv2.imencode('.jpg', img)
    assert success
    image_bytes = buffer.tobytes()

    result, decoded_img = build_quality_result(image_bytes)
    assert result.acceptable is True
    assert len(result.issues) == 0
    assert result.requestedAction is None
    assert decoded_img is not None
    assert decoded_img.shape == (300, 300, 3)

def test_build_quality_result_invalid():
    image_bytes = b"not an image"
    result, decoded_img = build_quality_result(image_bytes)
    assert result.acceptable is False
    assert len(result.issues) == 1
    assert result.issues[0].code == "INVALID_CODEC"
    assert result.requestedAction == "RETAKE"
    assert decoded_img is None
