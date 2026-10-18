# ADR-015: Separate identification modes and use reviewed active learning

## Status

Accepted — 2026-08-23.

## Context

SIDS began with one promoted Rice detector covering Rice leaf roller and Rice water weevil. The product now needs a visible path toward five common crops and general-insect identification, while preserving honest capability claims and preventing user uploads from silently changing a production model.

BAU and IP102 are research sources, not live database-backed inference engines. A successful experiment is insufficient for promotion when its scene coverage, out-of-distribution behavior, licensing, or runtime contract has not been verified.

## Decision

The public scan contract has two explicit modes:

- `CROP_PEST` requires a promoted crop identifier.
- `GENERAL_INSECT` forbids a crop identifier.

Catalog rows may describe planned crop coverage independently from inference capability through `identificationSupported`. Rice remains enabled; Corn, Wheat, Beet, and Citrus are visible data candidates until their detectors pass the declared evaluation and runtime gates.

The Python service accepts the same mode boundary. Until a general-insect model is promoted, it performs bounded image validation and returns only `UNKNOWN / MODEL_UNAVAILABLE` or an image rejection. It must not route general images through the Rice detector or expose research-only BAU labels.

Model improvement uses reviewed active learning rather than continuous online training. Upload use is opt-in. Consent and review submission are separate events; reviewers or administrators must approve labels. Retraining material is sealed as a versioned, provenance-bearing candidate dataset and can reach production only through evaluation, integrity checks, and an auditable promotion record. Ordinary users cannot access the review queue, decisions, or promotion endpoints.

Java remains the authority for catalog truth, consent, review authorization, general-insect safety guidance, and promotion records. Python returns bounded model evidence only. Research code and downloaded data remain under `ml` and never mutate the business database.

## Consequences

- The UI can show the five-crop roadmap without implying all five are scannable.
- Existing clients remain compatible because missing `mode` defaults to `CROP_PEST` on private calls.
- General-insect uploads can enter a consented review workflow before a general classifier is promoted, but users receive no unverified label.
- Model updates are not immediate or automatic; the review and promotion gates deliberately trade speed for provenance, rollback, and user safety.
- New crop or general-insect models require contract, OOD, runtime, and end-to-end evidence before their capability flags or catalogs are enabled.
