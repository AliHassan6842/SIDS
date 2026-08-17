# Foundation architecture

F0 creates ownership boundaries and development scaffolding without implementing product features.

- `apps/web` contains the pre-existing React/Vite application. Its scoped instructions prohibit incidental edits.
- `services/core-api` reserves the future Java/Spring runtime where business truth, authorization, agronomy policy, and durable workflows live.
- `services/ai-service` reserves the production Python inference runtime. It consumes approved exports and returns structured computational evidence.
- `ml` isolates datasets, experiments, training, evaluation, exports, model registry metadata, notebooks, and research scripts from production inference.
- `knowledge` separates authoritative agronomy sources, normalization, ingestion, and retrieval evaluation from ML datasets.
- `packages/contracts` will hold canonical OpenAPI, JSON Schema, event, example, and error specifications. It is not yet imported by the frontend.
- `packages/config` and `packages/test-utils` reserve future shared JS/TS packages only when concrete shared code exists.
- `infra` describes future Docker, Compose, PostgreSQL, Valkey, object-storage, and monitoring responsibilities without starting services.
- `docs` holds architecture, API, research, security, testing, ownership, agent playbooks, and ADRs.
- `scripts` separates future bootstrap, development, CI, and maintenance automation.
- `tools` is reserved for real repository tooling that may later become a pnpm workspace package.
- `.github` reserves CI and collaboration policy; no fake workflow is introduced.

The durable/transient boundary is deliberate: PostgreSQL is the source of business truth, Valkey is disposable fast state and work transport, and image bytes belong in object storage. PostgreSQL full-text search plus pgvector is the planned knowledge retrieval foundation; no separate vector database is introduced.
