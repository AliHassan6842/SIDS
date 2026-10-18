# Verified HTTP boundary (v1)

This document records only routes and transport fields present in the current source. JSON request and response bodies are defined by the adjacent draft 2020-12 schemas.

## Browser to Java Core API

All routes use prefix `/api/v1`. Except for register and login, requests require `Authorization: Bearer <token>`.

| Method | Route | Request | Successful response |
|---|---|---|---|
| POST | `/auth/register` | JSON `RegisterRequest` | `201` `AuthResponse` |
| POST | `/auth/login` | JSON `LoginRequest` | `200` `AuthResponse` |
| GET | `/me` | none | `200` `UserProfile` |
| PUT | `/me` | JSON `UpdateProfileRequest` | `200` `UserProfile` |
| GET | `/crops` | none | `200` array of `Crop` |
| GET | `/pests` | none | `200` array of `Pest`; summaries have `affectedCrops: []` and `guidance: null` |
| GET | `/pests/{pestId}` | UUID path parameter | `200` detailed `Pest` |
| GET | `/crops/{cropId}/pests` | UUID path parameter | `200` array of `Pest` |
| POST | `/vision/validate-frame` | multipart `cropId` UUID + `image` JPEG/PNG | `200` `ValidateFrameResponse` |
| POST | `/scans` | multipart `cropId` UUID + `image` JPEG/PNG | `201` `ScanResult` |
| GET | `/scans` | none | `200` array of authorized user's `ScanResult` |
| GET | `/scans/{scanId}` | UUID path parameter | `200` authorized user's `ScanResult` |
| GET | `/scans/{scanId}/image` | UUID path parameter | `200 image/jpeg`, private ownership check, `Cache-Control: no-store` |

## Additive multi-mode contract (v2 shape on `/api/v1`)

The current paths stay versioned as `/api/v1`; the v2 JSON Schema revision adds fields while preserving old multipart callers through server defaults.

| Method | Route | Request | Successful response |
|---|---|---|---|
| GET | `/crops` | optional `includeUnavailable` boolean | array of v2 `Crop`; default behavior may remain supported-only for old clients |
| GET | `/pests` | optional `kind=CROP_PEST\|GENERAL_INSECT`; optional `cropId` UUID only for crop pests | array of promoted v2 `Pest`; general list is currently empty |
| POST | `/scans` | multipart `mode`, conditional `cropId`, `trainingConsent`, `image` | `201` v2 `ScanResult` |
| PUT | `/scans/{scanId}/training-consent` | JSON `TrainingConsentRequest` | authorized owner's `TrainingConsentResponse` |
| POST | `/scans/{scanId}/review-submission` | JSON `ReviewSubmissionRequest`; current consent required | `201` Java-owned `ReviewResponse` |
| GET | `/reviews?status=` | `status=PENDING\|APPROVED\|REJECTED`, default `PENDING` | reviewer/admin-only array of `ReviewResponse` |
| POST | `/reviews/{reviewId}/claim` | none | reviewer/admin-only atomically assigned `ReviewResponse` |
| POST | `/reviews/{reviewId}/decision` | JSON `ReviewDecisionRequest` | assigned-reviewer/admin `ReviewResponse` |
| GET | `/reviews/{reviewId}/image` | UUID path | assigned-reviewer/admin private JPEG, `Cache-Control: no-store` |
| POST | `/model-promotions` | JSON `ModelPromotionRequest` | `201` admin-only immutable `ModelPromotionResponse` |

Multipart rules:

- `mode` is `CROP_PEST` or `GENERAL_INSECT`; an omitted value defaults to `CROP_PEST` only for backward compatibility.
- `cropId` is required for `CROP_PEST` and forbidden for `GENERAL_INSECT`.
- `trainingConsent` defaults to `false`; upload alone never grants consent.
- Only the scan owner may read a scan/image or update its consent/submission.
- `GENERAL_INSECT` currently has no promoted labels. Its successful persisted outcome is therefore `UNKNOWN` with null crop and pest; unpromoted BAU labels must never be exposed as results.

Review queue, claim, decision, and review-image endpoints require a database-backed `REVIEWER` or `ADMIN` role; an ordinary authenticated farmer token receives `403`. Model promotion requires `ADMIN`, verifies every referenced review is approved and currently consented, and persists the model/dataset/artifact hashes in an append-only audit record. JWT claims alone do not grant staff authority.

Errors use `ErrorModel`. Image uploads are currently bounded to 8 MiB, at least 224 by 224 pixels, and at most 20,000,000 decoded pixels by default. Deployment configuration may lower these limits but must not exceed the private AI service's limits.

Registration requires a password of 10–128 characters. Login deliberately accepts any nonblank password into the same credential-verification path so invalid lengths do not create a distinct public credential outcome; accounts created by this API still always have at least 10 characters. Profile update requires `fullName`; optional `language` retains the existing preference when omitted.

## Java to private Python AI service

These routes are not browser APIs. Both require `X-SIDS-Service-Token`; Java also propagates `X-Request-Id`.

| Method | Route | Multipart fields | Successful response |
|---|---|---|---|
| POST | `/internal/v1/validate-frame` | `crop_id` crop slug + `image` sanitized JPEG | `200` `ValidateFrameResponse` |
| POST | `/internal/v1/identify` | `crop_id` crop slug + `image` sanitized JPEG | `200` `IdentifyResponse` |

`crop_id` is deliberately a stable crop slug at this private boundary, not the public crop UUID. `prediction.pestId` is deliberately a stable pest slug. Only Java may resolve these slugs to catalog UUIDs and attach guidance.

The additive private multi-mode fields are:

- `mode=CROP_PEST|GENERAL_INSECT`, defaulting to `CROP_PEST` only for old Java callers;
- `crop_id` required for crop mode and forbidden for general mode;
- `image` remains the sanitized bounded JPEG.

For `GENERAL_INSECT`, Python may perform bounded image-quality checks but, while no general model is promoted, returns only `REJECTED_IMAGE` or `UNKNOWN/MODEL_UNAVAILABLE`. Research-only BAU labels never cross this production boundary. Java remains responsible for catalog resolution and all attributable crop/general guidance, authorization, consent, and review state.

## Status semantics

- `IDENTIFIED`: exactly one supported catalog pest, with confidence and optional normalized box.
- `UNKNOWN`: no supported prediction is safe to show; `prediction`/public `pest` is null.
- `REJECTED_IMAGE`: image quality or validation failed; no pest is claimed.
- `FAILED`: reserved for persisted Java processing failures. The current synchronous create path returns an error instead of persisting this state.

Neither `UNKNOWN` nor `REJECTED_IMAGE` may be converted to the top-scoring class by a client.
