# Infrastructure boundaries

F0 documents responsibility only; it does not start containers or provision services.

- PostgreSQL is the durable source of truth and hosts future pgvector/full-text retrieval.
- Valkey holds transient cache, rate limits, idempotency state, distributed locks, AI work streams, and short-lived state; it is not permanent business storage.
- Object storage holds original, sanitized, annotated, and derived imagery. Images are not PostgreSQL blobs.
- Docker/Compose will support reproducible local environments.
- Monitoring will define metrics, logs, traces, health checks, and local observability wiring.
