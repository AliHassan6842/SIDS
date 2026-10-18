# Error contract

All future service-facing errors use this stable envelope:

```json
{
  "code": "SIDS_ERROR_CODE",
  "message": "Human readable message",
  "requestId": "correlation-id",
  "retryable": false,
  "details": {}
}
```

## Semantics

- `code` is a stable, documented machine identifier; clients must not branch on `message`.
- `message` is safe for intended users and contains no secrets or stack traces.
- `requestId` correlates logs and traces across Java, AI, and infrastructure boundaries. It is 1–64 ASCII letters, digits, or hyphens; generated values are UUIDs, but a valid caller-supplied value is preserved.
- `retryable` states whether retrying the same logical request can be safe; it does not bypass idempotency.
- `details` is a bounded object with code-specific, non-sensitive context.

## Multi-mode and reviewed-training codes

- Mode/catalog validation: `CROP_REQUIRED`, `CROP_NOT_ALLOWED`, `UNSUPPORTED_CROP`, `INVALID_CATALOG_FILTER`.
- Owner-controlled intake: `TRAINING_CONSENT_REQUIRED`, `SCAN_NOT_REVIEWABLE`, `REVIEW_ALREADY_PENDING`.
- Staff review: `INVALID_REVIEW_STATUS`, `STAFF_ACCESS_REQUIRED`, `REVIEW_NOT_FOUND`, `REVIEW_NOT_AVAILABLE`, `REVIEW_LABEL_REQUIRED`, `REJECTED_REVIEW_HAS_LABEL`.
- Immutable promotion: `DUPLICATE_PROMOTION_REVIEW`, `REVIEW_NOT_PROMOTABLE`, `PROMOTION_NOT_FOUND`, `PROMOTION_MODEL_MISMATCH`, `PROMOTION_ALREADY_EXISTS`.

Ownership failures use the same not-found behavior as missing resources where appropriate, so a caller cannot enumerate another user's scans. Review queues and decisions require a current database-backed reviewer/admin role; model promotion requires admin. Error messages never turn a research label into a public identification.

Business error codes, HTTP mappings, localization, and validation detail schemas are intentionally deferred.
