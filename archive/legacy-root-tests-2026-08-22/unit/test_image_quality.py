import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir / "services/ai-service/src"))

from sids_ai.image_quality.blur import evaluate_blur
from sids_ai.image_quality.exposure import evaluate_exposure
from sids_ai.image_quality.resolution import evaluate_resolution
from sids_ai.image_quality.service import build_quality_result, decode_image_bytes


def test_evaluate_resolution():
    issues = evaluate_resolution(200, 200, min_width=224, min_height=224)
    assert len(issues) == 1
    assert issues[0].code == "RESOLUTION_TOO_LOW"

    issues2 = evaluate_resolution(300, 300, min_width=224, min_height=224)
    assert len(issues2) == 0

def test_evaluate_blur():
    # sharp image (high frequency edges)
    img_sharp = np.zeros((100, 100, 3), dtype=np.uint8)
    for i in range(0, 100, 2):
        img_sharp[i, :] = 255
    # Variance of laplacian should be very high
    issues = evaluate_blur(img_sharp, threshold=50.0)
    assert len(issues) == 0
    
    # blurry image (uniform)
    img_blurry = np.ones((100, 100, 3), dtype=np.uint8) * 128
    issues_blur = evaluate_blur(img_blurry, threshold=50.0)
    assert len(issues_blur) == 1
    assert issues_blur[0].code == "IMAGE_TOO_BLURRY"

def test_evaluate_exposure():
    img_under = np.ones((100, 100, 3), dtype=np.uint8) * 10
    issues = evaluate_exposure(img_under, min_threshold=40.0, max_threshold=220.0)
    assert len(issues) == 1
    assert issues[0].code == "UNDEREXPOSED"

    img_over = np.ones((100, 100, 3), dtype=np.uint8) * 240
    issues = evaluate_exposure(img_over, min_threshold=40.0, max_threshold=220.0)
    assert len(issues) == 1
    assert issues[0].code == "OVEREXPOSED"
    
    img_good = np.ones((100, 100, 3), dtype=np.uint8) * 128
    issues = evaluate_exposure(img_good, min_threshold=40.0, max_threshold=220.0)
    assert len(issues) == 0

def test_decode_image_bytes():
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", img)
    assert success
    decoded = decode_image_bytes(encoded.tobytes())
    assert decoded.shape == (50, 50, 3)

    with pytest.raises(ValueError):
        decode_image_bytes(b"not an image")

def test_build_quality_result():
    # Create valid image
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    for i in range(0, 300, 10):
        img[i:i+5, :] = 128
    
    success, encoded = cv2.imencode(".jpg", img)
    assert success
    
    result, out_img = build_quality_result(encoded.tobytes())
    assert result.acceptable is True
    assert len(result.issues) == 0
    assert out_img is not None
