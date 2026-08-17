# SIDS — AI Digital Crop Scout

SIDS (Smart Insect Detection System) is a planned offline-first platform that helps farmers capture crop observations, obtain bounded AI analysis, and make field decisions using verified context. The repository is currently in **F0 — Foundation**. It contains the existing frontend plus architecture and workspace boundaries; backend, AI, data, and infrastructure features are not implemented yet.

## Monorepo map

| Path | Purpose | Primary owner |
| --- | --- | --- |
| `apps/web` | Existing React/Vite frontend | Frontend member |
| `services/core-api` | Future Java/Spring business API | Java platform member |
| `services/ai-service` | Future production Python inference runtime | AI/research lead |
| `ml` | Research, datasets, training, and evaluation | AI/research lead |
| `knowledge` | Trusted agronomy source and retrieval preparation | AI/research lead |
| `packages/contracts` | Shared cross-boundary contract specifications | Shared |
| `infra` | Future local and deployment infrastructure | Shared |
| `docs` | Architecture, decisions, playbooks, and project rules | Shared |

The frontend is protected by `apps/web/AGENTS.md`. Foundation work relocated it without changing its source, manifest, lockfile, or configuration.

## JavaScript workspace setup

Node.js with Corepack is recommended. The repository pins pnpm in the root manifest.

```sh
corepack enable
pnpm install
```

An existing npm lockfile remains inside `apps/web` as frontend-owned history. F0 does not replace it. Root pnpm commands delegate frontend scripts to npm so they do not migrate its dependency tree. The root `.npmrc` changes pnpm's dependency check to warning-only, preventing an automatic install from rewriting npm-managed dependencies. Coordinate any future lockfile/package-manager migration with the frontend owner.

Run the existing frontend from the repository root:

```sh
pnpm web
pnpm web:check
pnpm web:build
```

No root install is required merely to inspect or parse the workspace. If installing dependencies, review the resulting lockfile and frontend dependency tree before committing.

## Planned systems

- Java/Spring core API: durable domain state, authorization, offline sync, agronomic decisions, and orchestration.
- Python/FastAPI AI service: validated production inference with explicit uncertainty and model metadata.
- PostgreSQL with pgvector: durable data plus hybrid knowledge retrieval.
- Valkey: transient cache, rate controls, idempotency, locks, and AI job streams.
- Object storage: agricultural imagery and derived image artifacts.

These systems, authentication, schemas, workers, models, training pipelines, datasets, and agronomic logic are intentionally absent in F0.
