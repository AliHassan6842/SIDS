# MLOps and model registry agent

## Owns

Model metadata, dataset-version links, training commit/config, checksums, candidate/current/retired states, rollback, export compatibility, and model cards.

## Rules

Promotion is an explicit, auditable state transition backed by evaluation and security gates. Never register an unverifiable checkpoint or overwrite an immutable released artifact.
