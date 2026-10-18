# Final Refactor Report

## Result

SIDS is now a bounded mobile-first insect-identification FYP with an honest expansion path. The production path is React/Vite → Java Core API → PostgreSQL/private image volume and a private Python detector. Production identification remains Rice plus two promoted pest labels, while the catalog exposes a five-crop roadmap and a separate general-insect review mode without publishing unpromoted research labels. Unsupported inputs return explicit `UNKNOWN` or `REJECTED_IMAGE`, guidance is attributed, and scan history remains owner-authorized.

## Removed or isolated complexity

Disease classification, PlantVillage/Paddy Doctor workflows, severity and field-incidence logic, economic thresholds, pesticide/dosage/PHI decisions, Punjab decision rules, RAG/pgvector, weather decisions, complex tasks/reminders, Valkey streams, public MinIO, and old specialist routing are absent from production imports and Compose. Historical Java, Python, root tests, and knowledge material were preserved under `archive/` for reference only.

## Retained and rebuilt

- Authentication was retained as a concept and rebuilt with normalized emails, BCrypt cost 12, issuer/audience/expiry-validated JWTs, fail-closed secrets, bounded rate limits, and uniform login failure timing.
- PostgreSQL and immutable Flyway history were retained. Forward migrations V005–V010 add the simplified schema, seed the promoted Rice catalog, attach reviewed media, add explicit modes/capability flags and consent/review/promotion audit state, and allow future reviewed coarse general labels without inventing species names.
- Private image storage, sanitation, EXIF removal, ownership checks, and cleanup-on-failure were implemented behind Java.
- Shared interfaces were consolidated under `packages/contracts` with canonical examples and compatibility tests.
- The model-registry idea was reduced to one checksum-enforced JSON manifest and one promoted local artifact.

## Frontend

The old dashboard was replaced by routes for login, registration, home, identify, result, pests, history, and profile. The identify flow has explicit Crop pest and General insect modes, promoted-only crop selection, real camera access, ROI guidance, gallery fallback, permission/no-device handling, latest-frame validation with cancellation/drop semantics, review/retake, and known/unknown/rejected results. Home shows Rice as available and Corn, Wheat, Beet, and Citrus as dataset preparation. Eligible results expose separate revocable consent and expert-review submission controls. Navigation is mobile-first; its active circle moves with the current route. Private scan imagery is fetched as an authenticated blob rather than through an unauthenticated `<img>` URL.

React routes are lazy-loaded. Redux/MUI and obsolete frontend dependencies were removed. React Router and Vite were upgraded after the release audit; the final production npm audit reports zero known production vulnerabilities.

## Java Core API

Java now owns users, authorization, crop/pest catalogs, attributed guidance, scan history, image coordination, AI response validation, consent, staff review, model-promotion audit records, rate limiting, and PostgreSQL persistence. Feature modules include `identity`, `catalog`, `scan`, `review`, `promotion`, `storage`, and `ai`. AI requests use typed DTOs, bounded timeouts, an explicit mode, a private service token, and an explicit `image/jpeg` multipart part. All AI statuses, reasons, model metadata, class slugs, confidence values, and boxes are validated before persistence. Ordinary farmer accounts receive 403 from staff review queues and promotion operations.

The production catalog contains Rice with `rice-leaf-roller` and `rice-water-weevil`. Guidance is predefined, non-chemical, attributed, and includes the required warning that identification alone does not determine pesticide treatment.

## Python AI runtime

The private FastAPI service performs bounded reads, magic/MIME/decode/pixel validation, JPEG sanitation, brightness/blur/candidate checks, model loading, inference, bounding-box normalization, and threshold-based `UNKNOWN`. Crop context is required only for `CROP_PEST`; `GENERAL_INSECT` forbids it and currently returns only image rejection or `UNKNOWN/MODEL_UNAVAILABLE`. It has no user, authorization, guidance, pesticide, field, or agronomy authority. Internal authentication runs in middleware before multipart parsing. The explicit decoder-RGB to Ultralytics-BGR boundary and production startup model warmup are regression-tested so the first user inference stays within Core's timeout.

The locked container uses official CPU-only PyTorch 2.13.0 and does not install CUDA packages. The service is not published to the host network by Compose.

## Dataset and model

Fetched source archives are isolated under `ml/data/fetched`; deterministic prepared splits are under `ml/data/prepared`; experiment runs are under `ml/runs`; promoted runtime assets are under `models`. Large data and weights remain Git-ignored while provenance, checksums, preparation scripts, split manifests, and evaluation reports are tracked.

IP102 supplies the positive detection evidence. BAU-Insectv2 supplies leakage-separated hard negatives and unsupported-insect probes. The weak Asiatic rice borer class was removed after held-out AP50 0.411. The final two-class v1.3 model passed its predeclared high-precision/open-set gates; detailed evidence is in `docs/ai/FINAL_DATASET_SCOPE.md` and `docs/ai/FINAL_MODEL_REPORT.md`.

Expansion v2 separately prepares a leakage-checked five-crop, 12-class IP102 candidate (2,128/531/735 images) but does not claim it was trained or promoted. A small BAU coarse-label `beetle`/`grasshopper`/`mosquito` classifier completed a research run but remains unpromoted because it is agricultural rather than household imagery and lacks adequate OOD/unknown/runtime gates. The opt-in active-learning scripts select, manually review, seal, and materialize versioned candidates; they never promote automatically. See `docs/ai/EXPANSION_V2_SCOPE.md`.

## Infrastructure and dependencies

Compose now contains only PostgreSQL 16, the private AI service, and Core API. Named volumes hold durable PostgreSQL data and private sanitized imagery. Root scripts, `.env.example`, service Dockerfiles, Poetry lock, npm lock, Maven wrapper, health checks, and a six-job CI workflow provide reproducible setup and verification. The final CPU-only AI image is large (about 2.21 GB uncompressed), which is documented as a release-size limitation rather than hidden.

## Security

The baseline architecture contained tenant-isolation, public-service, default-secret, and model-integrity risks. The rebuilt path removed or repaired those attack paths. The post-implementation scan then found and repaired four additional issues: published fallback secrets, an unbounded URI-keyed rate-limit map, login email timing differences, and AI multipart parsing before authentication. No reportable critical/high/medium/low finding remains. Security is still labeled `PARTIAL` because the final scan lacked an independent repeat and online Maven/Python advisory refreshes; see `docs/security/FINAL_SECURITY_REPORT.md`.

## Verification summary

- Contracts: 33 passed.
- Frontend: lint/typecheck PASS; 25 unit/component tests; production build PASS.
- Java: 59 tests, including PostgreSQL 16/Flyway V001–V010, staff authorization, ownership, consent, and promotion-audit cases.
- Python: Ruff/mypy PASS; 22 tests.
- Playwright: 46 deterministic cases passed with 10 intentional skips; all 12 visual baselines passed; the separately enabled real-stack smoke passed.
- Compose: PostgreSQL, Core, and AI are healthy; AI is ready after model warmup. The supplied Rice water-weevil image completed live browser inference at 86%, persisted to history, and entered the explicit consented `PENDING` review path.

## Remaining limitations

- The model is an academic two-class baseline with low runtime coverage, not production agricultural validation.
- Corn, Wheat, Beet, Citrus, the 12-class detector candidate, and the BAU general-insect classifier are not promoted product support.
- The promoted local model binary is ignored by Git and must be provisioned separately in a fresh clone.
- Security coverage remains partial for the tooling reasons documented above.
- The CPU AI image is functional but large and would benefit from a later inference-only export/runtime.
