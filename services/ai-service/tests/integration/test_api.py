from io import BytesIO
from types import SimpleNamespace

from fastapi.testclient import TestClient
from PIL import Image

from sids_ai.app import app
from sids_ai.insect.model import Detection
from sids_ai.schemas import BoundingBox, Prediction

SERVICE_TOKEN = "test-only-internal-token-32-characters"


def image_bytes(color=(0, 0, 0)) -> bytes:
    output = BytesIO()
    Image.new("RGB", (320, 320), color).save(output, format="JPEG")
    return output.getvalue()


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_requires_primary_and_small_subject_models() -> None:
    with TestClient(app) as client:
        assert client.get("/ready").status_code == 200
        client.app.state.small_subject_detector = None
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "MODEL_UNAVAILABLE"}


def test_validate_frame_rejects_dark_image() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/validate-frame",
            headers={"X-SIDS-Service-Token": SERVICE_TOKEN},
            data={"crop_id": "cotton"},
            files={"image": ("dark.jpg", image_bytes(), "image/jpeg")},
        )
    assert response.status_code == 200
    assert response.json()["reason"] == "TOO_DARK"


def test_internal_endpoint_rejects_missing_service_token() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/validate-frame",
            data={"crop_id": "cotton"},
            files={"image": ("dark.jpg", image_bytes(), "image/jpeg")},
        )
    assert response.status_code == 401


def test_internal_auth_rejects_before_multipart_parsing() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/identify",
            headers={"Content-Type": "multipart/form-data"},
            content=b"malformed multipart that must not be parsed",
        )
    assert response.status_code == 401


def test_identify_rejects_malformed_image_before_inference() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/identify",
            headers={"X-SIDS-Service-Token": SERVICE_TOKEN},
            data={"crop_id": "rice"},
            files={"image": ("broken.jpg", b"not an image", "image/jpeg")},
        )
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_IMAGE"


def test_identify_rejects_blurry_image_before_inference() -> None:
    import cv2
    import numpy as np

    y, x = np.indices((320, 320))
    checkerboard = (((y // 32 + x // 32) % 2) * 255).astype(np.uint8)
    blurred = cv2.GaussianBlur(checkerboard, (0, 0), 3)
    output = BytesIO()
    Image.fromarray(np.repeat(blurred[:, :, np.newaxis], 3, axis=2)).save(output, format="JPEG")
    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/identify",
            headers={"X-SIDS-Service-Token": SERVICE_TOKEN},
            data={"crop_id": "rice"},
            files={"image": ("blurry.jpg", output.getvalue(), "image/jpeg")},
        )
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED_IMAGE"
    assert response.json()["reason"] == "TOO_BLURRY"


def test_identify_never_forces_class_when_model_missing() -> None:
    rng = np_random_image()
    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/identify",
            headers={"X-SIDS-Service-Token": SERVICE_TOKEN},
            data={"crop_id": "cotton"},
            files={"image": ("random.jpg", rng, "image/jpeg")},
        )
    assert response.status_code == 200
    assert response.json()["status"] in {"UNKNOWN", "REJECTED_IMAGE"}


def test_general_insect_mode_quality_checks_without_using_crop_model() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/identify",
            headers={"X-SIDS-Service-Token": SERVICE_TOKEN},
            data={"mode": "GENERAL_INSECT"},
            files={"image": ("general.jpg", np_random_image(), "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "UNKNOWN"
    assert response.json()["reason"] in {"MODEL_UNAVAILABLE", "NO_DETECTION"}
    assert response.json()["prediction"] is None


def test_crop_mode_requires_crop_id() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/identify",
            headers={"X-SIDS-Service-Token": SERVICE_TOKEN},
            data={"mode": "CROP_PEST"},
            files={"image": ("crop.jpg", np_random_image(), "image/jpeg")},
        )

    assert response.status_code == 422


def test_general_insect_mode_forbids_crop_id() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/validate-frame",
            headers={"X-SIDS-Service-Token": SERVICE_TOKEN},
            data={"mode": "GENERAL_INSECT", "crop_id": "rice"},
            files={"image": ("general.jpg", np_random_image(), "image/jpeg")},
        )

    assert response.status_code == 422


def test_identify_routes_small_subject_to_bounded_fallback() -> None:
    fallback = SimpleNamespace(
        identify=lambda rgb, crop_id: Detection(
            Prediction(
                pestId="rice-water-weevil",
                confidence=0.86,
                bbox=BoundingBox(x=0.4, y=0.4, width=0.2, height=0.15),
            )
        )
    )
    with TestClient(app) as client:
        client.app.state.small_subject_manifest = SimpleNamespace(
            model_id="small-subject-model",
            version="1.1.0",
            dataset_version="small-subject-v1.4",
        )
        client.app.state.small_subject_detector = fallback
        response = client.post(
            "/internal/v1/identify",
            headers={"X-SIDS-Service-Token": SERVICE_TOKEN},
            data={"crop_id": "rice"},
            files={"image": ("distant.jpg", image_bytes((120, 120, 120)), "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "IDENTIFIED"
    assert response.json()["prediction"]["pestId"] == "rice-water-weevil"
    assert response.json()["model"] == {
        "id": "small-subject-model",
        "version": "1.1.0",
        "datasetVersion": "small-subject-v1.4",
    }


def test_identify_keeps_small_subject_rejected_when_fallback_is_uncertain() -> None:
    fallback = SimpleNamespace(identify=lambda rgb, crop_id: None)
    with TestClient(app) as client:
        client.app.state.small_subject_manifest = SimpleNamespace(
            model_id="small-subject-model",
            version="1.1.0",
            dataset_version="small-subject-v1.4",
        )
        client.app.state.small_subject_detector = fallback
        response = client.post(
            "/internal/v1/identify",
            headers={"X-SIDS-Service-Token": SERVICE_TOKEN},
            data={"crop_id": "rice"},
            files={"image": ("distant.jpg", image_bytes((120, 120, 120)), "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED_IMAGE"
    assert response.json()["reason"] == "SUBJECT_TOO_SMALL"


def np_random_image() -> bytes:
    import numpy as np

    output = BytesIO()
    Image.fromarray(np.random.default_rng(7).integers(0, 256, size=(320, 320, 3), dtype=np.uint8)).save(
        output, format="JPEG"
    )
    return output.getvalue()
