# ADR-014: Use a bounded detector for small subjects

## Status

Accepted — 2026-08-23.

## Context

The primary detector and quality gate were calibrated for controlled close-ups. A reviewed Rice water weevil image contained a sharp insect on a sharp leaf, but the deliberate out-of-focus background dominated global blur and edge metrics. The old ordering returned `TOO_BLURRY` before inference. Lowering the primary confidence threshold was unsafe: at 0.15, BAU false accepts rose to 17/45 and COCO8 false accepts rose to 3/4.

## Decision

Brightness, subject-density, and blur checks are evaluated separately. Low edge density is reported as `SUBJECT_TOO_SMALL`, not `TOO_BLURRY`.

The v1.0 detector remains the default for ordinary valid images. Only an image whose quality result is `SUBJECT_TOO_SMALL` may be passed to the checksum-verified v1.1 fallback. The fallback uses a 480-pixel full view plus a centered 80-percent view and requires confidence 0.75. If it is uncertain, the result remains `REJECTED_IMAGE / SUBJECT_TOO_SMALL`; no class is forced.

The Java service remains the domain and persistence authority. The Python service returns only structured detection evidence with the actual model and dataset versions used.

## Consequences

- Existing close-up behavior and the v1.0 calibration remain unchanged.
- Small centered pests can be recovered without weakening the general rejection boundary.
- The fallback adds CPU latency only on the small-subject path.
- A user-supplied image can be a regression probe but cannot enter training without provenance, licensing, a dataset version, and leakage review.
- Promotion evidence is recorded in `ml/reports/sids-rice-pest-detection-v1.4-small-subject-evaluation.json`.
