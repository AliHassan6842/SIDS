# Error contract

All future service-facing errors use this stable envelope:

```json
{
  "code": "SIDS_ERROR_CODE",
  "message": "Human readable message",
  "requestId": "uuid",
  "retryable": false,
  "details": {}
}
```

## Semantics

- `code` is a stable, documented machine identifier; clients must not branch on `message`.
- `message` is safe for intended users and contains no secrets or stack traces.
- `requestId` correlates logs and traces across Java, AI, and infrastructure boundaries.
- `retryable` states whether retrying the same logical request can be safe; it does not bypass idempotency.
- `details` is a bounded object with code-specific, non-sensitive context.

Business error codes, HTTP mappings, localization, and validation detail schemas are intentionally deferred.
