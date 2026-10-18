import json

from sids_ai.workers.consumer import ValkeyWorker


def test_valkey_worker_valid_envelope():
    worker = ValkeyWorker("redis://localhost:6379")
    payload = json.dumps({
        "type": "AI_ANALYSIS", 
        "jobId": "job-123", 
        "request": {
            "analysisId": "123",
            "crop": "COTTON",
            "images": [{"imageKey": "dummy"}]
        }
    })
    result = worker.process_job(payload)
    assert result["status"] == "SUCCESS"
    assert result["jobId"] == "job-123"

def test_valkey_worker_invalid_type():
    worker = ValkeyWorker("redis://localhost:6379")
    payload = json.dumps({"type": "UNKNOWN_TASK", "jobId": "job-123"})
    result = worker.process_job(payload)
    assert result["status"] == "IGNORED"

def test_valkey_worker_invalid_json():
    # If JSON is invalid, it throws an exception which is caught and returns ERROR (simulating retry state)
    worker = ValkeyWorker("redis://localhost:6379")
    payload = "not-a-valid-json"
    result = worker.process_job(payload)
    assert result["status"] == "ERROR"
