from fastapi.testclient import TestClient
from sids_ai.app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_ready_endpoint():
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"

def test_analyze_endpoint_validation():
    # Empty body
    response = client.post("/internal/v1/analyze", json={})
    assert response.status_code == 422

def test_analyze_endpoint_valid_schema():
    # Sending a minimal valid request
    payload = {
        "analysisId": "test-analysis-1",
        "crop": "COTTON",
        "mode": "QUICK_DIAGNOSIS",
        "images": [
            {"imageKey": "dummy_base64_string"}
        ]
    }
    response = client.post("/internal/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check JSON Schema structure of response
    assert data["analysisId"] == "test-analysis-1"
    assert "quality" in data
    assert "routing" in data
    assert "predictions" in data
    assert "uncertainty" in data
    assert "model" in data
    assert "latencyMs" in data
