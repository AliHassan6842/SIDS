# ADR-008: Separate ML research from production AI

- Status: Accepted
- Date: 2026-08-16

## Context

Exploration, training, and datasets have different dependencies and controls from reliable inference serving.

## Decision

Keep research in `ml` and production inference in `services/ai-service`. Only approved, evaluated exports cross the boundary.

## Consequences

Notebooks and training dependencies do not define production architecture. Promotion requires reproducible metadata and evaluation gates.
