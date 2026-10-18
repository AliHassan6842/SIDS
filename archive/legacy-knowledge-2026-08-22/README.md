# Agronomy knowledge foundation

`knowledge` is separate from ML datasets. It will hold registries and reproducible preparation of allowlisted agricultural evidence: Pakistani agriculture sources, economic pest thresholds, crop/problem relationships, IPM guidance, pesticide registration references, ingestion, and retrieval evaluation.

- `source-registry`: source authority, jurisdiction, dates, license, location, and checksums.
- `raw`: immutable acquired documents, excluded from Git when large or restricted.
- `processed`: normalized, attributable representations.
- `ingestion`: future deterministic ingestion definitions.
- `evaluation`: retrieval, citation, freshness, and answer-grounding tests.

No documents are downloaded in F0. The planned retrieval stack is PostgreSQL full-text search plus pgvector; a separate vector database is not part of the foundation.
