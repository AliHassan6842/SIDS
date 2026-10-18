# ADR-012: Separate fetched, prepared, experiment, and promoted AI assets

## Status

Accepted on 2026-08-22.

## Context

The repository contained disease datasets, placeholder pest manifests, unverifiable counts, and generic COCO smoke artifacts. Raw downloads must not be confused with prepared training data or a production model.

## Decision

- `ml/data/fetched` contains ignored immutable downloads/extracts and a tracked provenance/checksum manifest.
- `ml/data/prepared` contains ignored validated/deduplicated deterministic subsets and splits.
- `ml/runs` contains ignored experiment outputs.
- `models` contains only deliberately promoted runtime artifacts and strict manifests.
- `docs/ai` records measured scope and evaluation evidence.

IP102 is the primary dataset. BAU-Insectv2 may be used once as supplementary classification or unsupported-input evidence only when its coarse taxonomy is not misrepresented as a species label.

## Consequences

- Downloaded data is reproducible without committing large archives.
- No class becomes user-visible from a manifest claim alone.
- Production startup fails closed when artifact integrity or approved metadata is missing.
