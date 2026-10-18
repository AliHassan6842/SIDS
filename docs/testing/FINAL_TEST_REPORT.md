# Final Test Report

Date: 2026-08-23  
Environment: Windows, Node 24.18.1/npm 11.16.0, Temurin JDK 21.0.12, Docker Desktop 29.6.2, PostgreSQL 16.15, Python test environment plus Python 3.11 CPU-only container.

## Outcome

The expanded SIDS application passed its executed contract, frontend, Java, Python, model, container, visual-regression, deterministic E2E, and real cross-service smoke gates. The public contract now distinguishes crop-pest and general-insect modes, keeps unavailable crop/model capabilities explicit, and separates opt-in training consent from staff review and model promotion. Security coverage remains marked `PARTIAL` in the dedicated security report because independent variance and online Maven/Python advisory refreshes were unavailable, not because a known reportable vulnerability remains.

## Automated results

| Area | Executed result |
|---|---|
| Shared contracts | `python -m pytest packages/contracts/tests -q`: 33 passed |
| Frontend lint | `npm --prefix apps/web run lint`: PASS |
| Frontend typecheck | `npm --prefix apps/web run typecheck`: PASS |
| Frontend unit/component | `npm --prefix apps/web test -- --run`: 9 files, 25 tests passed |
| Frontend production build | Vite 8.2.2: 53 modules; main bundle 188.72 kB / 62.54 kB gzip |
| Frontend production dependency audit | `npm audit --omit=dev`: 0 vulnerabilities |
| Playwright typecheck | `npm --prefix apps/web run e2e:typecheck`: PASS |
| Playwright deterministic matrix | 46 passed, 10 intentional skips, 0 failed; desktop Chromium and Pixel 5; includes five-crop capability, multi-mode multipart rules, explicit UNKNOWN, consent/review separation, owner isolation, and farmer/reviewer authorization |
| Visual regression | 12 screenshot assertions and 12 inspected PNG baselines; PASS. Five intentional multi-mode UI changes were regenerated and visually inspected before the final no-update run |
| Live browser | Current warm-start stack identified the supplied insect image at 86%; the browser run exposed and verified the AI cold-start warmup repair |
| Real-stack Playwright | 1 passed; register, PostgreSQL-backed crop and full/filtered pest catalogs, authenticated Java multipart, private Python validation, scan persistence, authenticated image retrieval, anonymous image denial, history readback |
| Java | `mvnw.cmd test`: 59 passed, 0 failed/errors/skipped; BUILD SUCCESS |
| Flyway/PostgreSQL | PostgreSQL 16.15 Testcontainers validated and applied V001 through V010, including reviewed-training audit state and nullable coarse-label scientific names; PASS |
| Python | Ruff PASS; mypy PASS; pytest 22 passed; private mode/crop rules and general-mode suppression covered |
| Containers | Core and AI images built; PostgreSQL, AI, and Core all healthy |
| Model readiness | AI `/health` = UP and `/ready` = READY; manifest checksum verified |
| Dataset extraction | Tracked fetch manifest records IP102 and BAU-Insectv2 as `VERIFIED_AND_EXTRACTED`; raw/fetched, prepared, and model artifacts remain separate |
| Catalog/capability truth | Live PostgreSQL exposes `rice`, `corn`, `wheat`, `beet`, and `citrus`; only Rice has identification support. Promoted pests remain exactly the two Rice pests; the promoted general catalog is empty |

The ten deterministic Playwright skips are intentional: eight desktop duplicates of workflow baselines owned by the Pixel 5 project and two gated real-stack cases in the default mocked matrix. The gated real-stack case was then executed separately and passed.

## Model evidence

The promoted Rice-only detector supports `rice-leaf-roller` and `rice-water-weevil`. Frozen test mAP50 is 0.730. The calibration-only threshold is 0.66. Held-out accepted-prediction precision is 1.0 at 20/65 raw-model coverage; BAU unsupported-insect false accepts are 2/45 and COCO8 generic-object false accepts are 0/4. Exact runtime components identify 20/65 known fixtures after portrait-orientation normalization and dimension filtering. These are bounded academic results, not field validation.

## Final demo scenarios

| Scenario | Executed layer | Result |
|---|---|---|
| Good supported pest | Browser/API registration plus Java → private Python → PostgreSQL using held-out `IP000000064.jpg` | `IDENTIFIED`, `rice-leaf-roller`, confidence 0.934623, persisted in history |
| Second supported pest | Real Java → private Python → PostgreSQL using held-out `IP010000031.jpg` | `IDENTIFIED`, `rice-water-weevil`, confidence 0.758491, persisted in history |
| Portrait leaf-roller regression | Real browser → Java → private Python → PostgreSQL using both user-supplied portrait JPEGs | `IDENTIFIED`, `rice-leaf-roller`, confidence 0.886731 and 0.813189; bounding boxes remapped to the original portrait images |
| Small adult water-weevil regression | Real browser → Java → bounded small-subject Python fallback → PostgreSQL using the user-supplied 1200×1200 JPEG | `IDENTIFIED`, `rice-water-weevil`, confidence 0.862072; model v1.1.0/dataset v1.4 persisted with a bounding box on the adult insect |
| Blurry image | Python unit and authenticated HTTP integration tests; Playwright blur state | `REJECTED_IMAGE`, `TOO_BLURRY` |
| Person/random object | Real Java scan using COCO8 `000000000061.jpg`; held-out model suite | `UNKNOWN`, `NO_DETECTION`, null pest, persisted in history; 0/4 COCO8 false accepts |
| Unsupported insect | Real Java scan using BAU sawfly `jpg_19.jpg`; held-out BAU suite | `UNKNOWN`, `NO_DETECTION`, null pest; aggregate BAU false accepts 2/45 |

## Runtime/storage verification

- Compose exposed Core and PostgreSQL on loopback only; Python remained internal on port 8000.
- Flyway history contained successful versions 001–010.
- The supported database pest slugs were exactly `rice-leaf-roller` and `rice-water-weevil`.
- PostgreSQL catalog rows referenced three reviewed static assets: the Rice crop image and one image for each supported pest. Image bytes were not stored in PostgreSQL.
- The in-app browser loaded every catalog asset at its natural dimensions, and a held-out IP102 upload rendered in Result and History through authenticated scan-image retrieval.
- The live scan/prediction tables contained identified rows for both supported pest slugs plus honest `UNKNOWN` and `REJECTED_IMAGE` rows. Primary detections record dataset v1.3; bounded small-subject detections record dataset v1.4.
- Saved sanitized JPEGs were stored in the private named volume under owner-specific directories.
- Owner-authorized image GET returned JPEG; the anonymous request returned HTTP 403.
- The AI container used `torch 2.13.0+cpu`; CUDA availability was false.
- Flyway history contained successful versions 001–010. V009 adds explicit mode, consent events, staff review/audit, and immutable model-promotion records; forward V010 makes scientific names nullable so future coarse general labels are not forced into an invented species.
- Consent/review execution verified that upload defaults to no consent, consent alone does not submit, UNKNOWN scans can be submitted only after opt-in, withdrawal rejects a pending review, ordinary farmers receive 403 for the review queue, and only currently consented approved review IDs can enter an admin promotion record.

## Known limitations

- End-to-end known-pest coverage is deliberately low (20/65) because the threshold and quality gates prefer `UNKNOWN` over an unsafe forced answer.
- The AI image is approximately 2.21 GB uncompressed; it is CPU-only but still includes the Ultralytics scientific Python stack.
- The local promoted `.pt` artifact is intentionally Git-ignored. A fresh clone must provision the checksum-matching artifact described by the runtime manifest.
- The Starlette TestClient deprecation warning is non-failing and does not affect the deployed ASGI runtime.
- The prepared Corn, Wheat, Beet, and Citrus datasets are not trained or promoted product support. The research-only BAU `beetle`, `grasshopper`, and `mosquito` classifier is also unpromoted; general product scans therefore remain `UNKNOWN/MODEL_UNAVAILABLE` or `REJECTED_IMAGE` until separate household/OOD/unknown and promotion gates pass.
