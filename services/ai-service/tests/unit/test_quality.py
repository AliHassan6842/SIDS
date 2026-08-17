from sids_ai.image_quality.service import build_quality_result, evaluate_resolution
import cv2
import numpy as np

def test_resolution_too_low():
    issues = evaluate_resolution(100, 100, 400, 400)
    assert len(issues) == 1
    assert issues[0].code == "RESOLUTION_TOO_LOW"

def test_quality_acceptable():
    img = np.random.randint(100, 200, (600, 800, 3), dtype=np.uint8)
    _, buf = cv2.imencode('.jpg', img)
    result, _ = build_quality_result(buf.tobytes())
    assert result.acceptable == True
    assert len(result.issues) == 0
