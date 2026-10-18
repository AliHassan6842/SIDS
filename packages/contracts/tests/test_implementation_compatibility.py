"""Cheap executable guards for transport details that JSON Schema cannot inspect.

These tests intentionally read the three implementations. They are not a substitute
for runtime integration tests; they prevent the historically easy-to-miss route,
identifier, multipart-field, and status-vocabulary drift.
"""

from pathlib import Path


REPO = Path(__file__).parents[3]


def source(path: str) -> str:
    return (REPO / path).read_text(encoding="utf-8")


def test_public_multipart_fields_match_frontend_and_java() -> None:
    frontend = source("apps/web/src/api/client.ts")
    java = source("services/core-api/src/main/java/com/agrosense/scan/api/ScanController.java")
    assert 'body: form({ mode, ...(cropId ? { cropId } : {}) }, image, "frame.jpg")' in frontend
    assert "trainingConsent: String(options.trainingConsent)" in frontend
    assert "...(options.cropId ? { cropId: options.cropId } : {})" in frontend
    assert '}, image, "capture.jpg")' in frontend
    assert '@RequestParam(defaultValue="CROP_PEST") IdentificationMode mode' in java
    assert "@RequestParam(required=false) UUID cropId" in java
    assert '@RequestParam(defaultValue="false") boolean trainingConsent' in java
    assert "@RequestPart MultipartFile image" in java


def test_v2_frontend_serialized_types_are_required_and_nullable_where_canonical() -> None:
    frontend = source("apps/web/src/api/contracts.ts")
    assert 'export type IdentificationMode = "CROP_PEST" | "GENERAL_INSECT"' in frontend
    assert 'export type PestKind = "CROP_PEST" | "GENERAL_INSECT"' in frontend
    assert 'export type TrainingReviewStatus = "NOT_SUBMITTED" | "PENDING" | "APPROVED" | "REJECTED"' in frontend
    assert "identificationSupported: boolean" in frontend
    assert "mode: IdentificationMode" in frontend
    assert "crop: Crop | null" in frontend
    assert "trainingConsent: boolean" in frontend
    assert "consentedAt: string | null" in frontend
    assert "reviewStatus: TrainingReviewStatus" in frontend
    assert "generalGuidance: GeneralInsectGuidance | null" in frontend


def test_v2_java_review_and_promotion_dtos_match_canonical_shapes() -> None:
    review = "".join(source("services/core-api/src/main/java/com/agrosense/review/api/ReviewDtos.java").split())
    promotion = "".join(source("services/core-api/src/main/java/com/agrosense/promotion/api/PromotionDtos.java").split())
    controller = source("services/core-api/src/main/java/com/agrosense/review/api/ReviewController.java")
    authorization = source("services/core-api/src/main/java/com/agrosense/identity/application/StaffAuthorizationService.java")

    assert "recordTrainingConsentRequest(@NotNullBooleantrainingConsent)" in review
    assert "recordTrainingConsentResponse(UUIDscanId,booleantrainingConsent,OffsetDateTimeconsentedAt,StringreviewStatus)" in review
    assert "recordReviewSubmissionRequest(" in review and "StringproposedLabelSlug" in review and "Stringnotes" in review
    assert "enumReviewDecision{APPROVED,REJECTED}" in review
    for field in ("UUIDid", "UUIDscanId", "UUIDsubmittedBy", "IdentificationModemode", "StringscanStatus",
                  "Stringstatus", "UUIDassignedReviewerId", "StringreviewerLabelSlug", "OffsetDateTimecreatedAt"):
        assert field in review
    for field in ("StringmodelId", "StringmodelVersion", "StringdatasetVersion", "StringmanifestSha256",
                  "StringartifactSha256", "UUIDsupersedesPromotionId", "List<UUID>reviewIds"):
        assert field in promotion
    assert '@PutMapping("/scans/{scanId}/training-consent")' in controller
    assert '@PostMapping("/scans/{scanId}/review-submission")' in controller
    assert '@GetMapping("/reviews")' in controller
    assert "requireReviewer" in authorization and "requireAdmin" in authorization


def test_general_guidance_is_attributed_java_owned_data() -> None:
    migration = source("services/core-api/src/main/resources/db/migration/V011__general_insect_guidance.sql")
    repository = source("services/core-api/src/main/java/com/agrosense/catalog/infrastructure/CatalogRepository.java")
    dto = source("services/core-api/src/main/java/com/agrosense/catalog/api/CatalogDtos.java")
    python = source("services/ai-service/src/sids_ai/app.py")

    for column in ("harm_summary", "safe_removal", "seek_expert_help_when", "source_name", "source_url", "last_verified_at"):
        assert column in migration
    assert "PestKind.GENERAL_INSECT" in repository
    assert "FROM general_insect_guidance WHERE pest_id=?" in repository
    assert "new GeneralGuidanceResponse" in repository
    assert "record GeneralGuidanceResponse" in dto
    for java_owned_field in ("harmSummary", "safeRemoval", "seekExpertHelpWhen", "sourceName", "sourceUrl", "lastVerifiedAt"):
        assert java_owned_field not in python


def test_private_multipart_fields_and_slug_translation_match_java_and_python() -> None:
    client = source("services/core-api/src/main/java/com/agrosense/ai/AiClient.java")
    service = source("services/core-api/src/main/java/com/agrosense/scan/application/ScanService.java")
    python = source("services/ai-service/src/sids_ai/app.py")
    assert 'body.add("mode", mode)' in client
    assert 'if (cropId != null) body.add("crop_id", cropId)' in client
    assert 'body.add("image"' in client
    assert "crop.slug()" in service
    assert "mode: Annotated[IdentificationMode, Form()]" in python
    assert "crop_id: Annotated[str | None, Form(" in python
    assert "_validate_context(mode, crop_id)" in python
    assert "image: Annotated[UploadFile, File()]" in python


def test_general_private_mode_never_forces_a_research_label() -> None:
    java = source("services/core-api/src/main/java/com/agrosense/scan/application/ScanService.java")
    python = source("services/ai-service/src/sids_ai/app.py")
    assert '"REJECTED_IMAGE".equals(result.status())' in java
    assert 'new IdentifyResponse("UNKNOWN", "MODEL_UNAVAILABLE", null, null)' in java
    assert "if mode is IdentificationMode.GENERAL_INSECT:" in python
    assert "status=IdentificationStatus.UNKNOWN" in python
    assert "reason=UnknownReason.MODEL_UNAVAILABLE" in python


def test_private_image_part_declares_mime_accepted_by_python() -> None:
    client = source("services/core-api/src/main/java/com/agrosense/ai/AiClient.java")
    decoder = source("services/ai-service/src/sids_ai/image/decoder.py")
    assert "MediaType.IMAGE_JPEG" in client
    assert '"image/jpeg"' in decoder


def test_status_vocabulary_matches_all_three_systems() -> None:
    frontend = source("apps/web/src/api/contracts.ts")
    java = source("services/core-api/src/main/java/com/agrosense/ai/AiResponseValidator.java")
    python = source("services/ai-service/src/sids_ai/schemas.py")
    for status in ("IDENTIFIED", "UNKNOWN", "REJECTED_IMAGE"):
        assert status in frontend
        assert status in java
        assert f'{status} = "{status}"' in python


def test_public_pest_detail_uses_uuid_not_private_slug() -> None:
    client = source("apps/web/src/api/client.ts")
    row = source("apps/web/src/components/PestRow.tsx")
    result = source("apps/web/src/pages/ResultPage.tsx")
    controller = source("services/core-api/src/main/java/com/agrosense/catalog/api/CatalogController.java")
    assert "api.pest(pestId" not in client  # declaration is a direct request, not recursive use
    assert 'request<Pest>(`/pests/${encodeURIComponent(pestId)}`' in client
    assert "pest.id" in row and "pest.slug" not in row
    assert "scan.pest.id" in result
    assert "@PathVariable UUID pestId" in controller


def test_registration_password_minimum_is_ten_and_login_uses_uniform_path() -> None:
    login_page = source("apps/web/src/pages/LoginPage.tsx")
    register_page = source("apps/web/src/pages/RegisterPage.tsx")
    java = "".join(source("services/core-api/src/main/java/com/agrosense/identity/api/AuthDtos.java").split())
    assert 'minLength={10}' in login_page
    assert 'minLength={10}' in register_page
    assert "recordRegisterRequest" in java and "@Size(min=10,max=128)Stringpassword" in java
    login_record = java.split("recordLoginRequest", 1)[1].split("publicrecordUserResponse", 1)[0]
    assert "@NotBlank@Size(max=128)Stringpassword" in login_record
    assert "@Size(min=" not in login_record


def test_register_language_is_implemented_end_to_end() -> None:
    frontend = source("apps/web/src/api/client.ts")
    dto = source("services/core-api/src/main/java/com/agrosense/identity/api/AuthDtos.java")
    service = source("services/core-api/src/main/java/com/agrosense/identity/application/AuthService.java")
    assert "JSON.stringify({ fullName, email, password, language })" in frontend
    assert "String language" in dto
    assert "request.language()" in service
