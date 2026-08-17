# ADR-005: Limit Python to AI computation

- Status: Accepted
- Date: 2026-08-16

## Context

Production inference requires specialized Python libraries but must not become a second business authority.

## Decision

Python validates inputs, runs approved models, and returns structured results with versions and uncertainty. It does not authorize users or prescribe agronomic action.

## Consequences

The AI service can evolve independently while business rules remain centralized and auditable in Java.
