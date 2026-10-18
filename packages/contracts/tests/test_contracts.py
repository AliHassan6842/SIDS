import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).parents[1]
REPO = ROOT.parents[1]
SCHEMAS = ROOT / "json-schema"
EXAMPLES = ROOT / "examples"
sys.path.insert(0, str(REPO / "services" / "ai-service" / "src"))


def load(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def registry() -> Registry:
    result = Registry()
    for path in SCHEMAS.rglob("*.schema.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        result = result.with_resource(schema["$id"], Resource.from_contents(schema))
        if path.parent == SCHEMAS:
            result = result.with_resource(path.name, Resource.from_contents(schema))
    return result


def test_all_schemas_are_valid_draft_2020_12() -> None:
    for path in SCHEMAS.rglob("*.schema.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def load_v2(name: str) -> dict:
    return json.loads((SCHEMAS / "v2" / name).read_text(encoding="utf-8"))


def v2_example(name: str) -> object:
    return json.loads((EXAMPLES / "v2" / name).read_text(encoding="utf-8"))


def v2_validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(load_v2(name), registry=registry(), format_checker=FormatChecker())


def test_validate_frame_example() -> None:
    validator = Draft202012Validator(
        load("ValidateFrameResponse.schema.json"), registry=registry(), format_checker=FormatChecker()
    )
    validator.validate(json.loads((EXAMPLES / "validate-frame-ready.json").read_text(encoding="utf-8")))
    validator.validate(json.loads((EXAMPLES / "validate-frame-rejected.json").read_text(encoding="utf-8")))


def test_identify_examples() -> None:
    validator = Draft202012Validator(
        load("IdentifyResponse.schema.json"), registry=registry(), format_checker=FormatChecker()
    )
    validator.validate(json.loads((EXAMPLES / "identify-known.json").read_text(encoding="utf-8")))
    validator.validate(json.loads((EXAMPLES / "identify-unknown.json").read_text(encoding="utf-8")))
    validator.validate(json.loads((EXAMPLES / "identify-rejected.json").read_text(encoding="utf-8")))


@pytest.mark.parametrize(
    ("schema_name", "example_name"),
    [
        ("RegisterRequest.schema.json", "register-request.json"),
        ("AuthResponse.schema.json", "auth-response.json"),
        ("Pest.schema.json", "pest-detail.json"),
        ("ScanResult.schema.json", "scan-identified.json"),
        ("ScanResult.schema.json", "scan-unknown.json"),
        ("ErrorModel.schema.json", "error.json"),
    ],
)
def test_public_examples(schema_name: str, example_name: str) -> None:
    validator = Draft202012Validator(load(schema_name), registry=registry(), format_checker=FormatChecker())
    validator.validate(json.loads((EXAMPLES / example_name).read_text(encoding="utf-8")))


def test_status_semantics_reject_false_identification() -> None:
    invalid = json.loads((EXAMPLES / "identify-unknown.json").read_text(encoding="utf-8"))
    invalid["prediction"] = {"pestId": "rice-leaf-roller", "confidence": 0.4, "bbox": None}
    validator = Draft202012Validator(load("IdentifyResponse.schema.json"), registry=registry())
    assert list(validator.iter_errors(invalid)), "UNKNOWN must never carry a fallback prediction"


def test_scan_semantics_reject_pest_for_unknown() -> None:
    invalid = json.loads((EXAMPLES / "scan-unknown.json").read_text(encoding="utf-8"))
    invalid["pest"] = json.loads((EXAMPLES / "pest-detail.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(load("ScanResult.schema.json"), registry=registry())
    assert list(validator.iter_errors(invalid)), "UNKNOWN public scans must not claim a pest"


def test_bounding_box_cross_field_invariant_for_examples() -> None:
    for name in ("identify-known.json", "scan-identified.json"):
        payload = json.loads((EXAMPLES / name).read_text(encoding="utf-8"))
        box = payload.get("bbox") or payload.get("prediction", {}).get("bbox")
        assert box["x"] + box["width"] <= 1
        assert box["y"] + box["height"] <= 1


def test_actual_python_serialization_validates_against_private_schemas() -> None:
    from sids_ai.schemas import (
        IdentificationStatus,
        IdentifyResponse,
        ModelMetadata,
        QualityBand,
        QualitySummary,
        UnknownReason,
        ValidateFrameResponse,
    )

    validation = ValidateFrameResponse(
        valid=True,
        reason=None,
        insectCandidate=True,
        quality=QualitySummary(brightness=QualityBand.OK, blur=QualityBand.OK, subjectSize=QualityBand.OK),
    ).model_dump(mode="json")
    identify = IdentifyResponse(
        status=IdentificationStatus.UNKNOWN,
        reason=UnknownReason.MODEL_UNAVAILABLE,
        prediction=None,
        model=ModelMetadata(id="unavailable", version="unavailable", datasetVersion="unavailable"),
    ).model_dump(mode="json")
    Draft202012Validator(load("ValidateFrameResponse.schema.json"), registry=registry()).validate(validation)
    Draft202012Validator(load("IdentifyResponse.schema.json"), registry=registry()).validate(identify)


def test_caller_supplied_non_uuid_request_id_matches_java_policy() -> None:
    error = json.loads((EXAMPLES / "error.json").read_text(encoding="utf-8"))
    error["requestId"] = "web-Request-42"
    Draft202012Validator(load("ErrorModel.schema.json"), registry=registry()).validate(error)


def test_v2_five_crop_catalog_is_honest_about_promoted_scope() -> None:
    crops = v2_example("crops-five.json")
    validator = v2_validator("Crop.schema.json")
    for crop in crops:
        validator.validate(crop)
    assert [crop["slug"] for crop in crops] == ["rice", "corn", "wheat", "beet", "citrus"]
    assert [crop["slug"] for crop in crops if crop["identificationSupported"]] == ["rice"]


def test_v2_catalog_kind_separates_crop_and_general_guidance() -> None:
    validator = v2_validator("Pest.schema.json")
    crop_pest = v2_example("pest-crop.json")
    validator.validate(crop_pest)

    invalid = dict(crop_pest)
    invalid["kind"] = "GENERAL_INSECT"
    assert list(validator.iter_errors(invalid)), "general insects cannot carry crop relationships or crop guidance"
    assert v2_example("pests-general-empty.json") == [], "no general insect label has passed promotion gates"


def test_v2_crop_and_general_scan_examples() -> None:
    validator = v2_validator("ScanResult.schema.json")
    validator.validate(v2_example("scan-crop-identified.json"))
    validator.validate(v2_example("scan-general-unknown.json"))


def test_v2_mode_crop_rules_and_unknowns_are_closed() -> None:
    validator = v2_validator("ScanResult.schema.json")
    general = v2_example("scan-general-unknown.json")

    with_crop = json.loads(json.dumps(general))
    with_crop["crop"] = v2_example("crops-five.json")[0]
    assert list(validator.iter_errors(with_crop)), "GENERAL_INSECT must not accept a crop"

    cross_mode_identification = json.loads(json.dumps(general))
    cross_mode_identification.update({
        "status": "IDENTIFIED",
        "reason": None,
        "confidence": 0.7,
        "pest": v2_example("pest-crop.json"),
    })
    assert list(validator.iter_errors(cross_mode_identification)), "general mode must never return a crop-pest catalog entry"

    crop_without_crop = v2_example("scan-crop-identified.json")
    crop_without_crop["crop"] = None
    assert list(validator.iter_errors(crop_without_crop)), "CROP_PEST requires an authoritative crop"


def test_v2_consent_and_review_status_are_distinct() -> None:
    validator = v2_validator("ScanResult.schema.json")
    scan = v2_example("scan-crop-identified.json")

    consent_without_timestamp = json.loads(json.dumps(scan))
    consent_without_timestamp["consentedAt"] = None
    assert list(validator.iter_errors(consent_without_timestamp))

    pending_without_consent = json.loads(json.dumps(scan))
    pending_without_consent.update({"trainingConsent": False, "consentedAt": None})
    assert list(validator.iter_errors(pending_without_consent)), "pending review requires current opt-in"

    consented_not_submitted = json.loads(json.dumps(scan))
    consented_not_submitted["reviewStatus"] = "NOT_SUBMITTED"
    validator.validate(consented_not_submitted)


def test_v2_review_submission_does_not_accept_authoritative_decisions() -> None:
    validator = v2_validator("ReviewSubmissionRequest.schema.json")
    validator.validate({})
    validator.validate({"proposedLabelSlug": "beetle", "notes": "User-proposed annotation only."})
    assert list(validator.iter_errors({"decision": "APPROVED", "labelSlug": "beetle"}))


def test_v2_consent_and_review_response_examples() -> None:
    v2_validator("TrainingConsentResponse.schema.json").validate(v2_example("training-consent-enabled.json"))
    v2_validator("ReviewResponse.schema.json").validate(v2_example("review-pending.json"))


def test_v2_reviewer_decisions_enforce_label_semantics() -> None:
    validator = v2_validator("ReviewDecisionRequest.schema.json")
    validator.validate({"decision": "APPROVED", "labelSlug": "beetle", "notes": "Reviewed label."})
    validator.validate({"decision": "REJECTED", "notes": "Not usable."})
    assert list(validator.iter_errors({"decision": "APPROVED", "labelSlug": None}))
    assert list(validator.iter_errors({"decision": "REJECTED", "labelSlug": "beetle"}))


def test_v2_model_promotion_is_hash_and_review_bound() -> None:
    response = v2_example("model-promotion.json")
    v2_validator("ModelPromotionResponse.schema.json").validate(response)
    request = {key: value for key, value in response.items() if key not in {"id", "promotedBy", "promotedAt"}}
    validator = v2_validator("ModelPromotionRequest.schema.json")
    validator.validate(request)
    invalid = dict(request)
    invalid["artifactSha256"] = "not-a-sha256"
    assert list(validator.iter_errors(invalid))
    duplicate_reviews = dict(request)
    duplicate_reviews["reviewIds"] = [
        "50000000-0000-0000-0000-000000000010",
        "50000000-0000-0000-0000-000000000010",
    ]
    assert list(validator.iter_errors(duplicate_reviews))
