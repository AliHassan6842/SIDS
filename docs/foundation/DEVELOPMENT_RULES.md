# Development rules

1. Read the root and nearest scoped `AGENTS.md` before editing.
2. Keep changes within the requested owner boundary and inspect existing work first.
3. Treat Java as business/domain authority and Python as an AI computation service.
4. Keep research/training assets out of the production inference runtime.
5. Define shared interfaces once in `packages/contracts`; use versioned generation later instead of hand-maintained copies.
6. Commit no secrets, raw datasets, large imagery, or trained weights by default.
7. Record dataset provenance, license, checksum, reproducible split, and evaluation evidence.
8. Do not invent pesticides, dosage, thresholds, or whole-field estimates.
9. Prefer focused feature modules and explicit adapters over global utilities.
10. Validate changed configuration and relevant code without format-on-write or unrelated fixes.
11. Record consequential architecture changes as ADRs.
