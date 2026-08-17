from sids_ai.image_quality.service import build_quality_result, evaluate_resolution


def test_resolution_too_low():
    issues = evaluate_resolution(100, 100)
    assert len(issues) == 1
    assert issues[0].code == "RESOLUTION_TOO_LOW"

def test_quality_acceptable():
    result = build_quality_result(800, 600, False)
    assert result.acceptable == True
    assert len(result.issues) == 0
