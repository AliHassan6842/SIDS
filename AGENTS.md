# SIDS repository instructions

## Project

SIDS is the Smart Insect Detection System / AI Digital Crop Scout, an offline-first agricultural platform for farmers.

## Architectural authority

- `apps/web`: existing frontend; protected unless a user explicitly authorizes frontend changes.
- `services/core-api`: Java owns domain truth, authorization, risk, field state, thresholds, recommendations, treatment policy, and farm ownership.
- `services/ai-service`: Python performs bounded AI computation and returns structured evidence; it is not a business or agronomy authority.
- `ml`: research, datasets, training, experiments, evaluation, and model export only.
- `knowledge`: allowlisted, attributable agronomy evidence and retrieval assets.
- PostgreSQL: durable business truth and future vector/full-text retrieval.
- Valkey: transient cache, throttling, idempotency, locks, and work transport; never permanent business storage.
- Object storage: original, sanitized, annotated, and derived imagery.
- Hardware: an optional future adapter, not a core dependency.

## Working rules

- Inspect the repository and the nearest `AGENTS.md` before editing.
- Do not modify `apps/web` without explicit frontend authorization.
- Avoid cross-boundary coupling and duplicate schemas; shared interfaces belong in `packages/contracts`.
- Prefer feature-specific modules. Do not create giant `utils`, `common`, or `misc` dumping grounds.
- Keep secrets out of source control and use namespaced environment configuration.
- Never hard-code pesticides, dosages, crop thresholds, or invented field percentages.
- Never infer whole-field incidence from one image.
- Never place business authorization or agronomic policy in Python AI code or the UI.
- Run relevant, non-mutating validation after changes and report failures without hiding them.
- Record consequential architecture choices as ADRs under `docs/decisions`.
