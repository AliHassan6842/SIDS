# Initial repository audit

Date: 2026-08-22

## Product target

SIDS is being reduced to one defensible workflow: an authenticated farmer selects a dataset-supported crop, submits a controlled close-up insect image, receives `IDENTIFIED`, `UNKNOWN`, or `REJECTED_IMAGE`, views predefined attributed guidance for an identified supported pest, and can reopen their own scan history.

The product must not claim disease diagnosis, whole-field incidence, treatment necessity, pesticide choice, dosage, economic-threshold evaluation, or universal insect recognition.

## Repository baseline

- Git worktree was clean before changes.
- `apps/web` is React 18, TypeScript, Vite 5, React Router, MUI, Redux Toolkit/Saga/Persist, React Hook Form, and Zod.
- `services/core-api` is a Java 21 Spring Boot application with PostgreSQL/Flyway, OAuth2 resource-server scaffolding, S3-compatible storage scaffolding, and many legacy domain modules.
- `services/ai-service` is Python production inference code; `ml` contains dataset/training/evaluation/model-registry research code.
- `packages/contracts` contains obsolete generic analysis, disease, uncertainty, and Valkey job schemas.
- Infrastructure currently starts pgvector/PostgreSQL, Valkey, and MinIO and makes the image bucket anonymous.
- There is no CI workflow beyond an empty placeholder.
- The frontend build, Java build, and cross-service startup were not passing at audit time.

## KEEP

- React/Vite/TypeScript, React Router, MUI theme primitives, lazy route loading, and the responsive-shell concept.
- Java as the sole public API/business-authorization boundary.
- Python as a private bounded image-validation and pest-inference service.
- PostgreSQL, Flyway migration history, Spring validation/security foundations, and Testcontainers strategy.
- S3-compatible private object storage and a local development storage adapter.
- Existing image decode/quality/security utilities that pass review.
- Model registry/integrity concepts, deterministic dataset tooling, and useful pest-detection training/evaluation code.
- The stable error-envelope fields: `code`, `message`, `requestId`, `retryable`, and bounded `details`.
- Git history and existing ADRs as the record of superseded work.

## REFACTOR

### Frontend

- Replace the dashboard with `/home`, `/identify`, `/result/:scanId`, `/pests`, `/pests/:pestId`, `/history`, and `/profile`, plus real `/login` and `/register` flows.
- Replace the simulated black camera panel with `getUserMedia`, ROI guidance, permission/no-device states, gallery fallback, stream cleanup, capture/review/retake, latest-frame-only validation, cancellation, and stale-response protection.
- Replace the intercepted mock API with typed browser-to-Java `/api/v1` requests only.
- Reduce Redux/Saga/Persist use to state that genuinely benefits from it; keep transient camera state local.

### Java Core API

- Build feature-first `identity`, `crop`, `pest`, `scan`, `storage`, and `ai` modules.
- Add forward migrations for `crops`, `pests`, `crop_pests`, `pest_guidance`, `scans`, and `scan_predictions`; do not rewrite V001-V004.
- Derive ownership from authenticated identity and query scans by both scan ID and user ID.
- Implement a typed synchronous Python client with timeouts and explicit error mapping.
- Harden upload validation, safe object keys, EXIF removal/re-encoding, private retrieval, and ownership.

### Python runtime and ML

- Reduce production inference to decode, sanitize, quality, ROI, candidate validation, supported-pest inference, unknown gating, and model metadata.
- Freeze production classes only after the IP102 plus at-most-one-supplement dataset audit.
- Separate fetched/raw data, prepared deterministic splits, experiment runs, and promoted artifacts.
- Select the acceptance threshold from executed evaluation and bind it to the promoted manifest.

### Contracts and infrastructure

- Replace disease/generic-analysis/Valkey contracts with versioned frame-validation, identification, scan-result, and error schemas.
- Replace pgvector with standard PostgreSQL and remove the AI work queue unless another demonstrated use remains.
- Make storage private and align environment-variable names across compose and services.
- Add deterministic health checks, service startup, builds, tests, and CI.

## REMOVE FROM PRODUCTION

- Disease, PlantVillage, and Paddy Doctor workflows and artifacts.
- Severity segmentation, crop-disease classification, whole-field survey/incidence, economic thresholds, affected-area claims, and field analytics.
- Pesticide, dosage, PHI, chemical safety, treatment plan, and autonomous recommendation logic.
- Weather-driven decisions, complex task/reminder/notification workflows, RAG/knowledge retrieval, pgvector, and specialist routing.
- Browser-to-Python configuration, generic COCO production inference, arbitrary image URLs/model names, and unnecessary Valkey AI queues.
- Frontend routes `/fields`, `/survey`, `/tasks`, `/advisory`, `/alerts`, `/reports`, `/admin`, and `/more`, together with their prohibited claims and hard-coded mock results.

## ARCHIVE

- Preserve applied V001-V004 migrations unchanged.
- Use Git history rather than keeping obsolete compiled/runtime modules.
- Retain only clearly labelled non-production research evidence that remains useful; production code must not import it.
- Do not migrate old labels into `IDENTIFIED` unless they map exactly to the frozen supported taxonomy and model provenance.

## UNKNOWN AT AUDIT TIME

- Whether a real database has applied V001-V004 or contains legacy data requiring migration.
- Whether a real OIDC provider or user directory exists.
- Final supported crops and pests, pending executed dataset counts and annotation review.
- Final image-retention/deletion policy.
- Whether supplementary BAU-Insectv2 classes overlap the final IP102 scope sufficiently to justify use.
- Whether available hardware and wall-clock time permit a meaningful full training run in this environment.

## Material baseline defects

- Frontend authentication, API traffic, camera capture, and predictions are simulated; required routes and tests are missing.
- Frontend lint/build fail because dependencies/configuration and legacy TypeScript are inconsistent.
- Core API exposes only legacy audit/weather/sync/task/notification controllers; target APIs do not exist.
- Several legacy endpoints trust caller-supplied user/farm IDs, and sync pull is not ownership-filtered.
- No Java-to-Python client or scan orchestration exists.
- Storage is configured for anonymous public access and lacks image security/ownership enforcement.
- Core configuration does not match root environment/compose names.
- Java 21 was missing at audit time and is a build prerequisite.
- Existing dataset/model documentation reports unsupported or unverified disease/pest scope and cannot be treated as production evidence.

This audit drives implementation; it is not a completion claim.
