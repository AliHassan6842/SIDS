# SIDS shared contracts

This package is the canonical versioned interface boundary for the insect-identification product.

- `json-schema`: draft 2020-12 request, response, and persisted-result schemas.
- `examples`: validated, non-secret examples tied to the v1 schemas.
- `http`: exact public and private HTTP boundary notes, including multipart field names.
- `errors`: stable error semantics.
- `tests`: schema and implementation-compatibility checks.

The public browser calls only the Java Core API. Python implements only private `/internal/v1` endpoints. An OpenAPI document is deliberately not claimed yet; these schemas cover only interfaces verified against the current implementations.

## Contract revisions

- The top-level schemas are the implemented Rice-only v1 compatibility contract.
- `json-schema/v2` and `examples/v2` define the additive multi-mode contract. New producers must emit the required v2 mode, capability, consent, and review fields. Old clients may continue omitting the new multipart fields while Java applies the documented defaults.
- The API path remains `/api/v1`; the contract revision identifies the serialized shape, not a second HTTP API.

The v2 crop catalog contains the stable slugs `rice`, `corn`, `wheat`, `beet`, and `citrus`. Only `rice` currently has `identificationSupported: true`. The only promoted pest slugs remain `rice-leaf-roller` and `rice-water-weevil`. Candidate crop pests and the research-only BAU coarse labels are not public catalog entries until their data, evaluation, review, and model-promotion gates pass.

## Multi-mode and review authority

- `CROP_PEST` requires an authoritative public crop UUID. `GENERAL_INSECT` forbids a crop.
- Catalog `kind` uses the same two values. General-insect entries have no affected crops and never carry crop guidance.
- `generalGuidance`, when a reviewed general catalog entry eventually exists, is attributable Java-owned safety/removal guidance. Python never supplies harmfulness, removal, agronomy, authorization, consent, or review decisions.
- `trainingConsent` is explicit, current, and revocable. It is not implied by upload and does not itself submit a scan for review.
- `reviewStatus` is Java-owned and records `NOT_SUBMITTED`, `PENDING`, `APPROVED`, or `REJECTED`. A user-proposed label is annotation input, not an identification result or approval.
- With no promoted general model/catalog today, general scans must remain explicit `UNKNOWN` results and must not reveal the nearest research label.

## Identifier semantics

- Public `crop.id`, `pest.id`, `cropId`, `pestId`, and `scanId` values are UUIDs.
- Public `crop.slug` and `pest.slug` values are stable human-readable catalog slugs.
- Java translates the selected public crop UUID to the crop slug sent as private multipart field `crop_id`.
- Python's private response field `prediction.pestId` contains an allowlisted pest **slug**, despite the historical field name. Java resolves that slug to the authoritative public pest UUID.

Contracts intentionally exclude disease diagnosis, field incidence, severity, pesticide decisions, arbitrary image URLs, arbitrary model names, and Python-owned guidance or authorization.

Bounding boxes use normalized top-left `x`, `y`, `width`, and `height` values in `[0,1]`. In addition to the JSON Schema ranges, producers must ensure `x + width <= 1` and `y + height <= 1`; JSON Schema cannot express these arithmetic cross-field invariants directly.
