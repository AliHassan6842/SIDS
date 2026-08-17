from fastapi.testclient import TestClient
from sids_ai.app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze():
    payload = {
      "analysisId": "123e4567-e89b-12d3-a456-426614174000",
      "crop": "cotton",
      "mode": "QUICK_DIAGNOSIS",
      "images": [{"imageKey": "s3://bucket/test.jpg"}]
    }
    response = client.post("/internal/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["routing"]["problemType"] == "PEST"
    assert len(data["predictions"]) == 1
    assert data["predictions"][0]["classId"] == "cotton-whitefly"
