# Final simplified architecture

SIDS implements one bounded workflow: an authenticated farmer selects a supported crop, captures one controlled close-up image, and receives an identified supported pest, an explicit unknown result, or an image rejection. Java, not the browser or AI service, owns authorization, crop/pest allowlists, guidance, persistence, and image access.

```text
Farmer
  |
  v
React/Vite web app
  |  public HTTPS /api/v1, bearer JWT
  v
Java Core API
  |-- PostgreSQL: users, supported catalog, attributed guidance, scans
  |-- private image storage: sanitized JPEGs, owner-authorized retrieval
  `-- private authenticated multipart request
        v
      Python AI service
        |-- bounded decode and re-encode
        |-- frame-quality validation
        |-- checksum-verified two-class Rice detector
        `-- IDENTIFIED / UNKNOWN / REJECTED_IMAGE
```

## Request flow

1. The browser calls Java only. `/login` and `/register` are public; product routes and scan/catalog APIs require a valid Java-issued JWT.
2. The farmer selects a crop UUID published by Java. Java translates it to the stable crop slug expected by the private model manifest.
3. Live validation sends one resized latest frame approximately every 800 ms. Intermediate frames are dropped and stale requests are aborted.
4. Final capture sends the full image to Java. Java enforces byte and pixel limits, verifies image magic and decode, removes metadata by JPEG re-encoding, and stores a private copy.
5. Java calls Python with a service token, crop slug, request ID, and an `image/jpeg` multipart part. Python repeats bounded decode and quality checks before inference.
6. Java validates every AI status, reason, confidence, bounding box, pest slug, and model identifier. A predicted slug outside the selected crop allowlist becomes `UNKNOWN`.
7. Java looks up predefined attributed non-chemical guidance, persists the scan, and returns the owner-authorized result. Python never generates guidance.

## Supported production scope

- Crop: Rice.
- Pest identifiers: `rice-leaf-roller` and `rice-water-weevil`.
- `asiatic-rice-borer` remains in historical dataset evidence but is disabled in the production catalog because its held-out result did not justify promotion.
- Dataset and model promotion are versioned independently. The authoritative class/count decision is in `docs/ai/FINAL_DATASET_SCOPE.md`; measured model evidence is in `docs/ai/FINAL_MODEL_REPORT.md`.

## Removed production paths

Disease diagnosis, PlantVillage/Paddy Doctor, severity segmentation, whole-field incidence, pesticide/dosage/threshold decisions, weather, RAG/pgvector, Valkey AI queues, task/reminder workflows, public object storage, and direct browser-to-Python calls are outside the final product. Historical sources are isolated under `archive/` and are not on production import paths.

## Deployment boundary

Compose exposes only PostgreSQL and Java on loopback development ports. Python is reachable only on the internal Compose network. Images use a private persistent local volume in the FYP deployment; replacing that adapter with private S3-compatible storage is a future production-hardening option, not a change to domain ownership.

Architecture decisions are recorded in ADR-010 through ADR-012 under `docs/decisions/`.
