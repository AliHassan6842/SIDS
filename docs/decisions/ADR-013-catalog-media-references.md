# ADR-013: Catalog media references remain separate from research data

## Status

Accepted — 2026-08-23.

## Decision

PostgreSQL stores only reviewed relative `image_url` references for supported crops and pests. The web build serves the referenced catalog assets. Full image bytes are not stored in PostgreSQL.

The three local catalog assets are copied from source-native IP102 samples already covered by the academic-use dataset manifest. Their exact prepared-source paths and SHA-256 hashes are recorded in `apps/web/public/catalog/PROVENANCE.json`.

BAU remains unsupported-insect rejection evidence and is never mapped into the supported catalog. Fetched archives, extraction trees, prepared datasets, training runs, model artifacts, catalog media, and user scan storage remain separate concerns.

## Consequences

- Catalog APIs remain authoritative for which reviewed image reference belongs to each supported crop or pest.
- The browser can render catalog images without receiving research dataset paths.
- Production packaging must include `apps/web/public/catalog`.
- Any replacement asset requires a provenance and checksum update plus visual regression review.
