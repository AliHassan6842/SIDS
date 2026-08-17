# Shared contracts

This package boundary will become the canonical source for cross-system interfaces. F0 documents the structure only and does not change or import the frontend's existing contracts.

- `openapi`: future HTTP interface specifications.
- `json-schema`: transport-neutral data schemas.
- `examples`: validated, non-secret examples tied to schema versions.
- `events`: future Valkey work/event envelope definitions.
- `errors`: shared error envelope and code semantics.

Planned domains include Quick Diagnosis, Field Survey, AI Analysis, Image Quality, Diagnosis, Recommendation, Sync, Task, Treatment, and Errors. Future generated clients must trace back to a versioned canonical schema; hand-copied duplicate schemas are not authoritative.
