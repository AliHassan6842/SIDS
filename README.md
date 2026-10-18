# SIDS — Simplified Smart Insect Identification

SIDS is a final-year-project web application for bounded rice-pest identification from one uploaded image. The promoted product scope supports two pests: **rice leaf roller** (`rice-leaf-roller`) and **rice water weevil** (`rice-water-weevil`). An image is evidence for that image only; the system does not infer whole-field incidence or prescribe pesticides, dosages, or treatment thresholds.

## Runtime architecture

- `apps/web`: React/Vite user interface.
- `services/core-api`: Java 21/Spring Boot API. It owns users, authorization, scan ownership, catalog data, guidance, persistence, and private image storage.
- `services/ai-service`: private Python 3.11/FastAPI service. It validates images and returns bounded model evidence.
- PostgreSQL 16: durable application data and Flyway schema history.
- `sids_private_images`: a Docker named volume mounted only by the Core API at `/data/private-images`.
- `packages/contracts`: canonical public/private interface schemas and compatibility tests.

Valkey, MinIO, pgvector, disease classification, background workers, and treatment policy are not part of this simplified runtime.

## Prerequisites

- Node.js 24 and npm 11
- Java 21 (the repository includes Maven Wrapper scripts)
- Python 3.11 and Poetry 2.1.3
- Docker Desktop or Docker Engine with Compose v2

## First-time setup

From the repository root on Windows:

```powershell
npm run setup:dev
npm ci --prefix apps/web
python -m pip install poetry==2.1.3
poetry --directory services/ai-service install --with dev
```

`setup:dev` creates an ignored `.env` from `.env.example` and generates local secrets. On macOS/Linux, copy `.env.example` to `.env` and replace every `replace-with-...` value with a random secret.

The fetched datasets are not installed as application dependencies. Their separate provenance/checksum record is [`ml/data/fetched/FETCH_MANIFEST.json`](ml/data/fetched/FETCH_MANIFEST.json); large archives, prepared images, checkpoints, and weights remain ignored by Git.

## Model release input

This completed workspace contains the promoted, Git-ignored model weight and its tracked checksum manifest under `models/`:

```text
models/
  manifests/sids-pest-detector.json
  artifacts/sids-rice-pest-detector-v1.0.0.pt
```

The artifact SHA-256 is `b3af4057f3d59c21efd27266ee519fe487c0433468f641973b3f89290ea674bc`. A fresh Git clone does not contain the ignored `.pt` binary; provision that exact approved artifact (or a separately evaluated replacement) before startup. The manifest must match `services/ai-service/src/sids_ai/registry/manifest.py`, reference only the two supported pest slugs for crop slug `rice`, and contain the artifact's real checksum. Research/example manifests under `ml/model-registry` are not deployable runtime manifests.

The AI service exposes `/health` for process liveness and `/ready` for model readiness. Without a valid promoted artifact, liveness remains available but `/ready` returns `503 MODEL_UNAVAILABLE`.

## Run locally

Start PostgreSQL, AI service, and Core API:

```powershell
npm run dev
```

Then start the web app in a second terminal:

```powershell
npm run web:dev
```

The web app is at `http://localhost:5173`; the Core API is at `http://localhost:8080`. Stop the backend stack with `npm run infra:down`. `docker compose down` preserves both named volumes; add `--volumes` only when intentionally deleting local database and private-image data.

## Reproducible verification

```powershell
# Contracts
python -m pytest packages/contracts/tests

# Python
poetry --directory services/ai-service run ruff check src tests
poetry --directory services/ai-service run mypy src
poetry --directory services/ai-service run pytest

# Java (PowerShell)
$env:JAVA_HOME = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot'
services\core-api\mvnw.cmd -f services\core-api\pom.xml clean test
services\core-api\mvnw.cmd -f services\core-api\pom.xml package

# Frontend
npm ci --prefix apps/web
npm --prefix apps/web run lint
npm --prefix apps/web run typecheck
npm --prefix apps/web test
npm --prefix apps/web run build
npm --prefix apps/web run e2e

# Containers
docker compose --env-file .env -f infra/docker-compose.yml config --quiet
docker compose --env-file .env -f infra/docker-compose.yml build ai-service core-api
docker compose --env-file .env -f infra/docker-compose.yml up -d --wait db
```

The Java migration integration test applies the immutable Flyway chain V001 through V010 to PostgreSQL. V009 adds explicit scan modes, revocable training consent, staff review, and immutable promotion audit records; V010 permits reviewed coarse general labels without inventing a species name. CI repeats contracts, Python lint/type/tests, Java tests/package, frontend lint/type/unit/build, Win32 Playwright baselines, Compose resolution, and both service image builds. Real-stack/model E2E remains a release gate after a promoted model artifact is supplied; CI does not fabricate one.
